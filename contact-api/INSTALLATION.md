# Installation Guide - Triple C Contact API

Complete step-by-step installation guide for the contact form backend system.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Gmail Setup](#gmail-setup)
3. [Local Installation](#local-installation)
4. [Configuration](#configuration)
5. [Testing](#testing)
6. [Frontend Integration](#frontend-integration)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **pip** - Included with Python
- **Git** - [Download](https://git-scm.com/downloads)
- **Gmail Account** - For SMTP email delivery

### System Requirements

- **OS**: macOS, Linux, or Windows
- **RAM**: 512MB minimum
- **Storage**: 100MB minimum
- **Network**: Internet connection for SMTP

### Check Prerequisites

```bash
# Check Python version (must be 3.11+)
python3 --version

# Check pip
pip3 --version

# Check Git
git --version
```

---

## Gmail Setup

The API uses Gmail SMTP for sending emails. You need an App Password (not your regular password).

### Step 1: Enable 2-Factor Authentication

1. Go to https://myaccount.google.com/security
2. Click "2-Step Verification"
3. Follow the setup process
4. Verify 2FA is enabled

### Step 2: Generate App Password

1. Go to https://myaccount.google.com/apppasswords
2. Select app: "Mail"
3. Select device: "Other (Custom name)"
4. Enter: "Triple C Contact API"
5. Click "Generate"
6. **Save the 16-character password** (you'll need this)

**Important**: Use this App Password, NOT your regular Gmail password.

---

## Local Installation

### Step 1: Navigate to Project

```bash
cd /Users/247takadminstator/LLM/projects/cccops-website/contact-api
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate

# Verify activation (should show venv in prompt)
which python
```

### Step 3: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Verify installation
pip list
```

Expected packages:
- fastapi
- uvicorn
- pydantic
- python-dotenv
- python-multipart

---

## Configuration

### Step 1: Create Environment File

```bash
# Copy example
cp .env.example .env

# Open for editing
nano .env
# Or use your preferred editor: code .env, vim .env, etc.
```

### Step 2: Configure SMTP Settings

Replace these values in `.env`:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com              # Your Gmail address
SMTP_PASSWORD=abcd efgh ijkl mnop           # 16-char App Password
FROM_EMAIL=your-email@gmail.com             # Same as SMTP_USER
OWNER_EMAIL=consultingbytriplec@gmail.com   # Where submissions go
```

**Example**:
```env
SMTP_USER=john.doe@gmail.com
SMTP_PASSWORD=abcd efgh ijkl mnop
FROM_EMAIL=john.doe@gmail.com
OWNER_EMAIL=consultingbytriplec@gmail.com
```

### Step 3: Generate API Key

Generate a secure random API key:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output and add to `.env`:

```env
ADMIN_API_KEY=your-generated-key-here
```

### Step 4: Verify Configuration

Your `.env` should look like:

```env
# SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com
OWNER_EMAIL=consultingbytriplec@gmail.com

# Admin API Key
ADMIN_API_KEY=your-secure-random-key

# Rate Limiting
RATE_LIMIT_REQUESTS=5
RATE_LIMIT_WINDOW_SECONDS=3600

# Application
ENV=development
DEBUG=true
```

---

## Testing

### Step 1: Start the Server

```bash
# Easy way (recommended)
./start.sh

# Or manually
python main.py
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 2: Test Health Check

Open a new terminal:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "ok",
  "database": "healthy",
  "timestamp": "2025-12-17T11:14:00"
}
```

### Step 3: Run Automated Tests

```bash
./test_api.sh
```

You should see:
```
✓ PASSED - Health check
✓ PASSED - Root endpoint
✓ PASSED - Contact submission
✓ PASSED - Invalid email rejected
...
```

### Step 4: Test Manual Submission

```bash
curl -X POST http://localhost:8000/api/contact \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "organization": "Test Corp",
    "message": "This is a test message from the installation guide."
  }'
```

Expected response:
```json
{
  "success": true,
  "message": "Thank you for your message. We'll be in touch within 24 hours.",
  "submission_id": 1
}
```

### Step 5: Check Emails

1. **Check owner email** (consultingbytriplec@gmail.com)
   - Should receive notification with submission details

2. **Check test email** (test@example.com)
   - Should receive confirmation email

### Step 6: Test Admin Endpoints

```bash
# Replace YOUR_API_KEY with the key from .env
curl -H "X-API-Key: YOUR_API_KEY" \
  http://localhost:8000/api/submissions
```

Expected: JSON array of all submissions

---

## Frontend Integration

### Step 1: Verify Frontend Files

The frontend is already updated in:
- `/Users/247takadminstator/LLM/projects/cccops-website/index.html`
- `/Users/247takadminstator/LLM/projects/cccops-website/js/script-v2.js`

### Step 2: Test Frontend Locally

```bash
# Navigate to website directory
cd /Users/247takadminstator/LLM/projects/cccops-website

# Start a simple HTTP server
python3 -m http.server 3000
```

Open browser to: http://localhost:3000

### Step 3: Test Form Submission

1. Scroll to Contact section
2. Fill out form:
   - Name: "Test User"
   - Email: "your-email@example.com"
   - Message: "Testing the contact form"
3. Click "Send Message"
4. Should see green success message
5. Check your email for confirmation

### Step 4: Production Configuration

When deploying to production, update the API URL in:

**File**: `/Users/247takadminstator/LLM/projects/cccops-website/js/script-v2.js`

**Line 172**: Change from:
```javascript
const apiUrl = 'http://localhost:8000/api/contact';
```

To your production URL:
```javascript
const apiUrl = 'https://api.cccops.com/api/contact';
```

---

## Troubleshooting

### Problem: "SMTP Authentication Error"

**Symptoms**: Email not sending, SMTP error in logs

**Solution**:
1. Verify you're using App Password (not regular password)
2. Check 2FA is enabled on Google account
3. Regenerate App Password if needed
4. Test SMTP manually:

```python
python3 -c "
import smtplib
smtp = smtplib.SMTP('smtp.gmail.com', 587)
smtp.starttls()
smtp.login('your-email@gmail.com', 'your-app-password')
print('SMTP connection successful!')
smtp.quit()
"
```

### Problem: "Module not found" Error

**Symptoms**: ImportError when starting server

**Solution**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep fastapi
```

### Problem: "Address already in use"

**Symptoms**: Can't start server, port 8000 in use

**Solution**:
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process (replace PID)
kill -9 <PID>

# Or use different port
python main.py --port 8001
```

### Problem: "Permission denied" on .db file

**Symptoms**: Database errors, can't write

**Solution**:
```bash
# Check permissions
ls -la *.db

# Fix permissions
chmod 644 contact_submissions.db
```

### Problem: CORS Error in Browser

**Symptoms**: Form submission fails with CORS error

**Solution**:
1. Check `ALLOWED_ORIGINS` in `main.py`
2. Add your domain to the list
3. Restart server

### Problem: Rate Limit Exceeded

**Symptoms**: "429 Too Many Requests"

**Solution**:
```bash
# Edit .env
RATE_LIMIT_REQUESTS=10  # Increase limit

# Or wait 1 hour for reset
# Or restart server to clear memory
```

### Problem: Frontend Not Connecting to API

**Symptoms**: Form submission fails, network error

**Solution**:
1. Verify API is running: `curl http://localhost:8000/health`
2. Check API URL in `script-v2.js` (line 172)
3. Open browser console (F12) for details
4. Verify CORS configuration

---

## Next Steps

### Production Deployment

See `DEPLOYMENT.md` for:
- VPS deployment (Ubuntu)
- Docker deployment
- Cloud platform deployment
- SSL/TLS setup
- Security hardening

### Monitoring

Set up:
- Uptime monitoring (UptimeRobot)
- Error tracking (Sentry)
- Log aggregation
- Database backups

### Maintenance

Regular tasks:
- Review submissions daily
- Update dependencies monthly
- Check logs weekly
- Test backups quarterly

---

## Getting Help

### Documentation Files

- **README.md** - Complete documentation
- **QUICKSTART.md** - 5-minute setup
- **DEPLOYMENT.md** - Production deployment
- **PROJECT_SUMMARY.md** - Project overview

### API Documentation

Once server is running:
- Interactive docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

### Support

**Triple C Consulting**
- Email: consultingbytriplec@gmail.com
- Phone: (509) 903-6285
- Website: https://cccops.com

---

## Installation Checklist

- [ ] Python 3.11+ installed
- [ ] Gmail 2FA enabled
- [ ] Gmail App Password generated
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] `.env` file configured
- [ ] Server starts successfully
- [ ] Health check passes
- [ ] Test submission works
- [ ] Emails received
- [ ] Admin API accessible
- [ ] Frontend form works
- [ ] All tests pass

**Status**: If all checked, installation is complete!

---

**Installation Guide Version**: 1.0.0
**Last Updated**: December 17, 2025
