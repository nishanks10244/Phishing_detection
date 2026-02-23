# Quick reference for running the Phishing Detection System

## Installation (One-time)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Train the ML model
python train_model.py

# Expected output:
# ✓ Model training completed
# ✓ Model saved to src/models/phishing_detector.pkl
```

## Running the System

```bash
# Start the server
python main.py

# Output should show:
# Starting Phishing Detection System
# Starting server on http://0.0.0.0:5000
```

## Using the System

### Web Interface
1. Open browser: http://localhost:5000
2. Choose "Scan Email" or "Scan URL"
3. Paste content to scan
4. View results instantly

### API Usage

**Scan Email (cURL):**
```bash
curl -X POST http://localhost:5000/api/v1/scan/email \
  -H "Content-Type: application/json" \
  -d '{"email_content":"Subject: Verify Account\n\nClick here to confirm..."}'
```

**Scan URL (cURL):**
```bash
curl -X POST http://localhost:5000/api/v1/scan/url \
  -H "Content-Type: application/json" \
  -d '{"url":"http://suspicious-site.com"}'
```

**Python:**
```python
import requests

response = requests.post(
    'http://localhost:5000/api/v1/scan/email',
    json={'email_content': 'Your email here...'}
)
result = response.json()
print(f"Phishing: {result['is_phishing']}")
print(f"Confidence: {result['confidence']:.1%}")
```

## Test Data

Try these test inputs:

**Phishing Email:**
```
Subject: URGENT: Verify Your Account

Click here immediately to verify your account or it will be suspended!
Your account has been compromised. Update your password now.
Act immediately to protect your account.
```

**Legitimate Email:**
```
Subject: Meeting Tomorrow

Hi, I wanted to schedule a meeting for tomorrow at 2pm.
Please let me know if that works for you.
Looking forward to hearing from you.
```

**Phishing URL:**
- http://192.168.1.1/ (uses IP)
- http://verify-paypal.com/ (impersonation)
- http://bit.ly/phishing (URL shortener)

**Legitimate URL:**
- https://www.google.com
- https://github.com
- https://mailchimp.com

## Troubleshooting

**Port 5000 already in use?**
```bash
# Kill process on port 5000
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:5000 | xargs kill -9
```

**Model not found?**
```bash
# Retrain the model
python train_model.py
```

**Can't connect to API?**
1. Make sure server is running: `python main.py`
2. Check firewall settings
3. Try: http://localhost:5000/status

## Performance Tips

- Cache model in memory after first load
- Use batch endpoint for multiple scannings
- Implement request rate limiting
- Use async processing for high volume

## Next Steps

- Integrate with your email system
- Train model with your data
- Customize detection thresholds
- Deploy to production
- Monitor alerts in real-time

See README.md for complete documentation.
