# Deploying cinema-app to AWS Lightsail (Terraform + GitHub Actions)

This is a build guide, not applied infrastructure — none of the commands below
have been run and no AWS resources exist yet. Follow it top to bottom when you're
ready to deploy.

## Decisions this guide assumes

- **Deploy mechanism**: GitHub Actions builds Docker images and pushes them to
  ECR; the Lightsail instance only pulls + restarts. Building Next.js directly on
  a small Lightsail box risks OOM and is slow — building in CI is more robust.
- **Domain/TLS**: none yet — access via the Lightsail static IP over plain HTTP.
  Add a reverse proxy (Caddy) later once you have a domain; see "Adding a domain
  later" at the bottom.
- **Instance size**: 2 GB RAM / 1 vCPU (~$10/mo) — comfortable for postgres +
  backend + scheduler + frontend running concurrently.
- **Deploy trigger**: every push to `main`.

## Architecture

```
GitHub push to main
  -> GitHub Actions:
      - build cinema-backend image (used by both backend & scheduler services)
      - build cinema-frontend image (NEXT_PUBLIC_API_URL baked in at build time
        via --build-arg, since Next.js inlines NEXT_PUBLIC_* vars at build)
      - push both to ECR, tag :latest and :<sha>
      - rsync docker-compose.prod.yml to the Lightsail instance over SSH
      - ssh in: docker compose pull && docker compose up -d --remove-orphans

Terraform provisions (applied manually by you, infrequently):
  - Lightsail instance (Ubuntu 22.04), user_data installs docker + compose plugin
  - Lightsail static IP, attached to the instance
  - Lightsail firewall: 22 (SSH), 80 (frontend), 8000 (backend API)
  - Lightsail SSH key pair (Terraform-generated; private key output as a secret)
  - 2 ECR repos: cinema-backend, cinema-frontend (+ lifecycle policy to expire
    untagged images after 7 days)
  - 1 IAM user scoped to ECR push/pull on just those 2 repos, with an access key
    -- used both by GitHub Actions (push) and by the instance itself (pull)
```

Postgres data persists via a named Docker volume on the instance's disk — no
managed DB, consistent with the current local setup. The backend already runs
`init_db()` (`Base.metadata.create_all`) on startup via its FastAPI lifespan
handler ([api/main.py](src/backend/src/api/main.py)), so first deploy needs no
manual migration step.

---

## Part 1 — App changes (needed regardless of cloud provider)

These make the app container-deployable at all — the frontend currently has no
Dockerfile and only runs via `npm run dev`.

### 1a. Frontend Dockerfile

Create `src/frontend/cinema/Dockerfile`:

```dockerfile
# --- deps ---
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# --- build ---
FROM node:20-alpine AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
RUN npm run build

# --- run ---
FROM node:20-alpine AS run
WORKDIR /app
ENV NODE_ENV=production
COPY --from=build /app/public ./public
COPY --from=build /app/.next/standalone ./
COPY --from=build /app/.next/static ./.next/static
EXPOSE 3000
CMD ["node", "server.js"]
```

The `ARG`/`ENV` pair matters: Next.js inlines `NEXT_PUBLIC_*` vars into the
client JS bundle **at build time**, not at container start. If you forget the
`--build-arg` when building the image, the deployed frontend will silently try
to call `localhost:8000` from the browser.

### 1b. Enable standalone output

In `src/frontend/cinema/next.config.ts`, add `output: "standalone"`:

```ts
const nextConfig: NextConfig = {
  output: "standalone",
};
```

This is what makes `.next/standalone` (referenced in the Dockerfile above) exist
— it produces a minimal server bundle instead of requiring the full
`node_modules` tree in the runtime image.

### 1c. Production compose file

Create `docker-compose.prod.yml` at the repo root. Unlike the local
`docker-compose.yml`, this pulls pre-built images from ECR instead of building
on the box, and adds the frontend service:

```yaml
services:
  postgres:
    image: postgres:16
    restart: unless-stopped
    volumes:
      - postgres_data:/var/lib/postgresql/data
    env_file:
      - .env
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s

  backend:
    image: ${ECR_REGISTRY}/cinema-backend:${IMAGE_TAG:-latest}
    restart: unless-stopped
    ports:
      - "8000:8000"
    env_file:
      - .env
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
    depends_on:
      postgres:
        condition: service_healthy

  scheduler:
    image: ${ECR_REGISTRY}/cinema-backend:${IMAGE_TAG:-latest}
    restart: unless-stopped
    env_file:
      - .env
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      TZ: Europe/Dublin
    depends_on:
      postgres:
        condition: service_healthy
    command: ["cron", "-f"]

  frontend:
    image: ${ECR_REGISTRY}/cinema-frontend:${IMAGE_TAG:-latest}
    restart: unless-stopped
    ports:
      - "80:3000"
    depends_on:
      - backend

volumes:
  postgres_data:
```

Note `backend` and `scheduler` share the **same** `cinema-backend` image, same
as today's `docker-compose.yml` — only the `command` differs.

### 1d. Fix CORS for the deployed origin

[api/main.py](src/backend/src/api/main.py) currently hardcodes CORS to
`localhost:3000`/`127.0.0.1:3000` only:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    ...
)
```

Once deployed, the frontend's origin will be `http://<static-ip>`, which this
would silently reject (the browser blocks the API calls, listings just never
load). Change it to read from an env var:

```python
import os

cors_origins = os.environ.get(
    "CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    ...
)
```

Add to `.env.example`:

```
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

On the server, you'll set this to `http://<static-ip>` (see Part 4).

---

## Part 2 — Terraform

Create a `terraform/` directory at the repo root with the files below.
Terraform state is kept **local** for this setup (simplest for a solo project) —
move to an S3 backend later if you want remote/shared state.

### terraform/providers.tf

```hcl
terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}
```

### terraform/variables.tf

```hcl
variable "aws_region" {
  default = "eu-west-1" # Ireland
}

variable "project_name" {
  default = "cinema-app"
}

variable "availability_zone" {
  default = "eu-west-1a"
}

variable "bundle_id" {
  description = "Lightsail bundle (instance size). Run `aws lightsail get-bundles` to confirm the current ~2GB/1vCPU id — AWS renames these periodically (e.g. small_3_0)."
  default     = "small_3_0"
}
```

Before applying, run `aws lightsail get-bundles --query "bundles[?ramSizeInGb==\`2\`]"`
yourself and confirm `bundle_id` matches a real, current ~$10/mo bundle.

### terraform/lightsail.tf

```hcl
resource "aws_lightsail_key_pair" "this" {
  name = "${var.project_name}-key"
}

resource "aws_lightsail_instance" "this" {
  name              = var.project_name
  availability_zone = var.availability_zone
  blueprint_id      = "ubuntu_22_04"
  bundle_id         = var.bundle_id
  key_pair_name     = aws_lightsail_key_pair.this.name

  user_data = templatefile("${path.module}/user_data.sh.tpl", {
    aws_region        = var.aws_region
    ecr_registry      = "${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.aws_region}.amazonaws.com"
    iam_access_key_id = aws_iam_access_key.ci.id
    iam_secret_key    = aws_iam_access_key.ci.secret
  })
}

resource "aws_lightsail_static_ip" "this" {
  name = "${var.project_name}-ip"
}

resource "aws_lightsail_static_ip_attachment" "this" {
  static_ip_name = aws_lightsail_static_ip.this.name
  instance_name  = aws_lightsail_instance.this.name
}

resource "aws_lightsail_instance_public_ports" "this" {
  instance_name = aws_lightsail_instance.this.name

  port_info {
    protocol  = "tcp"
    from_port = 22
    to_port   = 22
  }
  port_info {
    protocol  = "tcp"
    from_port = 80
    to_port   = 80
  }
  port_info {
    protocol  = "tcp"
    from_port = 8000
    to_port   = 8000
  }
}

data "aws_caller_identity" "current" {}
```

### terraform/ecr.tf

```hcl
resource "aws_ecr_repository" "backend" {
  name                 = "${var.project_name}-backend"
  image_tag_mutability = "MUTABLE"
}

resource "aws_ecr_repository" "frontend" {
  name                 = "${var.project_name}-frontend"
  image_tag_mutability = "MUTABLE"
}

locals {
  ecr_lifecycle_policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "Expire untagged images after 7 days"
      selection = {
        tagStatus   = "untagged"
        countType   = "sinceImagePushed"
        countUnit   = "days"
        countNumber = 7
      }
      action = { type = "expire" }
    }]
  })
}

resource "aws_ecr_lifecycle_policy" "backend" {
  repository = aws_ecr_repository.backend.name
  policy     = local.ecr_lifecycle_policy
}

resource "aws_ecr_lifecycle_policy" "frontend" {
  repository = aws_ecr_repository.frontend.name
  policy     = local.ecr_lifecycle_policy
}
```

### terraform/iam.tf

One IAM user, used both by GitHub Actions (to push images) and by the instance
itself (to pull them) — keeps this simple for a solo project.

```hcl
resource "aws_iam_user" "ci" {
  name = "${var.project_name}-ecr"
}

resource "aws_iam_access_key" "ci" {
  user = aws_iam_user.ci.name
}

resource "aws_iam_user_policy" "ci_ecr" {
  name = "${var.project_name}-ecr-push-pull"
  user = aws_iam_user.ci.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "ecr:GetAuthorizationToken"
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:PutImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload",
        ]
        Resource = [
          aws_ecr_repository.backend.arn,
          aws_ecr_repository.frontend.arn,
        ]
      },
    ]
  })
}
```

### terraform/user_data.sh.tpl

Cloud-init script that runs once on first boot to prepare the instance:

```bash
#!/bin/bash
set -euxo pipefail

apt-get update
apt-get install -y ca-certificates curl gnupg unzip

# Docker + compose plugin
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" \
  > /etc/apt/sources.list.d/docker.list
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
usermod -aG docker ubuntu

# AWS CLI v2
curl -s "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o /tmp/awscliv2.zip
unzip -q /tmp/awscliv2.zip -d /tmp
/tmp/aws/install

# Credentials so the instance can `docker login`/pull from ECR itself
mkdir -p /home/ubuntu/.aws
cat > /home/ubuntu/.aws/credentials <<EOF
[default]
aws_access_key_id = ${iam_access_key_id}
aws_secret_access_key = ${iam_secret_key}
EOF
cat > /home/ubuntu/.aws/config <<EOF
[default]
region = ${aws_region}
EOF
chown -R ubuntu:ubuntu /home/ubuntu/.aws
chmod 600 /home/ubuntu/.aws/credentials

mkdir -p /opt/cinema-app
chown ubuntu:ubuntu /opt/cinema-app
```

### terraform/outputs.tf

```hcl
output "static_ip" {
  value = aws_lightsail_static_ip.this.ip_address
}

output "ssh_private_key" {
  value     = aws_lightsail_key_pair.this.private_key
  sensitive = true
}

output "ecr_backend_url" {
  value = aws_ecr_repository.backend.repository_url
}

output "ecr_frontend_url" {
  value = aws_ecr_repository.frontend.repository_url
}

output "ci_iam_access_key_id" {
  value     = aws_iam_access_key.ci.id
  sensitive = true
}

output "ci_iam_secret_access_key" {
  value     = aws_iam_access_key.ci.secret
  sensitive = true
}
```

### terraform/.gitignore

```
*.tfstate
*.tfstate.*
.terraform/
.terraform.lock.hcl
*.tfvars
!terraform.tfvars.example
```

---

## Part 3 — GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy

on:
  push:
    branches: [main]

env:
  AWS_REGION: eu-west-1

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - id: ecr-login
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build and push backend image
        env:
          REGISTRY: ${{ steps.ecr-login.outputs.registry }}
        run: |
          docker build -f src/backend/Dockerfile -t $REGISTRY/cinema-app-backend:${{ github.sha }} -t $REGISTRY/cinema-app-backend:latest .
          docker push $REGISTRY/cinema-app-backend:${{ github.sha }}
          docker push $REGISTRY/cinema-app-backend:latest

      - name: Build and push frontend image
        env:
          REGISTRY: ${{ steps.ecr-login.outputs.registry }}
        run: |
          docker build \
            --build-arg NEXT_PUBLIC_API_URL=${{ vars.NEXT_PUBLIC_API_URL }} \
            -t $REGISTRY/cinema-app-frontend:${{ github.sha }} \
            -t $REGISTRY/cinema-app-frontend:latest \
            src/frontend/cinema
          docker push $REGISTRY/cinema-app-frontend:${{ github.sha }}
          docker push $REGISTRY/cinema-app-frontend:latest

      - name: Copy compose file to instance
        uses: appleboy/scp-action@v0.1.7
        with:
          host: ${{ secrets.LIGHTSAIL_HOST }}
          username: ubuntu
          key: ${{ secrets.LIGHTSAIL_SSH_KEY }}
          source: "docker-compose.prod.yml"
          target: "/opt/cinema-app"

      - name: Deploy on instance
        uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.LIGHTSAIL_HOST }}
          username: ubuntu
          key: ${{ secrets.LIGHTSAIL_SSH_KEY }}
          envs: ECR_REGISTRY,IMAGE_TAG
          script: |
            cd /opt/cinema-app
            export ECR_REGISTRY=${{ steps.ecr-login.outputs.registry }}
            export IMAGE_TAG=${{ github.sha }}
            docker compose -f docker-compose.prod.yml pull
            docker compose -f docker-compose.prod.yml up -d --remove-orphans
            docker image prune -f
```

App-level secrets (DB password, `RESEND_API_KEY`/SMTP creds) are **not** part of
this workflow — they live only in `/opt/cinema-app/.env` on the instance,
written once by hand (Part 4). CI only needs AWS + SSH access.

---

## Part 4 — One-time rollout steps

1. `cd terraform && terraform init`
2. `terraform plan` — review exactly what will be created
3. `terraform apply` — creates the instance (~$10/mo), static IP, ECR repos, IAM user
4. `terraform output` to grab: `static_ip`, `ssh_private_key` (sensitive — save to
   a file, `chmod 600`), both ECR repo URLs, `ci_iam_access_key_id` /
   `ci_iam_secret_access_key`
5. SSH into the instance once (`ssh -i <key-file> ubuntu@<static_ip>`), create
   `/opt/cinema-app/.env` by hand based on `.env.example`, including:
   ```
   POSTGRES_USER=...
   POSTGRES_PASSWORD=<real password>
   POSTGRES_DB=cinema
   PUBLIC_API_URL=http://<static_ip>:8000
   CORS_ORIGINS=http://<static_ip>
   EMAIL_FROM=...
   RESEND_API_KEY=...   # or SMTP_* vars
   ```
6. In the GitHub repo settings, add:
   - **Secrets**: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` (the
     `ci_iam_access_key_id`/`ci_iam_secret_access_key` outputs), `LIGHTSAIL_HOST`
     (`static_ip`), `LIGHTSAIL_SSH_KEY` (`ssh_private_key`)
   - **Variable**: `NEXT_PUBLIC_API_URL` = `http://<static_ip>:8000`
7. Push to `main` (or trigger the workflow manually) and watch GitHub Actions
   build, push to ECR, and deploy
8. Verify: `curl http://<static_ip>:8000/health` and open `http://<static_ip>`
   in a browser

## Verification checklist

- After `terraform apply`: SSH in, confirm cloud-init finished
  (`cloud-init status --wait`) and `docker --version` / `docker compose version` work
- After the first GitHub Actions run: green workflow run, then on the instance
  `docker compose -f /opt/cinema-app/docker-compose.prod.yml ps` shows 4 healthy
  containers (postgres, backend, scheduler, frontend)
- Load `http://<static_ip>` in a browser and confirm listings actually render —
  this proves CORS + `NEXT_PUBLIC_API_URL` wiring is correct end-to-end, not just
  that containers started
- Push a trivial follow-up commit to `main` and confirm it redeploys automatically

## Costs

| Item | Cost |
|---|---|
| Lightsail instance (2GB/1vCPU) | ~$10/mo |
| ECR storage | pennies at this scale |
| Everything else (TLS n/a yet, email at free-tier Resend volume) | $0 |

## Adding a domain later

Once you have a domain, add a `caddy` service to `docker-compose.prod.yml`
listening on 80/443 in front of `frontend`, point the domain's A record at the
static IP, and open port 443 in `aws_lightsail_instance_public_ports`. Caddy
handles Let's Encrypt automatically with a ~5-line Caddyfile — no changes needed
to the backend/frontend services themselves beyond updating `PUBLIC_API_URL`,
`CORS_ORIGINS`, and `NEXT_PUBLIC_API_URL` to the new domain.
