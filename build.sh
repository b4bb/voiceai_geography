#!/bin/bash

# Build script for Render deployment
echo "Starting build process..."

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm install

# Build the frontend
echo "Building frontend..."
npm run build

# Check if build was successful
if [ -f "dist/index.html" ]; then
    echo "✅ Frontend build successful!"
    echo "Files in dist/:"
    ls -la dist/
    echo "Files in dist/static/:"
    ls -la dist/static/
else
    echo "❌ Frontend build failed - dist/index.html not found"
    exit 1
fi

echo "Build process completed successfully!"
