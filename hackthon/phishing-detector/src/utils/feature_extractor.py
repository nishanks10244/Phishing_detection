import re
from typing import Dict, List
from .email_parser import EmailParser, URLAnalyzer
import logging

logger = logging.getLogger(__name__)

class FeatureExtractor:
    """Extract comprehensive features from emails and URLs"""
    
    def __init__(self):
        self.email_parser = EmailParser()
        self.url_analyzer = URLAnalyzer()
    
    def extract_email_features(self, email_content: str) -> Dict:
        """Extract all features from email"""
        parsed_email = self.email_parser.parse_email(email_content)
        
        subject = parsed_email.get('subject', '').lower()
        body = parsed_email.get('body', '').lower()
        urls = parsed_email.get('urls', [])
        sender = parsed_email.get('sender', '')
        
        combined_text = f"{subject} {body}"
        
        # Basic features
        basic_features = {
            'subject_length': len(subject),
            'body_length': len(body),
            'url_count': len(urls),
            'email_count': len(parsed_email.get('emails', [])),
            'has_url': len(urls) > 0,
            'has_attachment': 'attachment' in str(parsed_email.get('headers', {})).lower(),
        }
        
        # Text-based features
        text_features = {
            'urgent_words': self._count_urgent_words(combined_text),
            'financial_words': self._count_financial_words(combined_text),
            'personal_words': self._count_personal_words(combined_text),
            'action_words': self._count_action_words(combined_text),
            'urgency_score': self._calculate_urgency_score(combined_text),
        }
        
        # URL features
        url_features = self._analyze_urls(urls)
        
        # Sender features
        sender_features = {
            'sender_domain_mismatch': self._check_domain_mismatch(sender, urls),
            'sender_has_numbers': any(c.isdigit() for c in sender),
            'sender_suspicious': self._is_suspicious_sender(sender),
        }
        
        # Structural features
        structural_features = {
            'excessive_links': len(urls) > 3,
            'short_body': len(body) < 50,
            'many_exclamations': combined_text.count('!') > 2,
            'unusual_capitals': self._count_caps_ratio(combined_text) > 0.3,
        }
        
        # Combine all features
        all_features = {
            **basic_features,
            **text_features,
            **url_features,
            **sender_features,
            **structural_features,
            'full_text': combined_text[:5000]  # Limit for model
        }
        
        return all_features
    
    def extract_url_features(self, url: str) -> Dict:
        """Extract features from a single URL"""
        analysis = self.url_analyzer.analyze_url(url)
        
        features = {
            'url': url,
            'has_ip': analysis.get('has_ip_address', False),
            'has_suspicious_pattern': analysis.get('has_suspicious_pattern', False),
            'url_length': analysis.get('url_length', 0),
            'subdomain_count': analysis.get('subdomain_count', 0),
            'uses_https': analysis.get('uses_https', True),
            'has_port': analysis.get('has_port', False),
            'suspicious_tld': self._check_suspicious_tld(url),
        }
        
        return features
    
    def _count_urgent_words(self, text: str) -> int:
        """Count urgent/threatening words"""
        urgent_words = ['urgent', 'immediate', 'critical', 'expire', 'expired',
                       'confirm', 'verify', 'validate', 'act now', 'limited time']
        return sum(text.count(word) for word in urgent_words)
    
    def _count_financial_words(self, text: str) -> int:
        """Count financial-related words"""
        financial_words = ['payment', 'billing', 'credit card', 'account', 'bank',
                          'refund', 'tax', 'invoice', 'transaction', 'unauthorized']
        return sum(text.count(word) for word in financial_words)
    
    def _count_personal_words(self, text: str) -> int:
        """Count personal/identity words"""
        personal_words = ['identity', 'password', 'personal information', 'ssn',
                         'driver license', 'social security', 'prove', 'confirm identity']
        return sum(text.count(word) for word in personal_words)
    
    def _count_action_words(self, text: str) -> int:
        """Count action-oriented words"""
        action_words = ['click', 'download', 'install', 'open', 'submit', 'update',
                       'reset', 'change', 'confirm', 'respond']
        return sum(text.count(word) for word in action_words)
    
    def _calculate_urgency_score(self, text: str) -> float:
        """Calculate urgency score (0-1)"""
        urgent_indicators = ['!', 'urgent', 'immediate', 'confirm', 'verify']
        count = sum(text.count(word) for word in urgent_indicators)
        # Normalize to 0-1
        return min(count / 10, 1.0)
    
    def _analyze_urls(self, urls: List[str]) -> Dict:
        """Analyze list of URLs"""
        if not urls:
            return {'url_risk_score': 0, 'suspicious_urls': 0}
        
        suspicious_count = 0
        risk_scores = []
        
        for url in urls:
            features = self.extract_url_features(url)
            risk = 0
            if features['has_ip']:
                risk += 0.3
            if features['has_suspicious_pattern']:
                risk += 0.3
            if not features['uses_https']:
                risk += 0.2
            if features['url_length'] > 100:
                risk += 0.1
            if features['suspicious_tld']:
                risk += 0.1
            
            risk_scores.append(min(risk, 1.0))
            if risk > 0.5:
                suspicious_count += 1
        
        return {
            'url_risk_score': sum(risk_scores) / len(risk_scores),
            'suspicious_urls': suspicious_count,
        }
    
    def _check_domain_mismatch(self, sender: str, urls: List[str]) -> bool:
        """Check if sender domain matches URL domains"""
        try:
            if '@' not in sender or not urls:
                return False
            
            sender_domain = sender.split('@')[1].lower()
            
            for url in urls:
                if sender_domain in url.lower():
                    return False
            
            return True
        except Exception as e:
            logger.warning(f"Error checking domain mismatch: {e}")
            return False
    
    def _is_suspicious_sender(self, sender: str) -> bool:
        """Check if sender looks suspicious"""
        suspicious_patterns = ['admin', 'support', 'noreply', 'notification',
                              'no-reply', 'donotreply', 'mailer']
        sender_lower = sender.lower()
        
        return any(pattern in sender_lower for pattern in suspicious_patterns)
    
    def _count_caps_ratio(self, text: str) -> float:
        """Calculate ratio of uppercase letters"""
        if len(text) == 0:
            return 0
        caps = sum(1 for c in text if c.isupper())
        return caps / len(text)
    
    def _check_suspicious_tld(self, url: str) -> bool:
        """Check for suspicious top-level domains"""
        suspicious_tlds = ['.tk', '.ml', '.ga', '.cf', '.top', '.pw', '.xyz']
        url_lower = url.lower()
        return any(tld in url_lower for tld in suspicious_tlds)
