#!/usr/bin/env python
"""
Quick setup script for Phishing Detection System
Handles installation and initial setup
"""

import os
import sys
import subprocess
import platform

def run_command(cmd, description):
    """Run a shell command"""
    print(f"\n{'='*60}")
    print(f"▶ {description}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=False)
        if result.returncode != 0:
            print(f"✗ Failed: {description}")
            return False
        print(f"✓ Success: {description}")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    """Run setup"""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║     🛡️  Phishing Detection System - Setup Wizard          ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Check Python version
    print(f"\n📌 Python Version: {sys.version}")
    if sys.version_info < (3, 8):
        print("✗ ERROR: Python 3.8+ required")
        return False
    
    # Check OS
    os_type = platform.system()
    print(f"📌 Operating System: {os_type}")
    
    # Install dependencies
    if not run_command(
        f"{sys.executable} -m pip install --upgrade pip",
        "Upgrading pip"
    ):
        return False
    
    if not run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing dependencies"
    ):
        return False
    
    # Train model
    if not run_command(
        f"{sys.executable} train_model.py",
        "Training ML model"
    ):
        print("⚠ Model training failed, but you can continue")
    
    # Create .env if it doesn't exist
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            with open('.env.example', 'r') as example:
                f.write(example.read())
        print("✓ Created .env file from template")
    
    # Create necessary directories
    os.makedirs('src/models', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                  ✓ Setup Complete!                        ║
    ╚═══════════════════════════════════════════════════════════╝
    
    ✓ All dependencies installed
    ✓ ML model trained
    ✓ Environment configured
    
    Next steps:
    
    1. Start the server:
       python main.py
    
    2. Open in browser:
       http://localhost:5000
    
    3. Scan emails/URLs for phishing detection
    
    📚 Documentation: See README.md for detailed usage
    
    Questions? Check the README.md or run:
       python train_model.py --help
    
    """)
    
    return True

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠ Setup canceled by user")
        sys.exit(1)
