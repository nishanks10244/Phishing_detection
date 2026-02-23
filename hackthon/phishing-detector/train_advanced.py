#!/usr/bin/env python
"""
PhishGuard - Advanced Model Training Script
Trains XGBoost/Gradient Boosting models with enhanced features
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report, roc_auc_score
import sys
import os
import logging

sys.path.insert(0, os.path.dirname(__file__))

from src.models.detector import PhishingDetector
from src.utils.feature_extractor import FeatureExtractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enhanced training dataset
TRAINING_DATA = [
    # Phishing emails
    {
        'text': 'verify your account immediately due to unusual activity click here to confirm your identity urgent action required',
        'is_phishing': 1
    },
    {
        'text': 'we noticed suspicious activity please update your password now within 24 hours or account will be suspended',
        'is_phishing': 1
    },
    {
        'text': 'click here to claim your prize 1 million dollars waiting verify account credentials PayPal urgent',
        'is_phishing': 1
    },
    {
        'text': 'your paypal account requires immediate verification limited time offer confirm billing information now',
        'is_phishing': 1
    },
    {
        'text': 'amazon urgent action needed suspicious login attempt reset password immediately http://verify-amazon.tk',
        'is_phishing': 1
    },
    {
        'text': 'bank alert unauthorized transactions detected click to verify account 192.168.1.1 important urgent',
        'is_phishing': 1
    },
    {
        'text': 'microsoft security alert unusual activity confirm identity immediately action required http://secure-verify-microsoft.xyz',
        'is_phishing': 1
    },
    {
        'text': 'apple id verification needed confirm password immediately reactivate account http://bit.ly/verify-apple',
        'is_phishing': 1
    },
    
    # Legitimate emails
    {
        'text': 'Your monthly statement is ready. Please click below to download your PDF statement from our secure portal. Banking services.',
        'is_phishing': 0
    },
    {
        'text': 'Hi John, Meeting scheduled for tomorrow at 2pm. Please confirm your attendance. Looking forward to seeing you then.',
        'is_phishing': 0
    },
    {
        'text': 'Thank you for your purchase. Your order confirmation and tracking information has been sent to your email.',
        'is_phishing': 0
    },
    {
        'text': 'Welcome to our service. Your account has been created successfully. You can now log in with your credentials.',
        'is_phishing': 0
    },
    {
        'text': 'Project update: Q3 results are ready for review. Please access our secure dashboard to view detailed analytics.',
        'is_phishing': 0
    },
    {
        'text': 'Hello team, Attached is the meeting minutes from today. Please review and provide feedback by Friday.',
        'is_phishing': 0
    },
    {
        'text': 'Your quarterly health insurance coverage is now active. Find plan details and ID card in your member portal.',
        'is_phishing': 0
    },
    {
        'text': 'New comment on your blog post. Click here to view and respond to reader feedback on your article.',
        'is_phishing': 0
    },
]

def train_model():
    """Train the advanced phishing detection model"""
    
    print("\n" + "="*70)
    print(" PhishGuard - Advanced ML Model Training")
    print("="*70 + "\n")
    
    # Create detector with optional XGBoost
    print("📦 Initializing model...")
    detector = PhishingDetector()
    detector.create_model()
    
    print(f"✓ Using {'XGBoost' if detector.use_xgboost else 'GradientBoosting'} classifier")
    print(f"✓ TF-IDF vectorizer: max 1000 features, bigrams enabled")
    
    # Extract features
    feature_extractor = FeatureExtractor()
    
    X_text = []
    X_features = []
    y = []
    
    print(f"\n📊 Processing {len(TRAINING_DATA)} training samples...")
    
    for i, sample in enumerate(TRAINING_DATA):
        try:
            text = sample['text']
            label = sample['is_phishing']
            
            # Extract comprehensive features
            features = {
                'subject_length': len(text.split()[0]) if text.split() else 0,
                'body_length': len(text),
                'url_count': text.count('http') + text.count('http://'),
                'urgent_words': sum(1 for w in ['urgent', 'immediate', 'confirm', 'verify', 'click', 'action', 'limited', 'expire'] if w in text.lower()),
                'financial_words': sum(1 for w in ['payment', 'account', 'credit', 'verify', 'bank', 'billing', 'transaction'] if w in text.lower()),
                'personal_words': sum(1 for w in ['password', 'identity', 'ssn', 'security number'] if w in text.lower()),
                'action_words': sum(1 for w in ['click', 'download', 'update', 'reset', 'confirm', 'verify'] if w in text.lower()),
                'urgency_score': min(text.count('!') / 10, 1.0),
            }
            
            # Build feature vector matching detector expectations
            feature_vector = [
                features['subject_length'],
                features['body_length'],
                features['url_count'],
                features['urgent_words'],
                features['financial_words'],
                features['personal_words'],
                features['action_words'],
                features['urgency_score'],
                0,  # url_risk_score placeholder
                0,  # suspicious_urls placeholder
                0,  # sender_domain_mismatch placeholder
                int('admin' in text.lower() or 'support' in text.lower()),
                0,  # excessive_links placeholder
                int(len(text) < 50),
                int(text.count('!') > 2),
                0,  # unusual_capitals placeholder
            ]
            
            X_text.append(text)
            X_features.append(feature_vector)
            y.append(label)
            
            status = "🚨 PHISHING" if label == 1 else "✅ LEGITIMATE"
            print(f"  [{i+1:2d}/{len(TRAINING_DATA)}] {status}: {text[:50]}...")
            
        except Exception as e:
            logger.error(f"Error processing sample {i}: {e}")
            continue
    
    # Prepare data
    X_features = np.array(X_features)
    y = np.array(y)
    
    print(f"\n✓ Processed {len(X_text)} samples")
    print(f"  - Phishing: {sum(y)} samples")
    print(f"  - Legitimate: {len(y) - sum(y)} samples")
    
    # Split data
    print("\n🔀 Splitting data (80% train, 20% test)...")
    X_text_train, X_text_test, X_feat_train, X_feat_test, y_train, y_test = train_test_split(
        X_text, X_features, y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )
    
    # Train model
    print(f"\n⏳ Training model...")
    success = detector.train(X_text_train, X_feat_train, y_train)
    
    if not success:
        print("❌ Model training failed!")
        return False
    
    print("✓ Model training completed")
    
    # Evaluate
    print("\n📈 Evaluating model performance...")
    eval_results = detector.evaluate(X_text_test, X_feat_test, y_test)
    
    if eval_results:
        print("\n" + "-"*50)
        print("Performance Metrics:")
        print("-"*50)
        print(f"Precision:     {eval_results.get('precision', 0):.3f}")
        print(f"Recall:        {eval_results.get('recall', 0):.3f}")
        print(f"F1-Score:      {eval_results.get('f1', 0):.3f}")
        print(f"ROC-AUC:       {eval_results.get('roc_auc', 0):.3f}")
        print("-"*50)
        
        cm = eval_results.get('confusion_matrix', [])
        if cm:
            print("\nConfusion Matrix:")
            print(f"True Negatives:  {cm[0][0]}")
            print(f"False Positives: {cm[0][1]}")
            print(f"False Negatives: {cm[1][0]}")
            print(f"True Positives:  {cm[1][1]}")
    
    # Save model
    model_dir = os.path.join(os.path.dirname(__file__), 'src', 'models')
    os.makedirs(model_dir, exist_ok=True)
    
    model_path = os.path.join(model_dir, 'phishing_detector.pkl')
    vectorizer_path = os.path.join(model_dir, 'vectorizer.pkl')
    
    detector.save_model(model_path)
    detector.save_vectorizer(vectorizer_path)
    
    print(f"\n✓ Model saved to {model_path}")
    print(f"✓ Vectorizer saved to {vectorizer_path}")
    
    # Test predictions
    print("\n" + "="*70)
    print(" Testing Predictions on New Data")
    print("="*70)
    
    test_cases = [
        ("URGENT: Verify your account immediately or it will be suspended. Click here now!", 1),
        ("Hi, just wanted to schedule a meeting for next week. Does Thursday work?", 0),
        ("Your PayPal account requires immediate action. Confirm your password now.", 1),
        ("Project update: Q3 results are ready for review in the system.", 0),
        ("CRITICAL: Unusual activity detected. Verify identity immediately via link.", 1),
    ]
    
    for test_text, expected in test_cases:
        features_counts = {
            'urgent': sum(1 for w in ['urgent', 'immediate'] if w in test_text.lower()),
            'action': sum(1 for w in ['click', 'confirm', 'verify'] if w in test_text.lower()),
        }
        
        feature_vector = np.array([
            0, len(test_text), test_text.count('http'),
            features_counts['urgent'],
            sum(1 for w in ['paypal', 'account'] if w in test_text.lower()),
            sum(1 for w in ['password'] if w in test_text.lower()),
            features_counts['action'],
            min(test_text.count('!') / 10, 1.0),
            0, 0, 0, 0, 0, 0, 0, 0
        ])
        
        prediction, confidence = detector.predict(test_text, feature_vector)
        is_phishing = prediction == 1
        
        expected_str = "PHISHING" if expected == 1 else "LEGITIMATE"
        result_str = "PHISHING" if is_phishing else "LEGITIMATE"
        match = "✓" if is_phishing == (expected == 1) else "✗"
        
        print(f"\n{match} Text: {test_text[:50]}...")
        print(f"  Expected: {expected_str} | Got: {result_str} ({confidence:.1%})")
    
    print("\n" + "="*70)
    print(" Training Complete!")
    print("="*70)
    print("\nNext steps:")
    print("1. Start the server: python main.py")
    print("2. Open: http://localhost:5000")
    print("3. Load Chrome extension from chrome-extension/")
    print("4. Start scanning emails and URLs!")
    
    return True

if __name__ == '__main__':
    try:
        success = train_model()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.exception("Fatal error during training")
        sys.exit(1)
