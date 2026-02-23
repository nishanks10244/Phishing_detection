import logging
import os
from flask import Flask, jsonify
from flask_cors import CORS
from src.config import config
from src.models.detector import PhishingDetector
from src.api.routes import init_api
from src.alerts.alert_manager import AlertManager

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app(config_name: str = 'development'):
    """Factory function to create Flask app"""
    
    # Create Flask app
    app = Flask(__name__, static_folder='frontend', static_url_path='')
    
    # Load configuration
    env_config = config.get(config_name, config['development'])
    app.config.from_object(env_config)
    
    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Initialize components
    phishing_detector = PhishingDetector()
    alert_manager = AlertManager()
    
    # Register API routes
    init_api(app, phishing_detector)
    
    # Store in app context
    app.phishing_detector = phishing_detector
    app.alert_manager = alert_manager
    
    # Serve frontend
    @app.route('/')
    def index():
        frontend_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'index.html')
        with open(frontend_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    # Basic health check route
    @app.route('/status')
    def status():
        return jsonify({
            'status': 'running',
            'component': 'Phishing Detection System',
            'version': '1.0.0'
        })
    
    logger.info(f"App created with config: {config_name}")
    
    return app, phishing_detector, alert_manager

if __name__ == '__main__':
    app, detector, alerts = create_app('development')
    app.run(host='0.0.0.0', port=5000, debug=True)
