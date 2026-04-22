# Domain Age Checker - Complete Setup & Usage Guide

## Overview
A fully-featured Flask web application that checks domain registration age and provides detailed WHOIS information including registrar details, registration dates, and domain status.

## ✨ Features
- **Domain Lookup**: Check when any domain was registered  
- **Domain Age Calculation**: Automatic calculation in years, months, and days  
- **WHOIS Data Extraction**: Registration date, expiration date, registrar, and status  
- **Clean UI**: Responsive, modern interface with cards and real-time results  
- **Error Handling**: Graceful handling of invalid domains and lookup failures  
- **Caching**: 24-hour per-domain cache to reduce WHOIS API calls  
- **API Endpoint**: JSON API for programmatic access  
- **Health Check**: Monitoring endpoint for service status

## 📁 Project Structure
```
domain-age-checker/
├── app.py                 # Main Flask application (Flask app + routes + caching)
├── whois_service.py       # WHOIS lookup and parsing service module
├── requirements.txt       # Python dependencies (all packages)
├── templates/
│   ├── base.html         # Base template (layout & structure)
│   └── index.html        # Home page with domain form & results display
└── static/
    └── style.css         # Responsive CSS (modern design + animations)
```

## 📦 Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

**Key Dependencies:**
- **Flask 3.0.0** - Web framework
- **python-whois 0.9.6** - WHOIS lookup library
- **validators 0.22.0** - Domain validation
- **flask-caching 2.1.0** - In-memory caching layer
- **python-dateutil 2.8.2** - Date parsing and calculation
- **requests 2.31.0** - HTTP client

### 2. Verify Installation
```bash
python -c "import flask, whois, validators, flask_caching; print('✓ All dependencies installed successfully')"
```

## 🚀 Running the Application

### Development Mode
```bash
python app.py
```

The application will start at:
- **Local**: http://localhost:5000
- **Network**: http://192.168.1.64:5000 (adjust IP as needed)

### Production Mode (with Gunicorn)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 💻 Usage

### Web Interface
1. Open `http://localhost:5000` in your browser
2. Enter a domain name (e.g., `example.com`, `google.com`, `github.com`)
3. Click "Check Domain" button
4. View results in organized cards showing:
   - Domain name and status (active/expired)
   - Registration date
   - Expiration date
   - Registrar name
   - Domain age (years, months, days)

### API Endpoint

**Endpoint:** `GET /check-domain`

**Query Parameters:**
- `domain` (required): Domain name to check

**Example Requests:**

```bash
# Using curl
curl "http://localhost:5000/check-domain?domain=example.com"

# Using Python requests
python -c "import requests; print(requests.get('http://localhost:5000/check-domain?domain=google.com').json())"
```

**Response Format:**
```json
{
  "domain": "example.com",
  "created_date": "1995-08-14",
  "expiration_date": "2026-08-13",
  "age": "30 years, 8 months, 8 days",
  "registrar": "VeriSign Global Registry Services",
  "status": "active",
  "error": null
}
```

**Status Values:**
- `active` - Domain is registered and not expired
- `expired` - Domain registration has expired
- `invalid` - Invalid domain format
- `not_found` - Domain doesn't exist or WHOIS lookup failed
- `error` - Service error occurred
- `unknown` - Cannot determine status

### Health Check Endpoint
```bash
curl http://localhost:5000/api/health
```

Response:
```json
{
  "status": "healthy",
  "service": "Domain Age Checker"
}
```

## 🔧 Configuration

### Cache Settings
Edit the cache configuration in `app.py`:
```python
cache_config = {
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 86400  # 24 hours
}
```

**Cache Behavior:**
- Each domain gets its own cache key: `whois_result_{domain}`
- Cache timeout: 24 hours (86400 seconds)
- Automatic expiration after TTL
- In-memory storage (no Redis needed)

### Debug Mode
```python
# In app.py - change debug setting
app.run(debug=False)  # Disable for production
```

## 🧪 Testing

### Test Valid Domains
```bash
# Test with well-known domains
python -c "import requests; r = requests.get('http://localhost:5000/check-domain?domain=google.com'); print(r.json())"
python -c "import requests; r = requests.get('http://localhost:5000/check-domain?domain=github.com'); print(r.json())"
python -c "import requests; r = requests.get('http://localhost:5000/check-domain?domain=example.com'); print(r.json())"
```

### Test Error Handling
```bash
# Invalid format (no TLD)
python -c "import requests; r = requests.get('http://localhost:5000/check-domain?domain=novaliddomain'); print(r.json())"

# Missing parameter
python -c "import requests; r = requests.get('http://localhost:5000/check-domain'); print(r.status_code, r.json())"

# Non-existent domain
python -c "import requests; r = requests.get('http://localhost:5000/check-domain?domain=thisshouldnotexist99999.com'); print(r.json())"
```

### Test Caching Performance
```bash
# First request (no cache)
python -c "import requests, time; s=time.time(); r=requests.get('http://localhost:5000/check-domain?domain=test123.com'); print(f'Time: {(time.time()-s)*1000:.2f}ms')"

# Second request (from cache - should be instant)
python -c "import requests, time; s=time.time(); r=requests.get('http://localhost:5000/check-domain?domain=test123.com'); print(f'Time: {(time.time()-s)*1000:.2f}ms')"
```

### Supported Domain Extensions
The application works with all valid TLDs:
- Generic: `.com`, `.org`, `.net`, `.edu`, `.gov`, `.mil`
- Country: `.uk`, `.de`, `.fr`, `.jp`, `.au`, `.ca`
- Modern: `.io`, `.ai`, `.co`, `.dev`, `.app`, `.cloud`
- And hundreds of other extensions

## 📋 Module Details

### whois_service.py
**Main Functions:**

- `validate_domain(domain)` - Validates domain format using regex pattern
- `get_domain_age(domain)` - Main WHOIS lookup function with error handling
- `calculate_age(created_date)` - Calculates age in years/months/days format
- `normalize_date(date_value)` - Converts various date formats to YYYY-MM-DD

**DomainInfo Class:**
- Data container for domain information
- `to_dict()` method for JSON serialization
- Stores: domain, created_date, expiration_date, age, registrar, status, error

**Error Handling:**
- Invalid domain format → returns "Invalid domain format" error
- WHOIS lookup failure → returns "Domain not found or WHOIS lookup failed"
- Network errors → returns "Error during WHOIS lookup"
- Missing data → normalizes to "Unknown"

### app.py
**Main Routes:**

- `GET /` - Renders home page with domain form
- `GET /check-domain` - API endpoint for domain lookup (JSON response)
- `GET /api/health` - Health check endpoint (for monitoring)

**Features:**
- Request validation (domain parameter required)
- Logging for debugging and monitoring
- Custom caching with per-domain cache keys
- Error handling with appropriate HTTP status codes
- CORS-friendly JSON responses

**Caching Implementation:**
- Custom `get_cached_domain_info()` function
- Per-domain cache keys: `whois_result_{domain}`
- 24-hour TTL (Time To Live)
- Cache hit logging for monitoring

## 🎨 Frontend Features

### Responsive Design
- Mobile-first approach
- Adapts to screens from 480px and up
- Touch-friendly buttons and inputs
- Flexible grid layout

### User Experience
- Real-time form validation
- Loading spinner during lookup
- Animated card results
- Color-coded status badges
- XSS protection with HTML escaping
- Helpful error messages

### Styling Features
- Modern gradient background (purple)
- Smooth CSS transitions and animations
- CSS Grid for responsive layout
- Color scheme:
  - Active domains: Green badge
  - Expired domains: Red badge
  - Unknown status: Gray badge

## 🚢 Deployment

### Docker (Optional)
Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV FLASK_ENV=production
ENV FLASK_DEBUG=0

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

Build and run:
```bash
docker build -t domain-age-checker .
docker run -p 5000:5000 domain-age-checker
```

### Environment Variables (Production)
```bash
export FLASK_ENV=production
export FLASK_DEBUG=0
export CACHE_TYPE=redis  # For larger deployments
```

## 🐛 Troubleshooting

### WHOIS Lookup Fails
- **Issue**: "Domain not found" or WHOIS error
- **Solution**: 
  - Check internet connectivity
  - Some registrars block automated WHOIS queries
  - Try a different domain to verify service is working
  - WHOIS servers may have rate limits

### Import Errors
- **Issue**: ModuleNotFoundError for flask, whois, etc.
- **Solution**: 
  - Verify all dependencies: `pip install -r requirements.txt`
  - Check Python version is 3.8+: `python --version`
  - Use virtual environment for isolation

### Slow Lookups
- **Issue**: Requests taking 2-5 seconds
- **Solution**: 
  - First query for a domain makes WHOIS call (expected)
  - Subsequent queries are cached (nearly instant)
  - Caching persists for 24 hours per domain
  - Clear cache by restarting the application

### Port Already in Use
- **Issue**: "Address already in use" error
- **Solution**: 
  - Change port in `app.py`: `app.run(port=8000)`
  - Or kill process using port 5000:
    - Windows: `netstat -ano | findstr :5000`
    - Linux/Mac: `lsof -i :5000`

### Missing Registration Date
- **Issue**: created_date shows "Unknown"
- **Solution**: 
  - Some domains don't publicly display registration info
  - This is controlled by WHOIS privacy settings
  - Domain age cannot be calculated for these domains

## 📊 Logging

Check application logs for debugging:

```bash
# Windows - Terminal output shows logs directly
# Linux/Mac - Output to file:
python app.py > app.log 2>&1 &

# Check logs
tail -f app.log
```

**Log Levels:**
- `INFO` - Normal operations (domain lookups, cache hits)
- `WARNING` - Potential issues (missing data, deprecations)
- `ERROR` - Errors (WHOIS failures, network issues)
- `DEBUG` - Detailed debugging info (enable if needed)

**Example Log Output:**
```
2026-04-22 11:37:37 - __main__ - INFO - Fetching WHOIS data for domain: example.com
2026-04-22 11:37:40 - __main__ - INFO - Cache hit for domain: google.com
2026-04-22 11:37:50 - werkzeug - INFO - 127.0.0.1 - - [22/Apr/2026 11:37:50] "GET /check-domain?domain=github.com HTTP/1.1" 200
```

## ⚡ Performance

### Cache Effectiveness
- **First query** for a domain: 2-5 seconds (WHOIS lookup)
- **Cached query**: <200ms (in-memory retrieval)
- **Cache hit rate** depends on usage patterns
- **24-hour TTL** balances freshness with performance

### Optimization Tips
1. Use Redis for production caching (multi-instance support)
2. Implement request rate limiting for API
3. Add CDN for static assets (CSS, JS)
4. Monitor WHOIS API rate limits
5. Use connection pooling for WHOIS requests
6. Consider async WHOIS lookups for high traffic

### Scalability Considerations
- Current implementation: Single instance with in-memory cache
- For high traffic:
  - Use Gunicorn with multiple workers (4-8)
  - Implement Redis for shared cache
  - Add rate limiting middleware
  - Use reverse proxy (Nginx)
  - Consider async/task queue (Celery)

## 🔐 Security Considerations

### ✅ Already Implemented
- HTML escaping to prevent XSS attacks
- Domain format validation (regex)
- Error message sanitization
- No sensitive data stored or logged
- HTTPS-ready (use reverse proxy for TLS)

### 🔒 Recommended for Production
- Use HTTPS/TLS certificate
- Implement request rate limiting (e.g., 10 req/min per IP)
- Add authentication if API is private
- Use environment variables for configuration
- Set up firewall rules and VPN access
- Implement request logging and monitoring
- Regular security audits

## 📈 Future Enhancements

Possible improvements:
- Batch domain checking (multiple domains at once)
- Export results to CSV/JSON/PDF
- Domain expiration alerts/email notifications
- Historical domain age tracking
- Enhanced WHOIS data parsing (more fields)
- Integration with other domain APIs (DNSChecker, Shodan)
- Docker compose with Redis
- Admin dashboard for monitoring
- API key authentication
- Webhook notifications for expired domains

## 📝 API Response Examples

### Successful Lookup
```json
{
  "domain": "google.com",
  "created_date": "1997-09-15",
  "expiration_date": "2028-09-14",
  "age": "28 years, 7 months, 7 days",
  "registrar": "MarkMonitor, Inc.",
  "status": "active",
  "error": null
}
```

### Invalid Domain Format
```json
{
  "domain": "novaliddomain",
  "created_date": null,
  "expiration_date": null,
  "age": null,
  "registrar": null,
  "status": "invalid",
  "error": "Invalid domain format. Please enter a valid domain (e.g., example.com)"
}
```

### Domain Not Found
```json
{
  "domain": "nonexistent12345.com",
  "created_date": null,
  "expiration_date": null,
  "age": null,
  "registrar": null,
  "status": "not_found",
  "error": "Domain not found or WHOIS lookup failed: No matching query."
}
```

## 📞 Support & Contact

For issues or questions:
1. Check the **Troubleshooting** section above
2. Verify all dependencies are installed correctly
3. Ensure WHOIS service is accessible
4. Check application logs for errors
5. Test with different domains to isolate the issue

## 📄 License

This project is open source and available for educational and commercial use.

## 🎯 Testing Summary

✅ **All Tests Passed:**
- Health check endpoint working
- Domain lookups returning correct WHOIS data
- Error handling for invalid domains
- Caching working (per-domain cache keys)
- HTML home page rendering correctly
- Parameter validation working
- All dependencies installed successfully

---

**Version:** 1.0  
**Last Updated:** April 2026  
**Python Version:** 3.8+  
**Status:** ✅ Production Ready
