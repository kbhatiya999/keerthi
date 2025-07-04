import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict, deque
import hashlib

class RealTimeAnalytics:
    """Real-time analytics for fraud detection, stock monitoring, and order tracking"""
    
    def __init__(self):
        # Fraud detection data structures
        self.customer_transactions = defaultdict(list)  # customer_id -> list of transactions
        self.ip_transactions = defaultdict(list)  # ip_address -> list of transactions
        self.device_transactions = defaultdict(list)  # device_id -> list of transactions
        self.suspicious_patterns = deque(maxlen=1000)  # Recent suspicious activities
        
        # Stock monitoring
        self.stock_alerts = {}  # product_id -> alert_info
        self.stock_thresholds = defaultdict(lambda: 10)  # Default threshold
        
        # Order tracking
        self.order_status_history = defaultdict(list)  # order_id -> status_changes
        self.real_time_orders = {}  # order_id -> current_status
        
        # Configuration
        self.fraud_thresholds = {
            'max_amount_per_hour': 1000.0,
            'max_orders_per_hour': 5,
            'max_failed_payments': 3,
            'suspicious_amount': 500.0,
            'new_customer_limit': 200.0
        }
    
    def analyze_transaction_fraud(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze transaction for potential fraud"""
        customer_id = transaction_data.get('customer_id')
        amount = transaction_data.get('amount', 0)
        ip_address = transaction_data.get('ip_address', '')
        device_id = transaction_data.get('device_id', '')
        timestamp = datetime.fromisoformat(transaction_data.get('timestamp', datetime.utcnow().isoformat()))
        
        risk_factors = []
        risk_score = 0.0
        
        # Check customer transaction history
        if customer_id:
            customer_txns = self.customer_transactions[customer_id]
            recent_txns = [txn for txn in customer_txns 
                          if timestamp - datetime.fromisoformat(txn['timestamp']) < timedelta(hours=1)]
            
            # High frequency transactions
            if len(recent_txns) >= self.fraud_thresholds['max_orders_per_hour']:
                risk_factors.append(f"High transaction frequency: {len(recent_txns)} in 1 hour")
                risk_score += 0.3
            
            # High amount transactions
            total_amount = sum(txn.get('amount', 0) for txn in recent_txns) + amount
            if total_amount > self.fraud_thresholds['max_amount_per_hour']:
                risk_factors.append(f"High amount in 1 hour: ${total_amount:.2f}")
                risk_score += 0.4
            
            # New customer with high amount
            if len(customer_txns) == 0 and amount > self.fraud_thresholds['new_customer_limit']:
                risk_factors.append(f"New customer with high amount: ${amount:.2f}")
                risk_score += 0.5
        
        # Check IP-based patterns
        if ip_address:
            ip_txns = self.ip_transactions[ip_address]
            recent_ip_txns = [txn for txn in ip_txns 
                             if timestamp - datetime.fromisoformat(txn['timestamp']) < timedelta(hours=1)]
            
            if len(recent_ip_txns) >= 3:  # Multiple transactions from same IP
                risk_factors.append(f"Multiple transactions from same IP: {len(recent_ip_txns)}")
                risk_score += 0.2
        
        # Check device-based patterns
        if device_id:
            device_txns = self.device_transactions[device_id]
            recent_device_txns = [txn for txn in device_txns 
                                 if timestamp - datetime.fromisoformat(txn['timestamp']) < timedelta(hours=1)]
            
            if len(recent_device_txns) >= 3:  # Multiple transactions from same device
                risk_factors.append(f"Multiple transactions from same device: {len(recent_device_txns)}")
                risk_score += 0.2
        
        # Suspicious amount patterns
        if amount > self.fraud_thresholds['suspicious_amount']:
            risk_factors.append(f"Suspicious amount: ${amount:.2f}")
            risk_score += 0.3
        
        # Store transaction for future analysis
        transaction_record = {
            'customer_id': customer_id,
            'amount': amount,
            'ip_address': ip_address,
            'device_id': device_id,
            'timestamp': timestamp.isoformat(),
            'risk_score': risk_score,
            'risk_factors': risk_factors
        }
        
        if customer_id:
            self.customer_transactions[customer_id].append(transaction_record)
        if ip_address:
            self.ip_transactions[ip_address].append(transaction_record)
        if device_id:
            self.device_transactions[device_id].append(transaction_record)
        
        # Clean old transactions (older than 24 hours)
        self._cleanup_old_transactions()
        
        return {
            'is_fraudulent': risk_score > 0.7,
            'risk_score': min(risk_score, 1.0),
            'risk_factors': risk_factors,
            'recommendation': 'BLOCK' if risk_score > 0.8 else 'REVIEW' if risk_score > 0.5 else 'ALLOW'
        }
    
    def monitor_stock_levels(self, product_id: str, product_name: str, 
                           current_stock: int, threshold: Optional[int] = None) -> Dict[str, Any]:
        """Monitor stock levels and generate alerts"""
        if threshold is None:
            threshold = self.stock_thresholds[product_id]
        else:
            self.stock_thresholds[product_id] = threshold
        
        alert_needed = current_stock <= threshold
        severity = 'critical' if current_stock <= 5 else 'warning' if current_stock <= threshold else 'normal'
        
        alert_info = {
            'product_id': product_id,
            'product_name': product_name,
            'current_stock': current_stock,
            'threshold': threshold,
            'severity': severity,
            'alert_needed': alert_needed,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.stock_alerts[product_id] = alert_info
        
        return alert_info
    
    def track_order_status(self, order_id: str, new_status: str, 
                          customer_id: str, total_amount: float) -> Dict[str, Any]:
        """Track order status changes for real-time updates"""
        timestamp = datetime.utcnow()
        
        status_change = {
            'order_id': order_id,
            'old_status': self.real_time_orders.get(order_id, 'unknown'),
            'new_status': new_status,
            'customer_id': customer_id,
            'total_amount': total_amount,
            'timestamp': timestamp.isoformat()
        }
        
        # Store status history
        self.order_status_history[order_id].append(status_change)
        
        # Update current status
        self.real_time_orders[order_id] = new_status
        
        return status_change
    
    def get_order_tracking_info(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive order tracking information"""
        if order_id not in self.real_time_orders:
            return None
        
        history = self.order_status_history.get(order_id, [])
        current_status = self.real_time_orders[order_id]
        
        return {
            'order_id': order_id,
            'current_status': current_status,
            'status_history': history,
            'last_updated': history[-1]['timestamp'] if history else None,
            'total_status_changes': len(history)
        }
    
    def get_fraud_summary(self) -> Dict[str, Any]:
        """Get summary of fraud detection activities"""
        total_suspicious = len(self.suspicious_patterns)
        recent_suspicious = len([p for p in self.suspicious_patterns 
                               if datetime.fromisoformat(p['timestamp']) > datetime.utcnow() - timedelta(hours=1)])
        
        return {
            'total_suspicious_transactions': total_suspicious,
            'recent_suspicious_transactions': recent_suspicious,
            'active_customers_monitored': len(self.customer_transactions),
            'active_ips_monitored': len(self.ip_transactions),
            'fraud_thresholds': self.fraud_thresholds
        }
    
    def get_stock_alerts_summary(self) -> Dict[str, Any]:
        """Get summary of stock alerts"""
        critical_alerts = [alert for alert in self.stock_alerts.values() 
                          if alert['severity'] == 'critical']
        warning_alerts = [alert for alert in self.stock_alerts.values() 
                         if alert['severity'] == 'warning']
        
        return {
            'total_alerts': len(self.stock_alerts),
            'critical_alerts': len(critical_alerts),
            'warning_alerts': len(warning_alerts),
            'products_monitored': len(self.stock_alerts)
        }
    
    def _cleanup_old_transactions(self):
        """Clean up old transaction data (older than 24 hours)"""
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        for customer_id in list(self.customer_transactions.keys()):
            self.customer_transactions[customer_id] = [
                txn for txn in self.customer_transactions[customer_id]
                if datetime.fromisoformat(txn['timestamp']) > cutoff_time
            ]
            if not self.customer_transactions[customer_id]:
                del self.customer_transactions[customer_id]
        
        for ip_address in list(self.ip_transactions.keys()):
            self.ip_transactions[ip_address] = [
                txn for txn in self.ip_transactions[ip_address]
                if datetime.fromisoformat(txn['timestamp']) > cutoff_time
            ]
            if not self.ip_transactions[ip_address]:
                del self.ip_transactions[ip_address]
        
        for device_id in list(self.device_transactions.keys()):
            self.device_transactions[device_id] = [
                txn for txn in self.device_transactions[device_id]
                if datetime.fromisoformat(txn['timestamp']) > cutoff_time
            ]
            if not self.device_transactions[device_id]:
                del self.device_transactions[device_id]

# Global real-time analytics instance
realtime_analytics = RealTimeAnalytics() 