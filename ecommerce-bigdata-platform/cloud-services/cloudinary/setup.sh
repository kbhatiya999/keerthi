#!/bin/bash

# =============================================================================
# Cloudinary Setup
# =============================================================================

# Load environment variables from cloud-services .env
if [ -f "../.env" ]; then
    export $(cat ../.env | grep -v '^#' | xargs)
    echo "✅ Loaded environment variables from cloud-services/.env"
else
    echo "⚠️  No .env file found in cloud-services directory"
    echo "   Please create cloud-services/.env with your Cloudinary credentials"
fi

echo "Setting up Cloudinary..."

# Install Cloudinary Python SDK
pip install cloudinary

# Install Cloudinary CLI globally
npm install -g cloudinary-cli

# Use environment variables from .env
if [ -z "$CLOUDINARY_CLOUD_NAME" ] || [ -z "$CLOUDINARY_API_KEY" ] || [ -z "$CLOUDINARY_API_SECRET" ]; then
    echo "⚠️  Cloudinary credentials not set in cloud-services/.env"
    echo "   Please add CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, and CLOUDINARY_API_SECRET to cloud-services/.env"
else
    echo "✅ Using Cloudinary Cloud Name: $CLOUDINARY_CLOUD_NAME"
fi

echo "Cloudinary setup complete!"
echo ""
echo "Please update the hardcoded values in the test scripts:"
echo "1. Go to https://cloudinary.com/console"
echo "2. Copy your Cloud Name, API Key, and API Secret"
echo "3. Update test-cloudinary.py and test-cli.sh with your actual values"
echo ""
echo "CLI Usage:"
echo "  npx cloudinary-cli --help"
echo "  npx cloudinary-cli config"
echo "  npx cloudinary-cli upload <file>" 