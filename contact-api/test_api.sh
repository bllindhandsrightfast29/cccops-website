#!/bin/bash
# Test script for Contact API

API_URL="${1:-http://localhost:8000}"

echo "==================================="
echo "Testing Contact API"
echo "API URL: $API_URL"
echo "==================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test 1: Health check
echo ""
echo "Test 1: Health Check"
echo "-----------------------------------"
response=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/health")
if [ "$response" -eq 200 ]; then
    echo -e "${GREEN}✓ PASSED${NC} - Health check (HTTP $response)"
else
    echo -e "${RED}✗ FAILED${NC} - Health check (HTTP $response)"
fi

# Test 2: Root endpoint
echo ""
echo "Test 2: Root Endpoint"
echo "-----------------------------------"
response=$(curl -s "$API_URL/")
if echo "$response" | grep -q "Triple C Contact API"; then
    echo -e "${GREEN}✓ PASSED${NC} - Root endpoint returns correct service name"
else
    echo -e "${RED}✗ FAILED${NC} - Root endpoint response incorrect"
fi

# Test 3: Valid contact submission
echo ""
echo "Test 3: Valid Contact Submission"
echo "-----------------------------------"
response=$(curl -s -X POST "$API_URL/api/contact" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "organization": "Test Corp",
    "message": "This is a test message from the automated test script."
  }')

if echo "$response" | grep -q '"success":true'; then
    submission_id=$(echo "$response" | grep -o '"submission_id":[0-9]*' | grep -o '[0-9]*')
    echo -e "${GREEN}✓ PASSED${NC} - Contact submission successful (ID: $submission_id)"
else
    echo -e "${RED}✗ FAILED${NC} - Contact submission failed"
    echo "Response: $response"
fi

# Test 4: Invalid email
echo ""
echo "Test 4: Invalid Email Validation"
echo "-----------------------------------"
response=$(curl -s -X POST "$API_URL/api/contact" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "invalid-email",
    "message": "Test message"
  }')

if echo "$response" | grep -q "detail"; then
    echo -e "${GREEN}✓ PASSED${NC} - Invalid email rejected"
else
    echo -e "${RED}✗ FAILED${NC} - Invalid email accepted (should be rejected)"
fi

# Test 5: Missing required fields
echo ""
echo "Test 5: Missing Required Fields"
echo "-----------------------------------"
response=$(curl -s -X POST "$API_URL/api/contact" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User"
  }')

if echo "$response" | grep -q "detail"; then
    echo -e "${GREEN}✓ PASSED${NC} - Missing fields rejected"
else
    echo -e "${RED}✗ FAILED${NC} - Missing fields accepted (should be rejected)"
fi

# Test 6: Honeypot spam protection
echo ""
echo "Test 6: Honeypot Spam Protection"
echo "-----------------------------------"
response=$(curl -s -X POST "$API_URL/api/contact" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Spam Bot",
    "email": "spam@example.com",
    "message": "Spam message",
    "_gotcha": "spam-bot-value"
  }')

if echo "$response" | grep -q '"success":true'; then
    echo -e "${GREEN}✓ PASSED${NC} - Honeypot returns success (to fool bots)"
else
    echo -e "${RED}✗ FAILED${NC} - Honeypot handling incorrect"
fi

# Test 7: Admin endpoints (requires API key)
echo ""
echo "Test 7: Admin Authentication"
echo "-----------------------------------"
response=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/api/submissions")
if [ "$response" -eq 422 ] || [ "$response" -eq 401 ]; then
    echo -e "${GREEN}✓ PASSED${NC} - Admin endpoint requires authentication (HTTP $response)"
else
    echo -e "${RED}✗ FAILED${NC} - Admin endpoint should require authentication (HTTP $response)"
fi

# Test 8: CORS headers
echo ""
echo "Test 8: CORS Headers"
echo "-----------------------------------"
response=$(curl -s -I -X OPTIONS "$API_URL/api/contact" -H "Origin: https://cccops.com")
if echo "$response" | grep -q "Access-Control-Allow-Origin"; then
    echo -e "${GREEN}✓ PASSED${NC} - CORS headers present"
else
    echo -e "${RED}✗ FAILED${NC} - CORS headers missing"
fi

# Summary
echo ""
echo "==================================="
echo "Test Suite Complete"
echo "==================================="
echo ""
echo "NOTE: Email sending is not tested by this script."
echo "To test email functionality, check your inbox after running Test 3."
echo ""
