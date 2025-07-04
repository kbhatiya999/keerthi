#!/bin/bash

echo "Cloudinary Account Monitor"
echo "=========================="

# Hardcoded Cloudinary credentials - UPDATE THESE WITH YOUR ACTUAL VALUES
CLOUDINARY_CLOUD_NAME="dlhv5towy"
CLOUDINARY_API_KEY="785245949597287"
CLOUDINARY_API_SECRET="BX5z56TipOMFmpMoDyI2RwVIPLA"

echo "✅ Using hardcoded credentials"
echo "Cloud Name: $CLOUDINARY_CLOUD_NAME"
echo "API Key: ${CLOUDINARY_API_KEY:0:8}..."

# Run the CLI test script
echo ""
echo "Running Cloudinary tests..."
cd ../cloudinary
./test-cli.sh

echo ""
echo "Monitor complete!" 