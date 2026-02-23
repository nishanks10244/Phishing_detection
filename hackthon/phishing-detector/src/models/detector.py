import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import joblib
import logging
from typing import Tuple, Dict, Any
import pickle
import os

logger = logging.getLogger(__name__)

# Try to import XGBoost, fall back to GradientBoosting if not available
try:
    import xgboost as xgb
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False
    logger.warning("XGBoost not available, using GradientBoosting")

class PhishingDetector:
    """ML-based phishing detection model with XGBoost or Gradient Boosting"""
    
    def __init__(self, model_path: str = None, vectorizer_path: str = None):
        self.model = None
        self.vectorizer = None
        self.scaler = StandardScaler()
        self.feature_importance = {}
        self.use_xgboost = HAS_XGBOOST
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        if vectorizer_path and os.path.exists(vectorizer_path):
            self.load_vectorizer(vectorizer_path)
    
    def create_model(self):
        """Create a new phishing detection model"""
        if self.use_xgboost:
            try:
                self.model = xgb.XGBClassifier(
                    n_estimators=100,
                    learning_rate=0.1,
                    max_depth=5,
                    random_state=42,
                    tree_method='hist',
                    device='cpu',
                    eval_metric='logloss'
                )
                logger.info("Using XGBoost model")
            except Exception as e:
                logger.warning(f"XGBoost initialization failed: {e}, using GradientBoosting")
                self.use_xgboost = False
                self.model = GradientBoostingClassifier(
                    n_estimators=100,
                    learning_rate=0.1,
                    max_depth=5,
                    random_state=42,
                    verbose=0
                )
        else:
            self.model = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42,
                verbose=0
            )
            logger.info("Using GradientBoosting model")
        
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            min_df=2,
            max_df=0.95,
            ngram_range=(1, 2),
            lowercase=True,
            stop_words='english'
        )
        
        return self.model, self.vectorizer
    
    def train(self, X_text: list, X_features: np.ndarray, y: np.ndarray):
        """Train the model on labeled data"""
        try:
            logger.info("Starting model training...")
            
            # Vectorize text features
            X_text_vectorized = self.vectorizer.fit_transform(X_text)
            X_text_vectorized = X_text_vectorized.toarray()
            
            # Combine with other features
            X_combined = np.hstack([X_text_vectorized, X_features])
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X_combined)
            
            # Train model
            self.model.fit(X_scaled, y)
            
            logger.info("Model training completed successfully")
            return True
        except Exception as e:
            logger.error(f"Error training model: {e}")
            return False
    
    def predict(self, X_text: str, X_features: np.ndarray) -> Tuple[int, float]:
        """Predict if email/URL is phishing"""
        try:
            if self.model is None or self.vectorizer is None:
                logger.warning("Model not trained or loaded")
                return 0, 0.5
            
            # Vectorize text
            X_text_vectorized = self.vectorizer.transform([X_text])
            X_text_vectorized = X_text_vectorized.toarray()
            
            # Combine with features
            X_combined = np.hstack([X_text_vectorized, X_features.reshape(1, -1)])
            
            # Scale
            X_scaled = self.scaler.transform(X_combined)
            
            # Predict
            prediction = self.model.predict(X_scaled)[0]
            probability = self.model.predict_proba(X_scaled)[0]
            
            # Phishing confidence (probability of class 1)
            phishing_confidence = probability[1]
            
            return int(prediction), phishing_confidence
        except Exception as e:
            logger.error(f"Error making prediction: {e}")
            return 0, 0.5
    
    def predict_proba(self, X_text: str, X_features: np.ndarray) -> Dict[str, float]:
        """Get probability distribution"""
        try:
            if self.model is None:
                return {'legitimate': 0.5, 'phishing': 0.5}
            
            X_text_vectorized = self.vectorizer.transform([X_text])
            X_text_vectorized = X_text_vectorized.toarray()
            X_combined = np.hstack([X_text_vectorized, X_features.reshape(1, -1)])
            X_scaled = self.scaler.transform(X_combined)
            
            proba = self.model.predict_proba(X_scaled)[0]
            
            return {
                'legitimate': float(proba[0]),
                'phishing': float(proba[1])
            }
        except Exception as e:
            logger.error(f"Error getting probabilities: {e}")
            return {'legitimate': 0.5, 'phishing': 0.5}
    
    def save_model(self, model_path: str):
        """Save trained model"""
        try:
            joblib.dump(self.model, model_path)
            logger.info(f"Model saved to {model_path}")
        except Exception as e:
            logger.error(f"Error saving model: {e}")
    
    def load_model(self, model_path: str):
        """Load trained model"""
        try:
            self.model = joblib.load(model_path)
            logger.info(f"Model loaded from {model_path}")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
    
    def save_vectorizer(self, vectorizer_path: str):
        """Save vectorizer"""
        try:
            joblib.dump(self.vectorizer, vectorizer_path)
            logger.info(f"Vectorizer saved to {vectorizer_path}")
        except Exception as e:
            logger.error(f"Error saving vectorizer: {e}")
    
    def load_vectorizer(self, vectorizer_path: str):
        """Load vectorizer"""
        try:
            self.vectorizer = joblib.load(vectorizer_path)
            logger.info(f"Vectorizer loaded from {vectorizer_path}")
        except Exception as e:
            logger.error(f"Error loading vectorizer: {e}")
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance from model"""
        try:
            if hasattr(self.model, 'feature_importances_'):
                importances = self.model.feature_importances_
                return {f'feature_{i}': imp for i, imp in enumerate(importances)}
        except Exception as e:
            logger.error(f"Error getting feature importance: {e}")
        
        return {}
    
    def evaluate(self, X_text: list, X_features: np.ndarray, y: np.ndarray) -> Dict:
        """Evaluate model performance"""
        try:
            from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score, roc_auc_score
            
            X_text_vectorized = self.vectorizer.transform(X_text)
            X_text_vectorized = X_text_vectorized.toarray()
            X_combined = np.hstack([X_text_vectorized, X_features])
            X_scaled = self.scaler.transform(X_combined)
            
            predictions = self.model.predict(X_scaled)
            probabilities = self.model.predict_proba(X_scaled)[:, 1]
            
            cm = confusion_matrix(y, predictions)
            
            return {
                'confusion_matrix': cm.tolist(),
                'true_negatives': int(cm[0, 0]),
                'false_positives': int(cm[0, 1]),
                'false_negatives': int(cm[1, 0]),
                'true_positives': int(cm[1, 1]),
                'precision': float(precision_score(y, predictions)),
                'recall': float(recall_score(y, predictions)),
                'f1': float(f1_score(y, predictions)),
                'roc_auc': float(roc_auc_score(y, probabilities))
            }
        except Exception as e:
            logger.error(f"Error evaluating model: {e}")
            return {}
