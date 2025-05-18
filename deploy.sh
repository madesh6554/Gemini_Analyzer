#!/bin/bash

# Exit on error
set -e

echo "Starting deployment process..."

echo "1. Building Docker image..."
docker build -t gemini-analyzer .

echo "2. Creating necessary directories..."
mkdir -p uploads logs

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Error: .env file not found. Please create it with your API key."
    exit 1
fi

echo "3. Starting Docker containers..."
docker-compose up -d

echo "4. Waiting for application to start..."
sleep 5

echo "5. Checking application health..."
if curl -f http://localhost:5000; then
    echo "Deployment successful!"
    echo "Application is running at http://localhost:5000"
else
    echo "Error: Application failed to start."
    docker-compose logs
    exit 1
fi

echo "Deployment complete!"
