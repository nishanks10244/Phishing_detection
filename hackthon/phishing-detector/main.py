#!/usr/bin/env python
"""Main entry point for the Phishing Detection System"""

import sys
import os
import logging

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from src.app import create_app

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('phishing_detector.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Run the application"""
    logger.info("Starting Phishing Detection System")
    
    try:
        # Create app
        app, detector, alert_manager = create_app('development')
        
        logger.info("Application created successfully")
        logger.info("Starting server on http://0.0.0.0:5000")
        
        # Run Flask app
        app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
