# Domain Age Checker - Quick Start Guide

## ⚡ Get Running in 3 Minutes

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Start the Application
```bash
python app.py
```

Output:
```
Running on http://127.0.0.1:5000
```

### Step 3: Open in Browser
Visit: **http://localhost:5000**

---

## 🎯 Quick Examples

### Via Web Interface
1. Go to http://localhost:5000
2. Type `google.com`
3. Click "Check Domain"
4. See results instantly!

### Via API (Command Line)
```bash
# Check a domain
python -c "import requests; print(requests.get('http://localhost:5000/check-domain?domain=github.com').json())"

# Check health
python -c "import requests; print(requests.get('http://localhost:5000/api/health').json())"
```

---

## 📋 What You Get

For any domain, you'll see:
- ✅ When it was registered (creation date)
- ✅ Domain age (years, months, days)
- ✅ When it expires (expiration date)
- ✅ Current registrar
- ✅ Domain status (active/expired)

---

## 🆘 Troubleshooting

### "Port 5000 already in use?"
```bash
# Change the port in app.py
python app.py --port=8000
# Then visit http://localhost:8000
```

### "ModuleNotFoundError"?
```bash
# Make sure dependencies are installed
pip install -r requirements.txt
```

### "Domain not found"?
- Domain may not exist
- WHOIS server may be slow
- Try another domain to test
- Internet must be connected

---

## 🔗 Useful URLs

| URL | Purpose |
|-----|---------|
| http://localhost:5000 | Web interface |
| http://localhost:5000/api/health | Health check |
| http://localhost:5000/check-domain?domain=example.com | API endpoint |

---

## 📚 Need Help?

See **README.md** for complete documentation
