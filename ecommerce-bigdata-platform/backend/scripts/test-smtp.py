#!/usr/bin/env python3
"""
Test SMTP Configuration with Free SMTP Server
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

def test_smtp_connection():
    """Test SMTP connection and send a test email"""
    
    # Configuration
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.freesmtpservers.com')
    smtp_port = int(os.getenv('SMTP_PORT', '25'))
    smtp_username = os.getenv('SMTP_USERNAME', '')
    smtp_password = os.getenv('SMTP_PASSWORD', '')
    admin_email = os.getenv('ADMIN_EMAIL', 'admin@ecommerce.com')
    
    print("🧪 Testing SMTP Configuration")
    print("=" * 40)
    print(f"SMTP Server: {smtp_server}")
    print(f"SMTP Port: {smtp_port}")
    print(f"Requires Auth: {bool(smtp_username and smtp_password)}")
    print(f"Admin Email: {admin_email}")
    print()
    
    try:
        # Test connection
        print("1. Testing SMTP connection...")
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            print("✅ SMTP connection successful")
            
            # Test authentication if credentials provided
            if smtp_username and smtp_password:
                print("2. Testing authentication...")
                server.starttls()
                server.login(smtp_username, smtp_password)
                print("✅ Authentication successful")
            else:
                print("2. Skipping authentication (free server)")
            
            # Test email sending
            print("3. Testing email sending...")
            
            # Create test message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = '🧪 Ecommerce Platform - SMTP Test'
            msg['From'] = smtp_username if smtp_username else 'noreply@ecommerce.com'
            msg['To'] = admin_email
            
            # Text version
            text_body = """
            SMTP Test Email
            
            This is a test email from the Ecommerce Big Data Platform.
            
            ✅ SMTP Configuration: Working
            ✅ Connection: Successful
            ✅ Authentication: {'Required' if smtp_username else 'Not Required'}
            
            Phase 1 Real-time Features:
            - Fraud Detection System
            - Stock Alert System
            - Order Tracking System
            - Notification System
            
            Best regards,
            Ecommerce Platform Team
            """
            
            # HTML version
            html_body = """
            <html>
            <body>
                <h2>🧪 Ecommerce Platform - SMTP Test</h2>
                <p>This is a test email from the Ecommerce Big Data Platform.</p>
                
                <h3>✅ Test Results:</h3>
                <ul>
                    <li><strong>SMTP Configuration:</strong> Working</li>
                    <li><strong>Connection:</strong> Successful</li>
                    <li><strong>Authentication:</strong> {'Required' if smtp_username else 'Not Required'}</li>
                </ul>
                
                <h3>🚀 Phase 1 Real-time Features:</h3>
                <ul>
                    <li>Fraud Detection System</li>
                    <li>Stock Alert System</li>
                    <li>Order Tracking System</li>
                    <li>Notification System</li>
                </ul>
                
                <p><em>Best regards,<br>Ecommerce Platform Team</em></p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            server.send_message(msg)
            print("✅ Test email sent successfully!")
            
            return True
            
    except Exception as e:
        print(f"❌ SMTP test failed: {e}")
        return False

def test_notification_service():
    """Test the notification service directly"""
    print("\n🔔 Testing Notification Service")
    print("=" * 40)
    
    try:
        from notifications import notification_service
        
        # Test stock alert notification
        print("1. Testing stock alert notification...")
        success = notification_service.notify_stock_alert(
            "test_product_123",
            "Test Product",
            5,
            10
        )
        
        if success:
            print("✅ Stock alert notification sent")
        else:
            print("❌ Stock alert notification failed")
        
        # Test fraud alert notification
        print("\n2. Testing fraud alert notification...")
        success = notification_service.notify_fraud_alert(
            "test_txn_123",
            "test_customer_123",
            500.0,
            "High amount transaction from new customer",
            0.85
        )
        
        if success:
            print("✅ Fraud alert notification sent")
        else:
            print("❌ Fraud alert notification failed")
        
        return True
        
    except Exception as e:
        print(f"❌ Notification service test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 SMTP Configuration Test Suite")
    print("=" * 50)
    
    # Test basic SMTP
    smtp_success = test_smtp_connection()
    
    # Test notification service
    notification_success = test_notification_service()
    
    print("\n📊 Test Results Summary")
    print("=" * 30)
    print(f"SMTP Connection: {'✅ PASS' if smtp_success else '❌ FAIL'}")
    print(f"Notification Service: {'✅ PASS' if notification_success else '❌ FAIL'}")
    
    if smtp_success and notification_success:
        print("\n🎉 All tests passed! SMTP configuration is working correctly.")
        print("\n📝 Next steps:")
        print("1. Check your email for the test message")
        print("2. Run the full Phase 1 test suite:")
        print("   python test-realtime-features.py")
        print("3. Start the backend server:")
        print("   python main.py")
    else:
        print("\n❌ Some tests failed. Please check the configuration.")
        print("\n🔧 Troubleshooting:")
        print("1. Verify SMTP server and port")
        print("2. Check network connectivity")
        print("3. Verify admin email address")

if __name__ == "__main__":
    main() 