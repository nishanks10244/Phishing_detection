import logging
from datetime import datetime
from flask import Blueprint, request, jsonify
from src.models.detector import PhishingDetector
from src.utils.feature_extractor import FeatureExtractor
from src.utils.email_parser import EmailParser

logger = logging.getLogger(__name__)

# Create blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# Initialize components
detector = None
feature_extractor = FeatureExtractor()
email_parser = EmailParser()

def init_api(app, phishing_detector: PhishingDetector):
    """Initialize API with detector instance"""
    global detector
    detector = phishing_detector
    app.register_blueprint(api_bp)

@api_bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'model_loaded': detector is not None and detector.model is not None
    }), 200

@api_bp.route('/scan/email', methods=['POST'])
def scan_email():
    """Scan email for phishing"""
    try:
        data = request.get_json()
        
        if not data or 'email_content' not in data:
            return jsonify({'error': 'Missing email_content'}), 400
        
        email_content = data['email_content']
        
        # Parse email
        parsed = email_parser.parse_email(email_content)
        
        # Extract features
        features = feature_extractor.extract_email_features(email_content)
        
        # Prepare feature vector for model
        feature_vector = [
            features['subject_length'],
            features['body_length'],
            features['url_count'],
            features['urgent_words'],
            features['financial_words'],
            features['personal_words'],
            features['action_words'],
            features['urgency_score'],
            float(features['url_risk_score']),
            features['suspicious_urls'],
            int(features['sender_domain_mismatch']),
            int(features['sender_suspicious']),
            int(features['excessive_links']),
            int(features['short_body']),
            int(features['many_exclamations']),
            int(features['unusual_capitals']),
        ]
        
        import numpy as np
        feature_vector = np.array(feature_vector)
        
        # Make prediction
        prediction, confidence = detector.predict(
            features['full_text'],
            feature_vector
        )
        
        is_phishing = prediction == 1
        
        return jsonify({
            'is_phishing': is_phishing,
            'confidence': float(confidence),
            'risk_level': _get_risk_level(confidence),
            'details': {
                'subject': parsed.get('subject', ''),
                'sender': parsed.get('sender', ''),
                'url_count': features['url_count'],
                'suspicious_urls': features['suspicious_urls'],
                'urls': parsed.get('urls', [])
            },
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error scanning email: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/scan/url', methods=['POST'])
def scan_url():
    """Scan URL for phishing"""
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({'error': 'Missing url'}), 400
        
        url = data['url']
        
        # Extract URL features
        features = feature_extractor.extract_url_features(url)
        
        # Create feature vector for model prediction
        feature_vector = [
            features['url_length'],
            features['subdomain_count'],
            int(features['has_ip']),
            int(features['has_suspicious_pattern']),
            int(not features['uses_https']),
            int(features['has_port']),
            int(features['suspicious_tld']),
            0,  # Padding to match email features
            0, 0, 0, 0, 0, 0, 0, 0
        ]
        
        import numpy as np
        feature_vector = np.array(feature_vector)
        
        # Make prediction (using URL as text)
        prediction, confidence = detector.predict(url, feature_vector)
        
        is_phishing = prediction == 1
        
        return jsonify({
            'url': url,
            'is_phishing': is_phishing,
            'confidence': float(confidence),
            'risk_level': _get_risk_level(confidence),
            'details': {
                'domain': features['domain'],
                'has_ip': features['has_ip'],
                'uses_https': features['uses_https'],
                'url_length': features['url_length'],
                'suspicious_pattern': features['has_suspicious_pattern'],
                'suspicious_tld': features['suspicious_tld']
            },
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error scanning URL: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/scan/batch', methods=['POST'])
def scan_batch():
    """Scan multiple emails/URLs in batch"""
    try:
        data = request.get_json()
        
        if not data or 'items' not in data:
            return jsonify({'error': 'Missing items'}), 400
        
        items = data['items']
        results = []
        
        for item in items:
            try:
                if 'email_content' in item:
                    # Scan as email
                    parsed = email_parser.parse_email(item['email_content'])
                    features = feature_extractor.extract_email_features(item['email_content'])
                    
                    feature_vector = [
                        features['subject_length'],
                        features['body_length'],
                        features['url_count'],
                        features['urgent_words'],
                        features['financial_words'],
                        features['personal_words'],
                        features['action_words'],
                        features['urgency_score'],
                        float(features['url_risk_score']),
                        features['suspicious_urls'],
                        int(features['sender_domain_mismatch']),
                        int(features['sender_suspicious']),
                        int(features['excessive_links']),
                        int(features['short_body']),
                        int(features['many_exclamations']),
                        int(features['unusual_capitals']),
                    ]
                    
                    import numpy as np
                    feature_vector = np.array(feature_vector)
                    
                    prediction, confidence = detector.predict(
                        features['full_text'],
                        feature_vector
                    )
                    
                    results.append({
                        'type': 'email',
                        'is_phishing': prediction == 1,
                        'confidence': float(confidence),
                        'risk_level': _get_risk_level(confidence)
                    })
                    
                elif 'url' in item:
                    # Scan as URL
                    features = feature_extractor.extract_url_features(item['url'])
                    
                    feature_vector = [
                        features['url_length'],
                        features['subdomain_count'],
                        int(features['has_ip']),
                        int(features['has_suspicious_pattern']),
                        int(not features['uses_https']),
                        int(features['has_port']),
                        int(features['suspicious_tld']),
                        0, 0, 0, 0, 0, 0, 0, 0, 0
                    ]
                    
                    import numpy as np
                    feature_vector = np.array(feature_vector)
                    
                    prediction, confidence = detector.predict(item['url'], feature_vector)
                    
                    results.append({
                        'type': 'url',
                        'url': item['url'],
                        'is_phishing': prediction == 1,
                        'confidence': float(confidence),
                        'risk_level': _get_risk_level(confidence)
                    })
            except Exception as e:
                logger.warning(f"Error processing item: {e}")
                results.append({'error': str(e)})
        
        return jsonify({
            'total': len(items),
            'results': results,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error in batch scan: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/model/info', methods=['GET'])
def model_info():
    """Get model information"""
    try:
        return jsonify({
            'model_loaded': detector is not None and detector.model is not None,
            'vectorizer_loaded': detector is not None and detector.vectorizer is not None,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        return jsonify({'error': str(e)}), 500

def _get_risk_level(confidence: float) -> str:
    """Determine risk level based on confidence"""
    if confidence >= 0.8:
        return 'critical'
    elif confidence >= 0.6:
        return 'high'
    elif confidence >= 0.4:
        return 'medium'
    else:
        return 'low'
