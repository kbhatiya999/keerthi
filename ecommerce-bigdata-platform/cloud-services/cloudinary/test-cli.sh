#!/bin/bash

echo "Cloudinary CLI Test"
echo "==================="

# Hardcoded Cloudinary credentials - UPDATE THESE WITH YOUR ACTUAL VALUES
CLOUDINARY_CLOUD_NAME="dlhv5towy"
CLOUDINARY_API_KEY="785245949597287"
CLOUDINARY_API_SECRET="BX5z56TipOMFmpMoDyI2RwVIPLA"

echo "Using Cloudinary credentials:"
echo "Cloud Name: $CLOUDINARY_CLOUD_NAME"
echo "API Key: ${CLOUDINARY_API_KEY:0:8}..."

# Test CLI help
echo ""
echo "Testing CLI help..."
npx cloudinary-cli --help

# Test CLI configuration
echo ""
echo "Testing CLI configuration..."
npx cloudinary-cli config

# Test account info
echo ""
echo "Testing account info..."
npx cloudinary-cli account --cloud_name=$CLOUDINARY_CLOUD_NAME --api_key=$CLOUDINARY_API_KEY --api_secret=$CLOUDINARY_API_SECRET

# Test listing resources
echo ""
echo "Testing resource listing..."
npx cloudinary-cli resources --type=upload --max_results=5 --cloud_name=$CLOUDINARY_CLOUD_NAME --api_key=$CLOUDINARY_API_KEY --api_secret=$CLOUDINARY_API_SECRET

# Test uploading a sample image file
echo ""
echo "Creating test image file for upload..."
# Create a simple SVG image for testing
cat > test_image.svg << 'EOF'
<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
  <rect width="100" height="100" fill="blue"/>
  <text x="50" y="50" text-anchor="middle" fill="white" font-size="12">Test</text>
</svg>
EOF

echo "Testing image upload..."
npx cloudinary-cli upload test_image.svg --public_id=cli_test_image --cloud_name=$CLOUDINARY_CLOUD_NAME --api_key=$CLOUDINARY_API_KEY --api_secret=$CLOUDINARY_API_SECRET

# Clean up test file
rm test_image.svg

echo ""
echo "🎉 CLI test completed!" 