#!/bin/bash

echo "🚀 Phase 1 Real-time Features Setup"
echo "==================================="

# Check if .env file exists
if [ ! -f "../.env" ]; then
    echo "❌ .env file not found. Creating from example..."
    cp ../.env.example ../.env
    echo "✅ .env file created from example"
fi

# Update .env with free SMTP configuration
echo "📧 Configuring SMTP for testing..."
sed -i 's/SMTP_SERVER=.*/SMTP_SERVER=smtp.freesmtpservers.com/' ../.env
sed -i 's/SMTP_PORT=.*/SMTP_PORT=25/' ../.env
sed -i 's/SMTP_USERNAME=.*/SMTP_USERNAME=/' ../.env
sed -i 's/SMTP_PASSWORD=.*/SMTP_PASSWORD=/' ../.env
sed -i 's/ADMIN_EMAIL=.*/ADMIN_EMAIL=test@example.com/' ../.env

echo "✅ SMTP configuration updated for free server"

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r ../requirements.txt

echo "✅ Dependencies installed"

# Test SMTP configuration
echo "🧪 Testing SMTP configuration..."
python test-smtp.py

echo ""
echo "🎉 Phase 1 setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Update ADMIN_EMAIL in .env to your actual email"
echo "2. Start the backend server: python main.py"
echo "3. Run the full test suite: python test-realtime-features.py"
echo ""
echo "🔗 Useful commands:"
echo "  - Test SMTP: python test-smtp.py"
echo "  - Test all features: python test-realtime-features.py"
echo "  - Start server: python main.py"
echo "  - API docs: http://localhost:8000/docs" 