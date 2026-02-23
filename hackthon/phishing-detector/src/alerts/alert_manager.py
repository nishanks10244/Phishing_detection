import logging
from datetime import datetime
from typing import Dict, List, Callable
from enum import Enum
import json

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Alert:
    """Represents a phishing detection alert"""
    
    def __init__(
        self,
        alert_id: str,
        severity: AlertSeverity,
        message: str,
        details: Dict,
        timestamp: datetime = None
    ):
        self.alert_id = alert_id
        self.severity = severity
        self.message = message
        self.details = details
        self.timestamp = timestamp or datetime.utcnow()
        self.read = False
        self.acknowledged = False
    
    def to_dict(self) -> Dict:
        """Convert alert to dictionary"""
        return {
            'alert_id': self.alert_id,
            'severity': self.severity.value,
            'message': self.message,
            'details': self.details,
            'timestamp': self.timestamp.isoformat(),
            'read': self.read,
            'acknowledged': self.acknowledged
        }
    
    def __repr__(self) -> str:
        return f"<Alert {self.alert_id}: {self.severity.value} - {self.message}>"

class AlertManager:
    """Manages alerts and notifications"""
    
    def __init__(self):
        self.alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.handlers: List[Callable] = []
        self.max_alerts = 1000
    
    def create_alert(
        self,
        severity: AlertSeverity,
        message: str,
        details: Dict,
        alert_id: str = None
    ) -> Alert:
        """Create a new alert"""
        if alert_id is None:
            alert_id = self._generate_alert_id()
        
        alert = Alert(alert_id, severity, message, details)
        self.alerts[alert_id] = alert
        self.alert_history.append(alert)
        
        # Keep history size manageable
        if len(self.alert_history) > self.max_alerts:
            self.alert_history = self.alert_history[-self.max_alerts:]
        
        # Notify handlers
        self._notify_handlers(alert)
        
        logger.info(f"Alert created: {alert}")
        return alert
    
    def get_alert(self, alert_id: str) -> Alert:
        """Get alert by ID"""
        return self.alerts.get(alert_id)
    
    def get_all_alerts(self, unread_only: bool = False) -> List[Dict]:
        """Get all alerts"""
        alerts = list(self.alerts.values())
        
        if unread_only:
            alerts = [a for a in alerts if not a.read]
        
        return [a.to_dict() for a in sorted(alerts, key=lambda a: a.timestamp, reverse=True)]
    
    def mark_alert_as_read(self, alert_id: str) -> bool:
        """Mark alert as read"""
        if alert_id in self.alerts:
            self.alerts[alert_id].read = True
            return True
        return False
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge/dismiss alert"""
        if alert_id in self.alerts:
            self.alerts[alert_id].acknowledged = True
            return True
        return False
    
    def delete_alert(self, alert_id: str) -> bool:
        """Delete alert"""
        if alert_id in self.alerts:
            del self.alerts[alert_id]
            return True
        return False
    
    def clear_old_alerts(self, days: int = 30):
        """Remove alerts older than specified days"""
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        to_delete = []
        for alert_id, alert in self.alerts.items():
            if alert.timestamp < cutoff_date:
                to_delete.append(alert_id)
        
        for alert_id in to_delete:
            del self.alerts[alert_id]
        
        logger.info(f"Cleared {len(to_delete)} old alerts")
        return len(to_delete)
    
    def register_handler(self, handler: Callable):
        """Register alert handler/listener"""
        self.handlers.append(handler)
    
    def unregister_handler(self, handler: Callable):
        """Unregister alert handler"""
        if handler in self.handlers:
            self.handlers.remove(handler)
    
    def _notify_handlers(self, alert: Alert):
        """Notify all registered handlers"""
        for handler in self.handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Error in alert handler: {e}")
    
    def _generate_alert_id(self) -> str:
        """Generate unique alert ID"""
        import uuid
        return str(uuid.uuid4())
    
    def get_stats(self) -> Dict:
        """Get alert statistics"""
        severity_counts = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0
        }
        
        for alert in self.alerts.values():
            severity_counts[alert.severity.value] += 1
        
        return {
            'total_active': len(self.alerts),
            'total_history': len(self.alert_history),
            'by_severity': severity_counts,
            'unread_count': sum(1 for a in self.alerts.values() if not a.read)
        }

class EmailAlertFormatter:
    """Format alerts for email notifications"""
    
    @staticmethod
    def format_alert(alert: Alert) -> str:
        """Format alert as email text"""
        return f"""
Phishing Alert - {alert.severity.value.upper()}

ID: {alert.alert_id}
Time: {alert.timestamp}

Message: {alert.message}

Details:
{json.dumps(alert.details, indent=2)}
"""

class WebSocketAlertHandler:
    """Handle WebSocket alert notifications"""
    
    def __init__(self, socketio):
        self.socketio = socketio
    
    def send_alert(self, alert: Alert):
        """Send alert via WebSocket"""
        try:
            self.socketio.emit(
                'phishing_alert',
                alert.to_dict(),
                broadcast=True,
                namespace='/alerts'
            )
            logger.info(f"Alert sent via WebSocket: {alert.alert_id}")
        except Exception as e:
            logger.error(f"Error sending alert via WebSocket: {e}")
