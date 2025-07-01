#!/bin/bash

# Script to set up the initial dashboard with categories and items.
# All items will be in 'unknown' status by default upon creation via the API.

API_BASE_URL="http://localhost:5000/api"

echo "Creating categories..."
curl -X POST -H "Content-Type: application/json" -d '{"category_name": "Builds"}' $API_BASE_URL/categories
echo ""
curl -X POST -H "Content-Type: application/json" -d '{"category_name": "Tests"}' $API_BASE_URL/categories
echo ""
curl -X POST -H "Content-Type: application/json" -d '{"category_name": "Host Up/Down"}' $API_BASE_URL/categories
echo ""
curl -X POST -H "Content-Type: application/json" -d '{"category_name": "Operational Systems"}' $API_BASE_URL/categories
echo ""

echo "Adding items to 'Builds'..."
curl -X POST -H "Content-Type: application/json" -d '{"item_name": "Main Build"}' "$API_BASE_URL/categories/Builds/items"
echo ""
curl -X POST -H "Content-Type: application/json" -d '{"item_name": "Release Build"}' "$API_BASE_URL/categories/Builds/items"
echo ""

echo "Adding items to 'Tests'..."
curl -X POST -H "Content-Type: application/json" -d '{"item_name": "Login Test"}' "$API_BASE_URL/categories/Tests/items"
echo ""
curl -X POST -H "Content-Type: application/json" -d '{"item_name": "API Test"}' "$API_BASE_URL/categories/Tests/items"
echo ""
curl -X POST -H "Content-Type: application/json" -d '{"item_name": "Performance Test"}' "$API_BASE_URL/categories/Tests/items"
echo ""
curl -X POST -H "Content-Type: application/json" -d '{"item_name": "Security Scan"}' "$API_BASE_URL/categories/Tests/items"
echo ""

echo "Adding items to 'Host Up/Down'..."
curl -X POST -H "Content-Type: application/json" -d '{"item_name": "mars"}' "$API_BASE_URL/categories/Host Up%2FDown/items" # URL encode space
echo ""
curl -X POST -H "Content-Type: application/json" -d '{"item_name": "saturn"}' "$API_BASE_URL/categories/Host Up%2FDown/items"
echo ""
curl -X POST -H "Content-Type: application/json" -d '{"item_name": "jupiter"}' "$API_BASE_URL/categories/Host Up%2FDown/items"
echo ""

echo "Adding item to 'Operational Systems'..."
curl -X POST -H "Content-Type: application/json" -d '{"item_name": "Core OS Services"}' "$API_BASE_URL/categories/Operational Systems/items"
echo ""

echo "Setup complete. All items are initialized to 'unknown' status."
echo "You might need to make this script executable: chmod +x setup_dashboard.sh"
# To see the current state: curl http://localhost:5000/api/health
