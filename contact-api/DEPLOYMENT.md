# Deployment Guide - Contact API

This guide covers deploying the Triple C Contact API to production.

## Pre-Deployment Checklist

- [ ] Configure `.env` file with production credentials
- [ ] Generate secure API key for admin endpoints
- [ ] Set up Gmail App Password for SMTP
- [ ] Update API URL in frontend JavaScript
- [ ] Test locally with production-like setup
- [ ] Prepare SSL/TLS certificates

## Environment Setup

### 1. Generate Secure API Key

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy this key to `.env` as `ADMIN_API_KEY`

### 2. Configure SMTP (Gmail)

1. Enable 2-Factor Authentication on Google Account
2. Visit: https://myaccount.google.com/apppasswords
3. Create App Password for "Mail"
4. Add to `.env`:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
FROM_EMAIL=your-email@gmail.com
OWNER_EMAIL=consultingbytriplec@gmail.com
```

### 3. Update Frontend API URL

Edit `/Users/247takadminstator/LLM/projects/cccops-website/js/script-v2.js`:

```javascript
// Change this line:
const apiUrl = 'http://localhost:8000/api/contact';

// To your production URL:
const apiUrl = 'https://api.cccops.com/api/contact';
```

## Deployment Options

## Option 1: VPS Deployment (Recommended for Full Control)

### Requirements
- Ubuntu 20.04+ or similar Linux server
- Root or sudo access
- Domain name pointed to server IP

### Step 1: Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip -y

# Install Nginx
sudo apt install nginx -y

# Install Supervisor (process manager)
sudo apt install supervisor -y
```

### Step 2: Application Setup

```bash
# Create application directory
sudo mkdir -p /var/www/contact-api
cd /var/www/contact-api

# Copy application files
sudo cp -r /path/to/contact-api/* .

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
sudo nano .env
# Paste your production environment variables

# Set permissions
sudo chown -R www-data:www-data /var/www/contact-api
sudo chmod 755 /var/www/contact-api
```

### Step 3: Supervisor Configuration

Create `/etc/supervisor/conf.d/contact-api.conf`:

```ini
[program:contact-api]
command=/var/www/contact-api/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 --workers 4
directory=/var/www/contact-api
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/contact-api.log
environment=ENV="production"
```

Start the service:

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start contact-api
```

### Step 4: Nginx Configuration

Create `/etc/nginx/sites-available/contact-api`:

```nginx
server {
    listen 80;
    server_name api.cccops.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/contact-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Step 5: SSL with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d api.cccops.com

# Auto-renewal is configured automatically
```

### Step 6: Firewall

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

---

## Option 2: Docker Deployment

### Build and Run

```bash
cd contact-api

# Build image
docker build -t cccops-contact-api .

# Run container
docker run -d \
  --name contact-api \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  --env-file .env \
  --restart unless-stopped \
  cccops-contact-api
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  contact-api:
    build: .
    container_name: contact-api
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    env_file:
      - .env
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

Run:

```bash
docker-compose up -d
```

---

## Option 3: Cloud Platform Deployment

### Railway.app

1. Sign up at https://railway.app
2. Click "New Project" → "Deploy from GitHub"
3. Connect your repository
4. Add environment variables in Settings
5. Railway will auto-deploy

### Render.com

1. Sign up at https://render.com
2. Click "New" → "Web Service"
3. Connect repository
4. Configure:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables

### DigitalOcean App Platform

1. Sign up at https://cloud.digitalocean.com
2. Create App → GitHub
3. Select repository
4. Configure build settings
5. Add environment variables

---

## Post-Deployment

### 1. Test the API

```bash
# Health check
curl https://api.cccops.com/health

# Test submission
curl -X POST https://api.cccops.com/api/contact \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "message": "Test message"
  }'
```

### 2. Test Admin Endpoints

```bash
curl -H "X-API-Key: your-api-key" \
  https://api.cccops.com/api/submissions
```

### 3. Monitor Logs

```bash
# Supervisor logs
sudo tail -f /var/log/contact-api.log

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 4. Database Backups

Set up automated backups:

```bash
# Create backup script
sudo nano /usr/local/bin/backup-contact-db.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/contact-api"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
cp /var/www/contact-api/contact_submissions.db \
   $BACKUP_DIR/contact_submissions_$DATE.db

# Keep only last 30 days
find $BACKUP_DIR -name "*.db" -mtime +30 -delete
```

```bash
# Make executable
sudo chmod +x /usr/local/bin/backup-contact-db.sh

# Add to crontab (daily at 2 AM)
sudo crontab -e
0 2 * * * /usr/local/bin/backup-contact-db.sh
```

---

## Security Hardening

### 1. Rate Limiting (Additional Layer)

Use Nginx rate limiting:

```nginx
http {
    limit_req_zone $binary_remote_addr zone=contact:10m rate=5r/m;

    server {
        location /api/contact {
            limit_req zone=contact burst=2;
            proxy_pass http://127.0.0.1:8000;
        }
    }
}
```

### 2. Fail2Ban

Protect against brute force:

```bash
sudo apt install fail2ban -y

# Create custom filter
sudo nano /etc/fail2ban/filter.d/contact-api.conf
```

```ini
[Definition]
failregex = ^.*"POST /api/contact.*" 429.*$
ignoreregex =
```

```bash
# Configure jail
sudo nano /etc/fail2ban/jail.local
```

```ini
[contact-api]
enabled = true
port = http,https
filter = contact-api
logpath = /var/log/nginx/access.log
maxretry = 5
bantime = 3600
```

### 3. Database Encryption

Enable SQLite encryption for sensitive data (optional):

```bash
pip install sqlcipher3
```

---

## Monitoring & Maintenance

### Set Up Monitoring

1. **Uptime Monitoring**: UptimeRobot (https://uptimerobot.com)
2. **Application Monitoring**: Sentry (https://sentry.io)
3. **Server Monitoring**: Netdata or Prometheus

### Regular Maintenance

- Review logs weekly
- Update dependencies monthly
- Test backups quarterly
- Review security annually

---

## Troubleshooting

### API not responding
```bash
# Check service status
sudo supervisorctl status contact-api

# Check logs
sudo tail -f /var/log/contact-api.log

# Restart service
sudo supervisorctl restart contact-api
```

### Email not sending
```bash
# Test SMTP connection
python3 -c "
import smtplib
smtp = smtplib.SMTP('smtp.gmail.com', 587)
smtp.starttls()
smtp.login('your-email@gmail.com', 'your-app-password')
print('SMTP connection successful')
"
```

### Database locked errors
```bash
# Check file permissions
ls -la /var/www/contact-api/*.db

# Fix permissions
sudo chown www-data:www-data /var/www/contact-api/*.db
```

---

## Rollback Procedure

If deployment fails:

```bash
# Stop service
sudo supervisorctl stop contact-api

# Restore previous version
cd /var/www/contact-api
git checkout <previous-commit>

# Restart service
sudo supervisorctl start contact-api
```

---

## Support

For deployment assistance:
- Email: consultingbytriplec@gmail.com
- Phone: (509) 903-6285
