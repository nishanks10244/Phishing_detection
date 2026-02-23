import re
import email
from email.mime.text import MIMEText
from typing import Dict, List, Tuple
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

class EmailParser:
    """Parse and extract features from email messages"""
    
    # Common suspicious keywords
    PHISHING_KEYWORDS = [
        'verify', 'confirm', 'urgent', 'immediate', 'action required',
        'update account', 'click here', 'validate', 'suspended',
        'limited', 'unusual activity', 'unauthorized', 'reset password',
        'prove identity', 'confirm identity', 'billing problem',
        'payment issue', 'claim', 'refund', 'tax return'
    ]
    
    def __init__(self):
        self.email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        self.url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
    
    def parse_email(self, email_content: str) -> Dict:
        """Parse email content and extract features"""
        try:
            msg = email.message_from_string(email_content)
            
            return {
                'subject': msg.get('Subject', ''),
                'sender': msg.get('From', ''),
                'recipient': msg.get('To', ''),
                'body': self._get_body(msg),
                'urls': self._extract_urls(email_content),
                'emails': self._extract_emails(email_content),
                'headers': dict(msg.items())
            }
        except Exception as e:
            logger.error(f"Error parsing email: {e}")
            return {}
    
    def _get_body(self, msg) -> str:
        """Extract email body"""
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        break
                    except Exception as e:
                        logger.warning(f"Error decoding email part: {e}")
        else:
            body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
        return body
    
    def _extract_urls(self, content: str) -> List[str]:
        """Extract all URLs from email"""
        urls = self.url_pattern.findall(content)
        return list(set(urls))  # Remove duplicates
    
    def _extract_emails(self, content: str) -> List[str]:
        """Extract all email addresses"""
        emails = self.email_pattern.findall(content)
        return list(set(emails))
    
    def extract_features(self, parsed_email: Dict) -> Dict:
        """Extract features for ML model"""
        subject = parsed_email.get('subject', '').lower()
        body = parsed_email.get('body', '').lower()
        urls = parsed_email.get('urls', [])
        sender = parsed_email.get('sender', '')
        
        combined_text = f"{subject} {body}"
        
        features = {
            'subject_length': len(subject),
            'body_length': len(body),
            'url_count': len(urls),
            'suspicious_keyword_count': sum(1 for keyword in self.PHISHING_KEYWORDS 
                                           if keyword in combined_text),
            'urgent_keywords': sum(1 for word in ['urgent', 'immediate', 'action required'] 
                                  if word in combined_text),
            'has_url': len(urls) > 0,
            'has_multiple_urls': len(urls) > 1,
            'sender_domain_suspicious': self._check_suspicious_sender(sender),
            'text_features': combined_text
        }
        
        return features
    
    def _check_suspicious_sender(self, sender: str) -> bool:
        """Check if sender domain is suspicious"""
        suspicious_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
        try:
            domain = sender.split('@')[1].lower() if '@' in sender else ''
            # If sender uses common email service with generic name, might be suspicious
            if any(domain.endswith(sd) for sd in suspicious_domains):
                if 'admin' in sender.lower() or 'support' in sender.lower():
                    return True
        except Exception as e:
            logger.warning(f"Error checking sender: {e}")
        
        return False
    
    @staticmethod
    def validate_email(email_str: str) -> bool:
        """Validate email format"""
        pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        return bool(pattern.match(email_str))


class URLAnalyzer:
    """Analyze URLs for phishing characteristics"""
    
    # Suspicious URL patterns
    SUSPICIOUS_PATTERNS = [
        r'(?:verify|confirm|update|login|signin|account|security|confirm-identity)',
        r'(?:paypal|amazon|apple|microsoft|google|bank)',  # Impersonation
        r'(?:bit\.ly|tinyurl|short\.link)',  # URL shorteners
    ]
    
    def __init__(self):
        pass
    
    def analyze_url(self, url: str) -> Dict:
        """Analyze URL for phishing characteristics"""
        try:
            parsed = urlparse(url)
            
            features = {
                'url': url,
                'domain': parsed.netloc,
                'path': parsed.path,
                'has_suspicious_pattern': self._check_suspicious_patterns(url),
                'has_ip_address': self._has_ip_address(parsed.netloc),
                'has_port': ':' in parsed.netloc and parsed.port is not None,
                'subdomain_count': parsed.netloc.count('.'),
                'url_length': len(url),
                'uses_https': parsed.scheme == 'https',
                'similarity_to_legitimate': 0  # To be computed
            }
            
            return features
        except Exception as e:
            logger.error(f"Error analyzing URL: {e}")
            return {}
    
    def _check_suspicious_patterns(self, url: str) -> bool:
        """Check for suspicious URL patterns"""
        url_lower = url.lower()
        for pattern in self.SUSPICIOUS_PATTERNS:
            if re.search(pattern, url_lower):
                return True
        return False
    
    def _has_ip_address(self, domain: str) -> bool:
        """Check if domain is an IP address"""
        parts = domain.split(':')[0].split('.')
        return len(parts) == 4 and all(part.isdigit() and 0 <= int(part) <= 255 for part in parts)
    
    def get_url_features_text(self, url_analysis: Dict) -> str:
        """Convert URL analysis to text for model"""
        features = []
        if url_analysis.get('has_ip_address'):
            features.append('ip_address')
        if url_analysis.get('has_suspicious_pattern'):
            features.append('suspicious_pattern')
        if not url_analysis.get('uses_https'):
            features.append('no_https')
        if url_analysis.get('url_length') > 75:
            features.append('long_url')
        if url_analysis.get('has_port'):
            features.append('non_standard_port')
        
        return ' '.join(features) if features else 'clean_url'
