#!/bin/bash

# Exit on error
set -e

echo "🚀 Starting test environment setup..."

# Build and start the containers
echo "📦 Building and starting Docker containers..."
docker-compose -f docker-compose.dev.yml build
docker-compose -f docker-compose.dev.yml up -d db redis

# Wait for MySQL to be ready
echo "⏳ Waiting for MySQL to be ready..."
sleep 10

# Run migrations
echo "🔄 Running database migrations..."
docker-compose -f docker-compose.dev.yml run --rm web python manage.py migrate

# Run the tests with coverage
echo "🧪 Running tests with coverage..."
docker-compose -f docker-compose.dev.yml run --rm test coverage run manage.py test nadooit.tests nadooit_auth.tests --settings=nadooit.tests.test_settings -v 2

# Generate coverage report
echo "📊 Generating coverage report..."
docker-compose -f docker-compose.dev.yml run --rm test coverage report

# Clean up
echo "🧹 Cleaning up..."
docker-compose -f docker-compose.dev.yml down

echo "✅ Test suite execution completed!"
