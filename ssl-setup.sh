#!/bin/bash

# SSL Certificate Setup Script for cccops.com
# This script automates the installation of Let's Encrypt SSL certificates using Certbot

set -e  # Exit on error

echo "================================================================="
echo "  SSL Certificate Setup for cccops.com"
echo "================================================================="
echo ""

# Function to check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        echo "❌ This script must be run as root or with sudo"
        exit 1
    fi
}

# Function to detect web server
detect_web_server() {
    if command -v nginx &> /dev/null; then
        echo "nginx"
    elif command -v apache2 &> /dev/null || command -v httpd &> /dev/null; then
        echo "apache"
    else
        echo "unknown"
    fi
}

# Check for root privileges
check_root

# Detect web server
WEB_SERVER=$(detect_web_server)

echo "📋 Detected web server: $WEB_SERVER"
echo ""

# Update package list
echo "📦 Updating package list..."
apt update

# Install certbot based on web server
echo "🔧 Installing certbot..."
if [ "$WEB_SERVER" = "nginx" ]; then
    apt install -y certbot python3-certbot-nginx
    CERTBOT_CMD="certbot --nginx"
elif [ "$WEB_SERVER" = "apache" ]; then
    apt install -y certbot python3-certbot-apache
    CERTBOT_CMD="certbot --apache"
else
    echo "⚠️  Could not detect nginx or apache. Installing standalone certbot."
    apt install -y certbot
    echo ""
    echo "ℹ️  You'll need to manually configure your web server after obtaining the certificate."
    CERTBOT_CMD="certbot certonly --standalone"
fi

echo ""
echo "🔐 Obtaining SSL certificate for cccops.com..."
echo ""

# Get certificate for both www and non-www domains
$CERTBOT_CMD -d cccops.com -d www.cccops.com

echo ""
echo "✅ Certificate obtained successfully!"
echo ""

# Test auto-renewal
echo "🔄 Testing certificate auto-renewal..."
certbot renew --dry-run

echo ""
echo "================================================================="
echo "  ✅ SSL Setup Complete!"
echo "================================================================="
echo ""
echo "Your website should now be accessible via HTTPS:"
echo "  👉 https://cccops.com"
echo "  👉 https://www.cccops.com"
echo ""
echo "📋 Next steps:"
echo "  1. Test your SSL configuration: https://www.ssllabs.com/ssltest/"
echo "  2. Verify auto-renewal is working (certificates renew automatically)"
echo "  3. Update any hardcoded HTTP links to HTTPS"
echo ""
echo "🔄 Certificate auto-renewal:"
echo "  - Certificates automatically renew when they have 30 days or less remaining"
echo "  - Certbot sets up a systemd timer to check twice daily"
echo "  - Check renewal status: sudo certbot renew --dry-run"
echo ""
