# Use official Node.js runtime as a base image
FROM node:16-alpine

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json first for efficient caching
COPY package.json package-lock.json /app/

# Install dependencies
RUN npm install

# Copy the rest of the frontend source code
COPY ./src/frontend/ /app/

# Build the React app for production
RUN npm run build

# Use a lightweight web server to serve the app
FROM nginx:alpine

# Copy the build output into Nginx's default public directory
COPY --from=0 /app/build /usr/share/nginx/html

# Expose port 80 for the web server
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
