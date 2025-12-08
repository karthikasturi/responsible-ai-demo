"""
Alert management system for LLM monitoring.
Supports multiple notification channels: Slack, Email, Console, File logs.
"""
import os
import logging
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List, Optional
from collections import deque
import requests

logger = logging.getLogger(__name__)

# Alert configuration
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
ALERT_EMAIL = os.getenv("ALERT_EMAIL")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

ALERT_LOG_FILE = "/app/data/alerts.log"


class AlertManager:
    """
    Manages alerts for various conditions in the LLM application.
    """
    
    def __init__(self):
        """Initialize alert manager."""
        self.alert_history = deque(maxlen=100)
        self.consecutive_failures = {
            "relevance": 0,
            "coherence": 0,
            "quality": 0
        }
        self.alert_thresholds = {
            "relevance_threshold": float(os.getenv("RELEVANCE_THRESHOLD", "0.7")),
            "quality_threshold": float(os.getenv("QUALITY_THRESHOLD", "0.6")),
            "drift_threshold": float(os.getenv("DRIFT_THRESHOLD", "0.3")),
            "consecutive_failures": 10,
            "toxicity_threshold": 0.3,
            "hallucination_threshold": 0.4
        }
    
    def check_quality_alert(self, evaluation: Dict) -> Optional[Dict]:
        """
        Check if quality metrics trigger an alert.
        
        Alert conditions:
        - Relevance < 0.7 for 10 consecutive requests
        - Overall quality < 0.6
        """
        if not evaluation.get("evaluations_available"):
            return None
        
        scores = evaluation.get("scores", {})
        overall_quality = evaluation.get("overall_quality")
        
        alert = None
        
        # Check relevance
        relevance = scores.get("relevance")
        if relevance is not None:
            if relevance < self.alert_thresholds["relevance_threshold"]:
                self.consecutive_failures["relevance"] += 1
            else:
                self.consecutive_failures["relevance"] = 0
            
            if self.consecutive_failures["relevance"] >= self.alert_thresholds["consecutive_failures"]:
                alert = {
                    "type": "quality_degradation",
                    "severity": "high",
                    "metric": "relevance",
                    "value": relevance,
                    "threshold": self.alert_thresholds["relevance_threshold"],
                    "consecutive_failures": self.consecutive_failures["relevance"],
                    "message": f"Relevance below threshold for {self.consecutive_failures['relevance']} consecutive requests"
                }
        
        # Check overall quality
        if overall_quality is not None and overall_quality < self.alert_thresholds["quality_threshold"]:
            alert = {
                "type": "quality_degradation",
                "severity": "medium",
                "metric": "overall_quality",
                "value": overall_quality,
                "threshold": self.alert_thresholds["quality_threshold"],
                "message": f"Overall quality below threshold: {overall_quality:.3f}"
            }
        
        if alert:
            alert["timestamp"] = datetime.utcnow().isoformat()
            self._send_alert(alert)
        
        return alert
    
    def check_drift_alert(self, drift_results: Dict) -> Optional[Dict]:
        """
        Check if drift detection triggers an alert.
        
        Alert conditions:
        - Embedding distance > threshold
        - Any drift detected
        """
        if not drift_results.get("any_drift_detected"):
            return None
        
        alert = {
            "type": "drift_detected",
            "severity": "high",
            "timestamp": datetime.utcnow().isoformat(),
            "details": []
        }
        
        # Check response drift
        if drift_results.get("response_drift", {}).get("drift_detected"):
            rd = drift_results["response_drift"]
            alert["details"].append({
                "drift_type": "response",
                "distance": rd.get("distance"),
                "threshold": rd.get("threshold")
            })
        
        # Check data drift
        if drift_results.get("data_drift", {}).get("drift_detected"):
            dd = drift_results["data_drift"]
            alert["details"].append({
                "drift_type": "data",
                "distance": dd.get("distance"),
                "threshold": dd.get("threshold")
            })
        
        # Check quality drift
        if drift_results.get("quality_drift", {}).get("drift_detected"):
            qd = drift_results["quality_drift"]
            alert["details"].append({
                "drift_type": "quality",
                "recent_avg": qd.get("recent_average"),
                "overall_avg": qd.get("overall_average")
            })
        
        alert["message"] = f"Drift detected: {', '.join([d['drift_type'] for d in alert['details']])}"
        
        self._send_alert(alert)
        return alert
    
    def check_toxicity_alert(self, text: str, score: float) -> Optional[Dict]:
        """Check if toxicity score triggers an alert."""
        if score > self.alert_thresholds["toxicity_threshold"]:
            alert = {
                "type": "toxicity",
                "severity": "critical",
                "score": score,
                "threshold": self.alert_thresholds["toxicity_threshold"],
                "text_preview": text[:100],
                "timestamp": datetime.utcnow().isoformat(),
                "message": f"High toxicity detected: {score:.3f}"
            }
            self._send_alert(alert)
            return alert
        return None
    
    def check_hallucination_alert(self, score: float) -> Optional[Dict]:
        """Check if hallucination score triggers an alert."""
        if score > self.alert_thresholds["hallucination_threshold"]:
            alert = {
                "type": "hallucination",
                "severity": "high",
                "score": score,
                "threshold": self.alert_thresholds["hallucination_threshold"],
                "timestamp": datetime.utcnow().isoformat(),
                "message": f"Potential hallucination detected: {score:.3f}"
            }
            self._send_alert(alert)
            return alert
        return None
    
    def _send_alert(self, alert: Dict):
        """Send alert through all configured channels."""
        self.alert_history.append(alert)
        
        # Console logging
        self._log_to_console(alert)
        
        # File logging
        self._log_to_file(alert)
        
        # Slack webhook
        if SLACK_WEBHOOK_URL:
            self._send_to_slack(alert)
        
        # Email
        if ALERT_EMAIL and SMTP_USER and SMTP_PASSWORD:
            self._send_email(alert)
    
    def _log_to_console(self, alert: Dict):
        """Log alert to console."""
        severity = alert.get("severity", "info").upper()
        message = alert.get("message", "Alert triggered")
        logger.warning(f"[ALERT:{severity}] {message}")
    
    def _log_to_file(self, alert: Dict):
        """Log alert to file."""
        try:
            os.makedirs(os.path.dirname(ALERT_LOG_FILE), exist_ok=True)
            with open(ALERT_LOG_FILE, 'a') as f:
                f.write(json.dumps(alert) + "\n")
        except Exception as e:
            logger.error(f"Failed to log alert to file: {e}")
    
    def _send_to_slack(self, alert: Dict):
        """Send alert to Slack via webhook."""
        try:
            severity_emoji = {
                "critical": "🚨",
                "high": "⚠️",
                "medium": "⚡",
                "low": "ℹ️"
            }
            
            emoji = severity_emoji.get(alert.get("severity", "medium"), "🔔")
            
            payload = {
                "text": f"{emoji} *{alert.get('type', 'Alert').upper()}*",
                "attachments": [{
                    "color": "danger" if alert.get("severity") in ["critical", "high"] else "warning",
                    "fields": [
                        {
                            "title": "Message",
                            "value": alert.get("message", "No message"),
                            "short": False
                        },
                        {
                            "title": "Severity",
                            "value": alert.get("severity", "unknown").upper(),
                            "short": True
                        },
                        {
                            "title": "Timestamp",
                            "value": alert.get("timestamp", "N/A"),
                            "short": True
                        }
                    ]
                }]
            }
            
            response = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=5)
            response.raise_for_status()
            logger.info("Alert sent to Slack")
            
        except Exception as e:
            logger.error(f"Failed to send alert to Slack: {e}")
    
    def _send_email(self, alert: Dict):
        """Send alert via email."""
        try:
            msg = MIMEMultipart()
            msg['From'] = SMTP_USER
            msg['To'] = ALERT_EMAIL
            msg['Subject'] = f"[{alert.get('severity', 'ALERT').upper()}] LLM Monitoring Alert"
            
            body = f"""
            Alert Type: {alert.get('type', 'Unknown')}
            Severity: {alert.get('severity', 'Unknown')}
            Timestamp: {alert.get('timestamp', 'N/A')}
            
            Message: {alert.get('message', 'No message')}
            
            Details:
            {json.dumps(alert, indent=2)}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)
            
            logger.info(f"Alert email sent to {ALERT_EMAIL}")
            
        except Exception as e:
            logger.error(f"Failed to send alert email: {e}")
    
    def get_alert_history(self, limit: int = 20) -> List[Dict]:
        """Get recent alerts."""
        return list(self.alert_history)[-limit:]
    
    def get_alert_statistics(self) -> Dict:
        """Get alert statistics."""
        if not self.alert_history:
            return {"total_alerts": 0}
        
        by_type = {}
        by_severity = {}
        
        for alert in self.alert_history:
            alert_type = alert.get("type", "unknown")
            severity = alert.get("severity", "unknown")
            
            by_type[alert_type] = by_type.get(alert_type, 0) + 1
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        return {
            "total_alerts": len(self.alert_history),
            "by_type": by_type,
            "by_severity": by_severity,
            "recent_count": len([a for a in list(self.alert_history)[-10:]])
        }


# Global alert manager
alert_manager = AlertManager()


def get_alert_manager() -> AlertManager:
    """Get the global alert manager instance."""
    return alert_manager
