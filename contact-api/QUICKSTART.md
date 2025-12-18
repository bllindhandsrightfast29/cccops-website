# Quick Start Guide - Contact API

Get the Contact API running in 5 minutes.

## Prerequisites

- Python 3.11 or higher
- Gmail account with App Password configured

## Step 1: Configure Environment

```bash
cd contact-api

# Copy example environment file
cp .env.example .env

# Edit configuration
nano .env
```

**Required settings in `.env`:**

```env
# Gmail SMTP (Get App Password from https://myaccount.google.com/apppasswords)
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
OWNER_EMAIL=consultingbytriplec@gmail.com

# Generate secure API key
# Run: python -c "import secrets; print(secrets.token_urlsafe(32))"
ADMIN_API_KEY=your-generated-api-key-here
```

## Step 2: Start the Server

```bash
# Easy way (uses start.sh script)
./start.sh

# Or manually
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

Server will start at: http://localhost:8000

## Step 3: Test the API

```bash
# Run automated tests
./test_api.sh

# Or test manually
curl -X POST http://localhost:8000/api/contact \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "message": "Test message"
  }'
```

## Step 4: View API Documentation

Open in browser:
- Interactive docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## Step 5: Update Frontend

Edit `/Users/247takadminstator/LLM/projects/cccops-website/js/script-v2.js`:

```javascript
// Line 172 - change API URL for production
const apiUrl = 'https://your-production-url.com/api/contact';
```

## Common Commands

```bash
# Start server (development)
python main.py

# Start server (production)
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Test API
./test_api.sh

# View submissions (requires API key)
curl -H "X-API-Key: your-api-key" http://localhost:8000/api/submissions

# Check health
curl http://localhost:8000/health
```

## API Endpoints

### Public
- `POST /api/contact` - Submit contact form

### Admin (requires X-API-Key header)
- `GET /api/submissions` - List all submissions
- `GET /api/submissions/{id}` - Get specific submission
- `PATCH /api/submissions/{id}/status` - Update status

## Frontend Integration

The form in `index.html` is already configured. It will:
- Show loading spinner while submitting
- Display success message inline
- Show error message if fails
- Keep user on same page (no redirect)

## Troubleshooting

### "SMTP Authentication Error"
- Verify you're using Gmail App Password (not regular password)
- Enable 2FA on Google account first
- Generate App Password at: https://myaccount.google.com/apppasswords

### "CORS Error"
- Check `ALLOWED_ORIGINS` in `main.py`
- Add your domain to the list

### "Rate Limit Exceeded"
- Wait 1 hour or adjust `RATE_LIMIT_REQUESTS` in `.env`

### Database locked
- Check file permissions: `ls -la *.db`
- Ensure only one instance is running

## Next Steps

1. **Production Deployment**: See `DEPLOYMENT.md`
2. **Monitor Submissions**: Use admin API endpoints
3. **Backup Database**: Set up automated backups
4. **Add Monitoring**: Configure uptime monitoring

## Support

- Email: consultingbytriplec@gmail.com
- Phone: (509) 903-6285
- Docs: See `README.md` for detailed documentation
