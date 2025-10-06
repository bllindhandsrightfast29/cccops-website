#!/bin/bash

echo "🚀 Deploying Triple C Consulting Website to GitHub Pages..."
echo ""

# Initialize git repo
git init

# Add all files
git add .

# Create initial commit
git commit -m "🎯 Triple C Consulting - Initial deployment

- Professional defense contractor website
- ATAK, UAV, 3D printing, training capabilities
- Capsule Corp inspired C³ branding
- Dark theme with tactical design
- Contact: consultingbytriplec@gmail.com, (509) 903-6285"

# Rename branch to main
git branch -M main

# Add remote
git remote add origin https://github.com/bllindhandsrightfast29/bllindhandsrightfast29.github.io.git

# Push to GitHub
echo ""
echo "📤 Pushing to GitHub..."
git push -u origin main

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Your site will be live at:"
echo "👉 https://bllindhandsrightfast29.github.io"
echo ""
echo "Next steps:"
echo "1. Go to https://github.com/bllindhandsrightfast29/bllindhandsrightfast29.github.io/settings/pages"
echo "2. Verify Pages is enabled (should auto-enable)"
echo "3. Wait 60 seconds and visit your site"
echo ""
