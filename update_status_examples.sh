#!/bin/bash

# Script to update the status of some items on the dashboard.

API_BASE_URL="http://localhost:5000/api"

echo "Updating statuses..."

# Update "Main Build" to "passing"
echo "Updating Main Build..."
curl -X PUT -H "Content-Type: application/json" \
  -d '{"status": "passing", "message": "Build successful on commit abc1234", "url": "http://jenkins.example.com/builds/main/101"}' \
  "$API_BASE_URL/categories/Builds/items/Main%20Build"
echo ""

# Update "mars" to "down", "jupiter" to "running"
# These item names ("mars", "jupiter") do not have spaces, so no URL encoding needed for them.
# The category "Host Up/Down" is correctly encoded in its path segment.
echo "Updating Host: mars..."
curl -X PUT -H "Content-Type: application/json" \
  -d '{"status": "down", "message": "Host mars is unresponsive, ping failed.", "url": "http://monitoring.example.com/hosts/mars"}' \
  "$API_BASE_URL/categories/Host%20Up%2FDown/items/mars"
echo ""

echo "Updating Host: jupiter..."
curl -X PUT -H "Content-Type: application/json" \
  -d '{"status": "running", "message": "All systems normal.", "url": "http://monitoring.example.com/hosts/jupiter"}' \
  "$API_BASE_URL/categories/Host%20Up%2FDown/items/jupiter"
echo ""


# Update "Login Test" to "failing", "API Test" to "passing"
echo "Updating Test: Login Test..."
curl -X PUT -H "Content-Type: application/json" \
  -d '{"status": "failing", "message": "Login test failed: credentials expired.", "url": "http://tests.example.com/results/login/latest"}' \
  "$API_BASE_URL/categories/Tests/items/Login%20Test"
echo ""

echo "Updating Test: API Test..."
curl -X PUT -H "Content-Type: application/json" \
  -d '{"status": "passing", "message": "All API endpoints responding correctly.", "url": "http://tests.example.com/results/api/latest"}' \
  "$API_BASE_URL/categories/Tests/items/API%20Test"
echo ""


# Update "Core OS Services" to "running"
echo "Updating Operational System: Core OS Services..."
curl -X PUT -H "Content-Type: application/json" \
  -d '{"status": "running", "message": "Operational system services are stable.", "url": "http://status.example.com/os"}' \
  "$API_BASE_URL/categories/Operational%20Systems/items/Core%20OS%20Services"
echo ""


echo "Status updates complete."
echo "You might need to make this script executable: chmod +x update_status_examples.sh"
# To see the current state: curl http://localhost:5000/api/health
