# Phishing Detector - Tests

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import unittest
from src.utils.email_parser import EmailParser, URLAnalyzer
from src.utils.feature_extractor import FeatureExtractor
from src.models.detector import PhishingDetector
from src.alerts.alert_manager import AlertManager, AlertSeverity

class TestEmailParser(unittest.TestCase):
    """Test email parser functionality"""
    
    def setUp(self):
        self.parser = EmailParser()
    
    def test_email_validation(self):
        """Test email validation"""
        self.assertTrue(self.parser.validate_email('test@example.com'))
        self.assertFalse(self.parser.validate_email('invalid-email'))
        self.assertFalse(self.parser.validate_email('test@'))
    
    def test_url_extraction(self):
        """Test URL extraction from text"""
        text = "Visit https://example.com or http://test.org for more info"
        urls = self.parser._extract_urls(text)
        self.assertEqual(len(urls), 2)
    
    def test_suspicious_sender_detection(self):
        """Test suspicious sender detection"""
        suspicious = 'admin@gmail.com'
        legitimate = 'john.doe@company.com'
        
        self.assertTrue(self.parser._check_suspicious_sender(suspicious))
        self.assertFalse(self.parser._check_suspicious_sender(legitimate))

class TestURLAnalyzer(unittest.TestCase):
    """Test URL analyzer functionality"""
    
    def setUp(self):
        self.analyzer = URLAnalyzer()
    
    def test_ip_detection(self):
        """Test IP address detection"""
        ip_url = "http://192.168.1.1/"
        domain_url = "http://example.com/"
        
        ip_analysis = self.analyzer.analyze_url(ip_url)
        domain_analysis = self.analyzer.analyze_url(domain_url)
        
        self.assertTrue(ip_analysis.get('has_ip_address'))
        self.assertFalse(domain_analysis.get('has_ip_address'))
    
    def test_https_detection(self):
        """Test HTTPS detection"""
        secure_url = "https://example.com/"
        insecure_url = "http://example.com/"
        
        secure = self.analyzer.analyze_url(secure_url)
        insecure = self.analyzer.analyze_url(insecure_url)
        
        self.assertTrue(secure.get('uses_https'))
        self.assertFalse(insecure.get('uses_https'))
    
    def test_suspicious_pattern(self):
        """Test suspicious pattern detection"""
        suspicious_url = "http://verify-paypal.com/"
        normal_url = "https://example.com/"
        
        suspicious = self.analyzer.analyze_url(suspicious_url)
        normal = self.analyzer.analyze_url(normal_url)
        
        self.assertTrue(suspicious.get('has_suspicious_pattern'))
        self.assertFalse(normal.get('has_suspicious_pattern'))

class TestFeatureExtractor(unittest.TestCase):
    """Test feature extraction"""
    
    def setUp(self):
        self.extractor = FeatureExtractor()
    
    def test_phishing_email_features(self):
        """Test feature extraction from phishing email"""
        phishing_email = """
        Subject: URGENT: Verify Account
        
        Click here immediately to verify your account or it will be suspended!
        Your account has been compromised. Update your password now.
        """
        
        features = self.extractor.extract_email_features(phishing_email)
        
        self.assertGreater(features['urgent_words'], 0)
        self.assertGreater(features['action_words'], 0)
    
    def test_legitimate_email_features(self):
        """Test feature extraction from legitimate email"""
        legitimate_email = """
        Subject: Meeting Tomorrow
        
        Hi, I wanted to schedule a meeting for tomorrow at 2pm.
        Please let me know if that works for you.
        """
        
        features = self.extractor.extract_email_features(legitimate_email)
        
        self.assertEqual(features['urgent_words'], 0)
        self.assertLess(features['action_words'], 2)

class TestAlertManager(unittest.TestCase):
    """Test alert management"""
    
    def setUp(self):
        self.manager = AlertManager()
    
    def test_create_alert(self):
        """Test alert creation"""
        alert = self.manager.create_alert(
            AlertSeverity.CRITICAL,
            "Phishing detected",
            {'url': 'http://phishing.com'}
        )
        
        self.assertIsNotNone(alert.alert_id)
        self.assertEqual(alert.severity, AlertSeverity.CRITICAL)
    
    def test_mark_alert_read(self):
        """Test marking alert as read"""
        alert = self.manager.create_alert(
            AlertSeverity.HIGH,
            "Test alert",
            {}
        )
        
        self.manager.mark_alert_as_read(alert.alert_id)
        retrieved = self.manager.get_alert(alert.alert_id)
        
        self.assertTrue(retrieved.read)
    
    def test_get_all_alerts(self):
        """Test retrieving all alerts"""
        for i in range(3):
            self.manager.create_alert(
                AlertSeverity.MEDIUM,
                f"Alert {i}",
                {}
            )
        
        alerts = self.manager.get_all_alerts()
        self.assertEqual(len(alerts), 3)
    
    def test_alert_stats(self):
        """Test alert statistics"""
        self.manager.create_alert(AlertSeverity.CRITICAL, "Test", {})
        self.manager.create_alert(AlertSeverity.HIGH, "Test", {})
        self.manager.create_alert(AlertSeverity.MEDIUM, "Test", {})
        
        stats = self.manager.get_stats()
        
        self.assertEqual(stats['total_active'], 3)
        self.assertEqual(stats['by_severity']['critical'], 1)
        self.assertEqual(stats['by_severity']['high'], 1)
        self.assertEqual(stats['by_severity']['medium'], 1)

class TestPhishingDetector(unittest.TestCase):
    """Test phishing detector model"""
    
    def test_detector_initialization(self):
        """Test detector initialization"""
        detector = PhishingDetector()
        detector.create_model()
        
        self.assertIsNotNone(detector.model)
        self.assertIsNotNone(detector.vectorizer)

if __name__ == '__main__':
    unittest.main()
