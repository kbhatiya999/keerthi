import os
import json
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()

class NotificationService:
    """Real-time notification service for ecommerce platform"""
    
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.freesmtpservers.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '25'))
        self.smtp_username = os.getenv('SMTP_USERNAME', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.admin_email = os.getenv('ADMIN_EMAIL', 'admin@ecommerce.com')
        self.webhook_url = os.getenv('WEBHOOK_URL')
        
        # Check if using free SMTP server (no auth required)
        self.requires_auth = bool(self.smtp_username and self.smtp_password)
        
    def send_email(self, to_email: str, subject: str, body: str, html_body: Optional[str] = None):
        """Send email notification"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.smtp_username if self.smtp_username else 'noreply@ecommerce.com'
            msg['To'] = to_email
            
            # Add text and HTML parts
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)
            
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                # Only use authentication if credentials are provided
                if self.requires_auth:
                    server.starttls()
                    server.login(self.smtp_username, self.smtp_password)
                
                server.send_message(msg)
                
            print(f"✅ Email notification sent to {to_email}: {subject}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email notification: {e}")
            return False
    
    def send_webhook(self, payload: Dict[str, Any]):
        """Send webhook notification"""
        try:
            if not self.webhook_url:
                print("⚠️ No webhook URL configured")
                return False
                
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ Webhook notification sent: {payload.get('type', 'unknown')}")
                return True
            else:
                print(f"❌ Webhook failed with status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to send webhook notification: {e}")
            return False
    
    def notify_order_status_change(self, order_id: str, customer_email: str, 
                                 old_status: str, new_status: str, order_details: Dict[str, Any]):
        """Notify customer about order status change"""
        subject = f"Order #{order_id} Status Update: {new_status.title()}"
        
        body = f"""
        Your order status has been updated!
        
        Order ID: {order_id}
        Previous Status: {old_status.title()}
        New Status: {new_status.title()}
        Total Amount: ${order_details.get('total_amount', 0):.2f}
        
        Track your order at: http://localhost:3000/orders/{order_id}
        
        Thank you for shopping with us!
        """
        
        html_body = f"""
        <html>
        <body>
            <h2>Order Status Update</h2>
            <p>Your order status has been updated!</p>
            <table>
                <tr><td><strong>Order ID:</strong></td><td>{order_id}</td></tr>
                <tr><td><strong>Previous Status:</strong></td><td>{old_status.title()}</td></tr>
                <tr><td><strong>New Status:</strong></td><td>{new_status.title()}</td></tr>
                <tr><td><strong>Total Amount:</strong></td><td>${order_details.get('total_amount', 0):.2f}</td></tr>
            </table>
            <p><a href="http://localhost:3000/orders/{order_id}">Track your order</a></p>
            <p>Thank you for shopping with us!</p>
        </body>
        </html>
        """
        
        # Send email to customer
        self.send_email(customer_email, subject, body, html_body)
        
        # Send webhook for real-time updates
        webhook_payload = {
            "type": "order_status_change",
            "order_id": order_id,
            "customer_email": customer_email,
            "old_status": old_status,
            "new_status": new_status,
            "timestamp": datetime.utcnow().isoformat(),
            "order_details": order_details
        }
        self.send_webhook(webhook_payload)
    
    def notify_stock_alert(self, product_id: str, product_name: str, 
                          current_stock: int, threshold: int = 10):
        """Notify admin about low stock"""
        subject = f"🚨 Low Stock Alert: {product_name}"
        
        body = f"""
        LOW STOCK ALERT!
        
        Product: {product_name}
        Product ID: {product_id}
        Current Stock: {current_stock}
        Threshold: {threshold}
        
        Please restock this item immediately!
        """
        
        html_body = f"""
        <html>
        <body>
            <h2 style="color: red;">🚨 Low Stock Alert</h2>
            <table>
                <tr><td><strong>Product:</strong></td><td>{product_name}</td></tr>
                <tr><td><strong>Product ID:</strong></td><td>{product_id}</td></tr>
                <tr><td><strong>Current Stock:</strong></td><td style="color: red;">{current_stock}</td></tr>
                <tr><td><strong>Threshold:</strong></td><td>{threshold}</td></tr>
            </table>
            <p><strong>Please restock this item immediately!</strong></p>
        </body>
        </html>
        """
        
        # Send email to admin
        self.send_email(self.admin_email, subject, body, html_body)
        
        # Send webhook
        webhook_payload = {
            "type": "stock_alert",
            "product_id": product_id,
            "product_name": product_name,
            "current_stock": current_stock,
            "threshold": threshold,
            "timestamp": datetime.utcnow().isoformat(),
            "severity": "high" if current_stock <= 5 else "medium"
        }
        self.send_webhook(webhook_payload)
    
    def notify_fraud_alert(self, transaction_id: str, customer_id: str, 
                          amount: float, reason: str, risk_score: float):
        """Notify admin about potential fraud"""
        subject = f"🚨 Fraud Alert: Transaction #{transaction_id}"
        
        body = f"""
        FRAUD ALERT!
        
        Transaction ID: {transaction_id}
        Customer ID: {customer_id}
        Amount: ${amount:.2f}
        Risk Score: {risk_score:.2f}
        Reason: {reason}
        
        Please review this transaction immediately!
        """
        
        html_body = f"""
        <html>
        <body>
            <h2 style="color: red;">🚨 Fraud Alert</h2>
            <table>
                <tr><td><strong>Transaction ID:</strong></td><td>{transaction_id}</td></tr>
                <tr><td><strong>Customer ID:</strong></td><td>{customer_id}</td></tr>
                <tr><td><strong>Amount:</strong></td><td>${amount:.2f}</td></tr>
                <tr><td><strong>Risk Score:</strong></td><td style="color: red;">{risk_score:.2f}</td></tr>
                <tr><td><strong>Reason:</strong></td><td>{reason}</td></tr>
            </table>
            <p><strong>Please review this transaction immediately!</strong></p>
        </body>
        </html>
        """
        
        # Send email to admin
        self.send_email(self.admin_email, subject, body, html_body)
        
        # Send webhook
        webhook_payload = {
            "type": "fraud_alert",
            "transaction_id": transaction_id,
            "customer_id": customer_id,
            "amount": amount,
            "reason": reason,
            "risk_score": risk_score,
            "timestamp": datetime.utcnow().isoformat(),
            "severity": "high" if risk_score > 0.8 else "medium"
        }
        self.send_webhook(webhook_payload)
    
    def notify_payment_success(self, order_id: str, customer_email: str, amount: float):
        """Notify customer about successful payment"""
        subject = f"✅ Payment Confirmed - Order #{order_id}"
        
        body = f"""
        Payment Confirmed!
        
        Order ID: {order_id}
        Amount: ${amount:.2f}
        
        Your order is being processed. You'll receive updates as your order progresses.
        
        Thank you for your purchase!
        """
        
        html_body = f"""
        <html>
        <body>
            <h2 style="color: green;">✅ Payment Confirmed</h2>
            <table>
                <tr><td><strong>Order ID:</strong></td><td>{order_id}</td></tr>
                <tr><td><strong>Amount:</strong></td><td>${amount:.2f}</td></tr>
            </table>
            <p>Your order is being processed. You'll receive updates as your order progresses.</p>
            <p>Thank you for your purchase!</p>
        </body>
        </html>
        """
        
        self.send_email(customer_email, subject, body, html_body)
    
    def notify_payment_failure(self, order_id: str, customer_email: str, amount: float, reason: str):
        """Notify customer about failed payment"""
        subject = f"❌ Payment Failed - Order #{order_id}"
        
        body = f"""
        Payment Failed
        
        Order ID: {order_id}
        Amount: ${amount:.2f}
        Reason: {reason}
        
        Please try again or contact support if the problem persists.
        """
        
        html_body = f"""
        <html>
        <body>
            <h2 style="color: red;">❌ Payment Failed</h2>
            <table>
                <tr><td><strong>Order ID:</strong></td><td>{order_id}</td></tr>
                <tr><td><strong>Amount:</strong></td><td>${amount:.2f}</td></tr>
                <tr><td><strong>Reason:</strong></td><td>{reason}</td></tr>
            </table>
            <p>Please try again or contact support if the problem persists.</p>
        </body>
        </html>
        """
        
        self.send_email(customer_email, subject, body, html_body)

# Global notification service instance
notification_service = NotificationService() 