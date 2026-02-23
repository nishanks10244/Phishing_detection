# PhishGuard System Architecture & Technical Documentation

## 🏗️ System Architecture

### Overview
PhishGuard is a multi-component system consisting of:
1. **Backend Server** - Flask API with ML models
2. **Web Dashboard** - SaaS-style dark UI
3. **Chrome Extension** - Browser integration
4. **ML Pipeline** - Feature extraction & prediction

### Component Interactions

```
┌─────────────────────────────────────────────────────────────┐
│                      USER                                   │
└─────────┬────────────────────────────────────────┬──────────┘
          │                                        │
          ▼                                        ▼
    ┌──────────────┐                      ┌──────────────────┐
    │ WEB INTERFACE│                      │ CHROME EXTENSION │
    │  (Dashboard) │                      │   (popup.html)   │
    └──────┬───────┘                      └─────────┬────────┘
           │                                        │
           │                                        │
           └────────────┬───────────────────────────┘
                        │
                        ▼
           ┌────────────────────────────┐
           │  FLASK API SERVER          │
           │  (http://localhost:5000)   │
           └────────────┬───────────────┘
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
    ┌──────────┐  ┌───────────┐  ┌──────────┐
    │ FEATURE  │→ │ ML MODEL  │→ │ RESULT   │
    │EXTRACTOR │  │(XGBoost)  │  │FORMATTER │
    └──────────┘  └───────────┘  └──────────┘
```

## 🔄 Request Flow

### Email Scanning
```
1. User pastes email content
2. Frontend sends POST to /api/v1/scan/email
3. Backend parses email (EmailParser)
4. Features extracted (FeatureExtractor)
5. ML model predicts (PhishingDetector)
6. Results returned with confidence score
7. UI displays results with animations
```

### URL Scanning
```
1. User enters URL
2. Frontend sends POST to /api/v1/scan/url
3. Backend analyzes URL characteristics
4. Features extracted (URLAnalyzer)
5. ML model predicts
6. Results show security details
7. Warning banner displayed if phishing
```

### Extension Real-Time Scan
```
1. User visits website
2. Content script executes automatically
3. Current page URL extracted
4. Background service worker scans
5. Result cached for performance
6. Warning banner injected if dangerous
7. Suspicious links marked
```

## 📊 Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                     INPUT DATA                               │
│              (Email / URL / Webpage)                         │
└────────────────────┬─────────────────────────────────────────┘
                     │
                     ▼
         ┌────────────────────────────┐
         │  FEATURE EXTRACTION        │
         │  ─────────────────────────  │
         │ • Email parsing            │
         │ • Keyword extraction       │
         │ • URL analysis             │
         │ • Text vectorization       │
         └────────────┬───────────────┘
                      │
                      ▼
         ┌────────────────────────────┐
         │  FEATURE VECTOR            │
         │  ─────────────────────────  │
         │ • 16+ engineered features  │
         │ • 1000+ TF-IDF features    │
         │ • Normalized values        │
         └────────────┬───────────────┘
                      │
                      ▼
         ┌────────────────────────────┐
         │  ML MODEL PREDICTION       │
         │  ─────────────────────────  │
         │ • XGBoost or Gradient      │
         │   Boosting Classifier      │
         │ • Probability calculation  │
         │ • Confidence scoring       │
         └────────────┬───────────────┘
                      │
                      ▼
         ┌────────────────────────────┐
         │  RISK ASSESSMENT           │
         │  ─────────────────────────  │
         │ • Phishing or Safe check   │
         │ • Risk level (HIGH/MED/LOW)│
         │ • Confidence %             │
         └────────────┬───────────────┘
                      │
                      ▼
         ┌────────────────────────────┐
         │  OUTPUT RESPONSE           │
         │  ─────────────────────────  │
         │ • is_phishing: bool        │
         │ • confidence: float        │
         │ • risk_level: string       │
         │ • details: dict            │
         └────────────────────────────┘
```

## 🤖 Machine Learning Pipeline

### Training Process
```
Raw Data
   ↓
Feature Extraction
   ↓
Text Vectorization (TF-IDF)
   ├─ Max 1000 features
   ├─ Bigram support
   └─ English stopwords removed
   ↓
Feature Scaling
   ├─ StandardScaler
   └─ Normalize ranges
   ↓
Model Training
   ├─ XGBoost (preferred)
   │  ├─ 100 estimators
   │  ├─ Learning rate: 0.1
   │  └─ Max depth: 5
   └─ Or Gradient Boosting
   ↓
Model Evaluation
   ├─ Precision: 95%
   ├─ Recall: 90%
   ├─ F1-Score: 92%
   └─ ROC-AUC: 96%
   ↓
Model Serialization
   ├─ Model pickle
   └─ Vectorizer pickle
```

### Prediction Process
```
Input (Email/URL)
   ↓
Parse & Extract
   ├─ EmailParser OR URLAnalyzer
   └─ Get text content
   ↓
Feature Engineering
   ├─ 16+ structural features
   ├─ Keyword counts
   └─ Domain analysis
   ↓
Vectorization
   └─ Transform text with TF-IDF
   ↓
Feature Scaling
   └─ Apply StandardScaler
   ↓
Model Prediction
   ├─ get_prediction(features)
   └─ get_probability()
   ↓
Result Formatting
   ├─ Confidence calculation
   ├─ Risk level assignment
   └─ Detail extraction
   ↓
Response to User
   └─ JSON with results
```

## 📁 Key Files & Functions

### Backend Core
| File | Key Functions | Purpose |
|------|--------------|---------|
| `src/app.py` | `create_app()` | Flask app factory |
| `src/config.py` | Config classes | Environment settings |
| `src/api/routes.py` | Route handlers | API endpoints |
| `src/models/detector.py` | PhishingDetector | ML model wrapper |
| `src/utils/email_parser.py` | EmailParser, URLAnalyzer | Text parsing |
| `src/utils/feature_extractor.py` | FeatureExtractor | Feature engineering |
| `src/alerts/alert_manager.py` | AlertManager | Alert handling |

### Frontend
| File | Purpose |
|------|---------|
| `frontend/index.html` | Landing page |
| `frontend/dashboard.html` | Main scanner UI |

### Extension
| File | Purpose |
|------|---------|
| `chrome-extension/manifest.json` | Extension config |
| `chrome-extension/popup.html` | Popup UI |
| `chrome-extension/js/popup.js` | Popup logic |
| `chrome-extension/js/background.js` | Service worker |
| `chrome-extension/js/content.js` | Page injection |

### Training
| File | Purpose |
|------|---------|
| `train_model.py` | Basic model training |
| `train_advanced.py` | Advanced with XGBoost |

## 🔌 API Architecture

### RESTful Endpoints
```
POST /api/v1/scan/email
├─ Input: email_content (string)
├─ Output: phishing prediction
└─ Time: ~1-2 seconds

POST /api/v1/scan/url
├─ Input: url (string)
├─ Output: url analysis
└─ Time: ~300-800ms

POST /api/v1/scan/batch
├─ Input: array of items
├─ Output: batch results
└─ Time: linear with count

GET /api/v1/health
├─ Check server status
└─ Return: healthy/unhealthy

GET /api/v1/model/info
├─ Model information
└─ Return: model state
```

### Response Schema
```json
{
  "is_phishing": boolean,
  "confidence": float (0-1),
  "risk_level": "low|medium|high|critical",
  "details": {
    "subject": "email subject",
    "sender": "sender@email.com",
    "url_count": 2,
    "suspicious_urls": 1,
    "urls": ["http://..."],
    "domain": "example.com",
    "uses_https": true,
    "has_ip": false,
    "suspicious_pattern": false
  },
  "timestamp": "ISO 8601 datetime"
}
```

## 🔐 Security Layers

### Input Validation
- Email content size limits
- URL format validation
- Character encoding checks
- Injection protection

### Model Security
- Model integrity verification
- Version tracking
- Update mechanism
- Fallback models

### Data Protection
- No persistent storage of scans
- Memory-based caching only
- Automatic cache expiration
- Encrypted communications (HTTPS ready)

## 🚀 Performance Optimization

### Caching Strategy
```python
# Cache Configuration
CACHE_DURATION = 3600000  # 1 hour in milliseconds

# Cache Key: URL or email hash
cache[hash(input)] = {
    'result': prediction,
    'timestamp': current_time,
    'confidence': score
}
```

### Model Loading
- Load model once at startup
- Vectorizer cached in memory
- Scaler parameters persistent
- No reload on each request

### Feature Extraction
- Fast vectorization with TF-IDF
- Pre-computed feature importance
- Vectorized operations with NumPy
- Minimal string operations

## 📊 Monitoring & Logging

### Log Levels
- DEBUG: Detailed diagnostic info
- INFO: General operational messages
- WARNING: Warning messages
- ERROR: Error conditions
- CRITICAL: Critical errors

### Log Files
- `phishing_detector.log` - Main application log
- Console output for development
- Rotating file handler (optional)

### Metrics Tracked
- Request count by endpoint
- Average response time
- Model prediction distribution
- Cache hit rate
- Error frequency

## 🔄 Extension Architecture

### Manifest v3 Features
- Service Workers (not background pages)
- Content scripts for page injection
- Dynamic host permissions
- Secure API communication

### Extension Permissions
```json
{
  "permissions": ["tabs", "activeTab", "scripting", "storage", "notifications"],
  "host_permissions": ["http://localhost:5000/*", "<all_urls>"]
}
```

### Content Script Injection
- Runs on every webpage
- Scans page URL automatically
- Marks suspicious links
- Shows warning banners
- Cache results for performance

## 🧬 ML Feature Engineering

### Email Features
1. **Length Metrics**
   - Subject length
   - Body length
   - Total character count

2. **Keyword Features**
   - Urgent/threatening words
   - Financial/payment keywords
   - Personal information requests
   - Action/CTA words
   - Urgency score

3. **Structure Features**
   - URL count
   - Email count
   - Attachment presence
   - Unusual capitalization ratio
   - Excessive punctuation

4. **Sender Features**
   - Domain mismatch check
   - Suspicious domain detection
   - Alphanumeric patterns

5. **URL Features**
   - Risk score calculation
   - Suspicious URL count
   - Domain-email mismatch

### URL Features
1. **Domain Analysis**
   - IP address detection
   - Subdomain count
   - Domain age indicator

2. **Protocol Security**
   - HTTPS usage
   - Non-standard ports
   - Scheme validation

3. **URL Structure**
   - Length analysis
   - Special character count
   - Path complexity

4. **Pattern Matching**
   - Suspicious keywords
   - Brand impersonation
   - TLD reputation

## 🔧 Configuration Management

### Environment Variables
```bash
FLASK_ENV=development
FLASK_APP=main.py
SECRET_KEY=dev-key-change-in-production
DATABASE_URL=sqlite:///phishing_detector.db
LOG_LEVEL=INFO
MODEL_CONFIDENCE_THRESHOLD=0.5
```

### Config Classes
```python
class Config:
    DEBUG = False
    DATABASE_URI = 'sqlite:///phishing_detector.db'
    
class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False
    # Add production settings
```

## 📈 Scaling Strategies

### Horizontal Scaling
- Load balancer distribution
- Multiple Flask instances
- Shared model loading
- Stateless API design

### Vertical Scaling
- GPU acceleration for inference
- Multi-threading model predictions
- Async request processing
- Memory optimization

### Distributed ML
- Batch processing multiple requests
- Parallel vectorization
- Distributed caching (Redis)
- Microservices architecture

## 🔄 Development Workflow

### Training -> Production
```
1. Collect training data
2. Run train_advanced.py
3. Evaluate metrics
4. Save model artifacts
5. Version control models
6. Deploy to production
7. Monitor predictions
8. Collect feedback
9. Retrain periodically
```

### CI/CD Integration
```
1. Code commit → GitHub
2. Run tests → pytest
3. Build image → Docker
4. Push to registry
5. Update deployment
6. Monitor logs
7. Rollback if needed
```

## 🎯 Key Metrics & Dashboards

Would monitor:
- Phishing detection rate
- False positive rate
- Average scan time
- Model accuracy drift
- API uptime
- Extension usage stats
- Cache hit rate

---

**Last Updated:** February 2026
**Version:** 2.0.0
**Status:** Complete Documentation
