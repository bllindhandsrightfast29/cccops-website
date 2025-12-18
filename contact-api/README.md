# Triple C Consulting - Contact Form API

Production-ready FastAPI backend for handling contact form submissions at cccops.com.

## Features

- **REST API** - FastAPI with automatic OpenAPI documentation
- **Email Notifications** - Professional HTML emails to owner and customers
- **SQLite Database** - Lightweight, reliable storage for submissions
- **Security**:
  - Rate limiting (5 requests per IP per hour)
  - Honeypot spam protection
  - CORS configuration for cccops.com
  - API key authentication for admin endpoints
- **Admin Panel** - API endpoints to view and manage submissions

## Quick Start

### 1. Installation

```bash
# Clone or navigate to the directory
cd contact-api

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
# SMTP Configuration (Gmail example)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-gmail-app-password
FROM_EMAIL=your-email@gmail.com
OWNER_EMAIL=consultingbytriplec@gmail.com

# Generate a secure API key
ADMIN_API_KEY=your-secure-random-key-here
```

**Important:** For Gmail, you must create an App Password:
1. Enable 2-Factor Authentication on your Google account
2. Go to https://myaccount.google.com/apppasswords
3. Generate an app password for "Mail"
4. Use that 16-character password in `SMTP_PASSWORD`

### 3. Run the Server

```bash
# Development mode (with auto-reload)
python main.py

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### 4. Test the API

```bash
# Health check
curl http://localhost:8000/health

# Submit a test contact form
curl -X POST http://localhost:8000/api/contact \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "organization": "Test Corp",
    "message": "This is a test message"
  }'
```

## API Documentation

Once running, visit:
- **Interactive API docs**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc

## API Endpoints

### Public Endpoints

#### POST /api/contact
Submit a contact form.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "organization": "Defense Corp",
  "message": "I'm interested in your mobile app development services."
}
```

**Response:**
```json
{
  "success": true,
  "message": "Thank you for your message. We'll be in touch within 24 hours.",
  "submission_id": 123
}
```

### Admin Endpoints (Require API Key)

All admin endpoints require the `X-API-Key` header:

```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/api/submissions
```

#### GET /api/submissions
Get all submissions with pagination.

**Query Parameters:**
- `limit` (default: 50) - Number of results
- `offset` (default: 0) - Pagination offset
- `status` (optional) - Filter by status: new, contacted, resolved, spam

**Example:**
```bash
curl -H "X-API-Key: your-api-key" \
  "http://localhost:8000/api/submissions?limit=10&status=new"
```

#### GET /api/submissions/{id}
Get a specific submission by ID.

#### PATCH /api/submissions/{id}/status
Update submission status.

**Request Body:**
```json
{
  "status": "contacted"
}
```

Valid statuses: `new`, `contacted`, `resolved`, `spam`

## Database

SQLite database with the following schema:

```sql
submissions (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  organization TEXT,
  message TEXT NOT NULL,
  created_at TEXT NOT NULL,
  ip_address TEXT NOT NULL,
  status TEXT DEFAULT 'new'
)
```

Database file: `contact_submissions.db`

## Security Features

### Rate Limiting
- 5 requests per IP address per hour
- Prevents spam and abuse
- Configurable in `.env`

### Honeypot Spam Protection
- Hidden `_gotcha` field catches bots
- Transparent to real users
- Auto-rejects spam silently

### CORS
- Configured for cccops.com domains
- Includes localhost for development
- Edit in `main.py` if needed

### API Key Authentication
- Admin endpoints require API key
- Pass via `X-API-Key` header
- Generate secure key: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

## Email Templates

Professional HTML email templates in `templates/`:

1. **owner_notification.html** - Notification to consultingbytriplec@gmail.com
2. **customer_confirmation.html** - Auto-reply to customer

Both templates are production-ready with:
- Responsive design
- Professional styling
- Brand consistency
- Clear call-to-actions

## Deployment

### Docker Deployment

Build the Docker image:

```bash
docker build -t cccops-contact-api .
```

Run the container:

```bash
docker run -d \
  --name contact-api \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  --env-file .env \
  cccops-contact-api
```

### Production Considerations

1. **Reverse Proxy**: Use Nginx or Caddy
2. **HTTPS**: Enable SSL/TLS (Let's Encrypt)
3. **Process Manager**: Use systemd or supervisor
4. **Monitoring**: Add logging and health checks
5. **Backups**: Regularly backup `contact_submissions.db`
6. **Environment Variables**: Never commit `.env` to git

### Example Nginx Configuration

```nginx
server {
    listen 80;
    server_name api.cccops.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Frontend Integration

Update your HTML form to use JavaScript instead of direct form submission:

```html
<form id="contact-form">
  <input type="text" name="name" required>
  <input type="email" name="email" required>
  <input type="text" name="organization">
  <textarea name="message" required></textarea>

  <!-- Honeypot -->
  <input type="text" name="_gotcha" style="display:none">

  <button type="submit">Send Message</button>
  <div id="form-status"></div>
  <div id="form-spinner" style="display:none">Sending...</div>
</form>

<script>
document.getElementById('contact-form').addEventListener('submit', async (e) => {
  e.preventDefault();

  const form = e.target;
  const formData = new FormData(form);
  const status = document.getElementById('form-status');
  const spinner = document.getElementById('form-spinner');

  // Show loading
  spinner.style.display = 'block';
  status.textContent = '';

  try {
    const response = await fetch('http://localhost:8000/api/contact', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(Object.fromEntries(formData))
    });

    const data = await response.json();

    if (response.ok) {
      status.textContent = data.message;
      status.style.color = 'green';
      form.reset();
    } else {
      throw new Error(data.detail || 'Submission failed');
    }
  } catch (error) {
    status.textContent = 'Error: ' + error.message;
    status.style.color = 'red';
  } finally {
    spinner.style.display = 'none';
  }
});
</script>
```

## Troubleshooting

### Email not sending
- Verify SMTP credentials in `.env`
- For Gmail, ensure you're using an App Password (not regular password)
- Check firewall allows outbound SMTP (port 587)
- Review logs for specific error messages

### CORS errors
- Ensure your frontend domain is in `ALLOWED_ORIGINS` in `main.py`
- Check browser console for specific CORS error

### Database errors
- Ensure write permissions for `contact_submissions.db`
- Check disk space
- Verify SQLite is properly installed

### Rate limiting issues
- Adjust `RATE_LIMIT_REQUESTS` in `.env`
- Clear rate limit cache (restart server)
- Check IP address detection (X-Forwarded-For header)

## Development

### Run tests
```bash
# Test database
python database.py

# Test email service (requires .env configured)
python email_service.py
```

### View logs
```bash
# Development mode shows logs in console
python main.py

# Production logs
tail -f /var/log/contact-api.log
```

## Support

For issues or questions:
- Email: consultingbytriplec@gmail.com
- Phone: (509) 903-6285
- Website: https://cccops.com

## License

Copyright 2025 Triple C Consulting. All rights reserved.
