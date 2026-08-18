FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends cron \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies from the repo root requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY src/backend/src /app

# Install crontab for the scheduler service
COPY src/backend/crontab /etc/cron.d/cinema-scrape
RUN chmod 0644 /etc/cron.d/cinema-scrape \
    && crontab /etc/cron.d/cinema-scrape \
    && touch /var/log/scrape.log /var/log/cleanup.log

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
