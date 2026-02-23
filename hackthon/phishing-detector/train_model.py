import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from src.models.detector import PhishingDetector
from src.utils.feature_extractor import FeatureExtractor

# Sample training data
# In production, use real phishing/legitimate email datasets
TRAINING_DATA = [
    {
        'text': 'verify your account immediately due to unusual activity click here to confirm your identity',
        'is_phishing': 1
    },
    {
        'text': 'we noticed unusual activity update your password now payment verification required',
        'is_phishing': 1
    },
    {
        'text': 'Your monthly statement is ready. Click the link to download your PDF statement from our secure portal.',
        'is_phishing': 0
    },
    {
        'text': 'Meeting scheduled for tomorrow at 2pm. Please confirm your attendance.',
        'is_phishing': 0
    },
    {
        'text': 'URGENT: Your account has been compromised! Act now - click here to secure your account',
        'is_phishing': 1
    },
    {
        'text': 'Thank you for your purchase. Your order confirmation is attached.',
        'is_phishing': 0
    },
    {
        'text': 'Please update your credit card information before your subscription expires',
        'is_phishing': 1
    },
    {
        'text': 'Hello, your quarterly report has been prepared and is available in your dashboard.',
        'is_phishing': 0
    },
    {
        'text': 'VERIFY PAYPAL ACCOUNT - click link immediately or your account will be suspended',
        'is_phishing': 1
    },
    {
        'text': 'Project status update: Team will be working remotely on Friday.',
        'is_phishing': 0
    },
]

def train_model():
    """Train the phishing detection model"""
    
    print("=" * 60)
    print("Phishing Detection Model Training")
    print("=" * 60)
    
    # Create detector
    detector = PhishingDetector()
    detector.create_model()
    
    # Extract features
    feature_extractor = FeatureExtractor()
    
    X_text = []
    X_features = []
    y = []
    
    print(f"\nProcessing {len(TRAINING_DATA)} training samples...")
    
    for i, sample in enumerate(TRAINING_DATA):
        try:
            text = sample['text']
            label = sample['is_phishing']
            
            # Extract basic features
            features = {
                'subject_length': len(text.split()[0]) if text.split() else 0,
                'body_length': len(text),
                'url_count': text.count('http'),
                'urgent_words': sum(1 for w in ['urgent', 'immediate', 'confirm', 'verify', 'click'] if w in text.lower()),
                'financial_words': sum(1 for w in ['payment', 'account', 'credit', 'verify'] if w in text.lower()),
                'personal_words': sum(1 for w in ['password', 'identity'] if w in text.lower()),
                'action_words': sum(1 for w in ['click', 'download', 'update'] if w in text.lower()),
                'urgency_score': min(text.count('!') / 10, 1.0),
            }
            
            feature_vector = [
                features['subject_length'],
                features['body_length'],
                features['url_count'],
                features['urgent_words'],
                features['financial_words'],
                features['personal_words'],
                features['action_words'],
                features['urgency_score'],
                0,  # url_risk_score
                0,  # suspicious_urls
                0,  # sender_domain_mismatch
                int('admin' in text.lower() or 'support' in text.lower()),
                0,  # excessive_links
                int(len(text) < 50),
                int(text.count('!') > 2),
                0,  # unusual_capitals
            ]
            
            X_text.append(text)
            X_features.append(feature_vector)
            y.append(label)
            
            status = "PHISHING" if label == 1 else "LEGITIMATE"
            print(f"  [{i+1}/{len(TRAINING_DATA)}] {status}: {text[:50]}...")
            
        except Exception as e:
            print(f"  ERROR processing sample {i}: {e}")
            continue
    
    # Convert to numpy arrays
    X_features = np.array(X_features)
    y = np.array(y)
    
    print(f"\n✓ Processed {len(X_text)} samples")
    print(f"  Phishing samples: {sum(y)}")
    print(f"  Legitimate samples: {len(y) - sum(y)}")
    
    # Train model
    print("\nTraining model...")
    detector.train(X_text, X_features, y)
    
    print("✓ Model training completed")
    
    # Evaluate
    print("\nEvaluating model...")
    eval_results = detector.evaluate(X_text, X_features, y)
    
    if eval_results:
        print(f"  Precision: {eval_results.get('precision', 0):.3f}")
        print(f"  Recall: {eval_results.get('recall', 0):.3f}")
        print(f"  F1-Score: {eval_results.get('f1', 0):.3f}")
        print(f"  ROC-AUC: {eval_results.get('roc_auc', 0):.3f}")
    
    # Save model
    model_path = os.path.join(os.path.dirname(__file__), 'src', 'models', 'phishing_detector.pkl')
    vectorizer_path = os.path.join(os.path.dirname(__file__), 'src', 'models', 'vectorizer.pkl')
    
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    
    detector.save_model(model_path)
    detector.save_vectorizer(vectorizer_path)
    
    print(f"\n✓ Model saved to {model_path}")
    print(f"✓ Vectorizer saved to {vectorizer_path}")
    
    # Test predictions
    print("\n" + "=" * 60)
    print("Testing Predictions")
    print("=" * 60)
    
    test_cases = [
        "URGENT: Verify your account immediately or it will be suspended. Click here now!",
        "Hi, just wanted to schedule a meeting for next week. Does Thursday work?",
        "Your PayPal account requires immediate action. Confirm your password now.",
        "Project update: Q3 results are ready for review in the system.",
    ]
    
    for test_text in test_cases:
        features_dict = {
            'subject_length': 0,
            'body_length': len(test_text),
            'url_count': test_text.count('http'),
            'urgent_words': sum(1 for w in ['urgent', 'immediate', 'confirm', 'verify'] if w in test_text.lower()),
            'financial_words': sum(1 for w in ['payment', 'account'] if w in test_text.lower()),
            'personal_words': sum(1 for w in ['password'] if w in test_text.lower()),
            'action_words': sum(1 for w in ['click', 'confirm'] if w in test_text.lower()),
            'urgency_score': min(test_text.count('!') / 10, 1.0),
        }
        
        feature_vector = np.array([
            0, len(test_text), 0,
            features_dict['urgent_words'],
            features_dict['financial_words'],
            features_dict['personal_words'],
            features_dict['action_words'],
            features_dict['urgency_score'],
            0, 0, 0, 0, 0, 0, 0, 0
        ])
        
        prediction, confidence = detector.predict(test_text, feature_vector)
        result = "PHISHING" if prediction == 1 else "LEGITIMATE"
        
        print(f"\nText: {test_text}")
        print(f"Result: {result} (Confidence: {confidence:.1%})")
    
    print("\n" + "=" * 60)
    print("Training complete!")
    print("=" * 60)

if __name__ == '__main__':
    train_model()
