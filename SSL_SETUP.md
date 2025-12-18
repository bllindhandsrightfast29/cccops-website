# SSL Certificate Setup for cccops.com

This guide covers setting up free SSL certificates from Let's Encrypt using Certbot for your cccops.com website.

## Prerequisites

- Ubuntu/Debian server with root/sudo access
- Domain (cccops.com) pointing to your server's IP address
- Nginx or Apache web server installed and running
- Port 80 and 443 open in your firewall

## Quick Setup

### Option 1: Automated Script

```bash
# SSH into your server
ssh your-server

# Navigate to the website directory
cd /path/to/cccops-website

# Make the script executable
chmod +x ssl-setup.sh

# Run the setup script
sudo ./ssl-setup.sh
```

### Option 2: Manual Setup

#### Step 1: SSH into Your Server

```bash
ssh your-server
```

#### Step 2: Update System Packages

```bash
sudo apt update
```

#### Step 3: Install Certbot

**For Nginx:**
```bash
sudo apt install certbot python3-certbot-nginx
```

**For Apache:**
```bash
sudo apt install certbot python3-certbot-apache
```

#### Step 4: Obtain SSL Certificate

**For Nginx:**
```bash
sudo certbot --nginx -d cccops.com -d www.cccops.com
```

**For Apache:**
```bash
sudo certbot --apache -d cccops.com -d www.cccops.com
```

#### Step 5: Follow the Prompts

Certbot will ask you a few questions:
- Enter your email address (for renewal notifications)
- Agree to the Terms of Service
- Choose whether to redirect HTTP to HTTPS (recommended: Yes)

#### Step 6: Verify Installation

Visit your website:
- https://cccops.com
- https://www.cccops.com

You should see a secure padlock icon in your browser!

## Certificate Auto-Renewal

Certbot automatically sets up certificate renewal. Test it with:

```bash
sudo certbot renew --dry-run
```

To manually renew (if needed):
```bash
sudo certbot renew
```

To check renewal timer status:
```bash
sudo systemctl status certbot.timer
```

## Troubleshooting

### Issue: Domain not pointing to server

**Solution:** Verify DNS records
```bash
# Check if domain points to your server
dig cccops.com
dig www.cccops.com
```

Make sure the A records point to your server's IP address.

### Issue: Port 80/443 blocked

**Solution:** Open firewall ports
```bash
# For UFW (Ubuntu Firewall)
sudo ufw allow 'Nginx Full'  # or 'Apache Full'
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw reload

# Verify
sudo ufw status
```

### Issue: Web server not running

**Solution:** Start web server
```bash
# For Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# For Apache
sudo systemctl start apache2  # or httpd on some systems
sudo systemctl enable apache2
```

### Issue: Certificate renewal fails

**Solution:** Check renewal logs
```bash
sudo certbot renew --dry-run --verbose
sudo journalctl -u certbot.timer
```

## GitHub Pages Configuration

If you're using GitHub Pages with a custom domain (which you are based on your CNAME file):

1. **In GitHub:**
   - Go to your repo settings → Pages
   - Enable "Enforce HTTPS"
   - GitHub automatically provisions SSL certificates for custom domains

2. **DNS Configuration:**
   - Make sure your domain's A records point to GitHub's IPs:
     ```
     185.199.108.153
     185.199.109.153
     185.199.110.153
     185.199.111.153
     ```
   - Or use a CNAME record pointing to: `bllindhandsrightfast29.github.io`

3. **Wait for SSL provisioning:**
   - GitHub can take up to 24 hours to provision SSL for custom domains
   - Check your repo's Pages settings to see SSL status

## Security Best Practices

1. **Force HTTPS Redirect:** Ensure all HTTP traffic redirects to HTTPS
2. **HSTS Header:** Consider adding HTTP Strict Transport Security
3. **Test Configuration:** Use https://www.ssllabs.com/ssltest/ to verify your SSL setup
4. **Monitor Expiration:** Set up monitoring for certificate expiration (though auto-renewal should handle this)

## Certificate Information

- **Provider:** Let's Encrypt
- **Validity:** 90 days
- **Auto-renewal:** Every 60 days (when 30 days remain)
- **Cost:** FREE
- **Supported domains:** cccops.com, www.cccops.com

## Additional Resources

- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [Certbot Documentation](https://certbot.eff.org/)
- [Nginx SSL Configuration](https://nginx.org/en/docs/http/configuring_https_servers.html)
- [Apache SSL Configuration](https://httpd.apache.org/docs/2.4/ssl/)

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review certbot logs: `sudo journalctl -u certbot`
3. Verify web server logs for errors

---

**Last Updated:** October 2025
**Domain:** cccops.com
**Contact:** consultingbytriplec@gmail.com
