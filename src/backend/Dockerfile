# Use official Python runtime as a base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /src

# Copy the backend code into the container
COPY ./src /src

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port FastAPI will run on
EXPOSE 8000

# Set environment variable for FastAPI
ENV UVICORN_CMD="uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload"

# Command to run FastAPI app
CMD ["sh", "-c", "$UVICORN_CMD"]