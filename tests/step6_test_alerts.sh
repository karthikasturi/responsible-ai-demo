#!/bin/bash
# Step 6: Test Alert System

echo "======================================="
echo "Step 6: Testing Alert System"
echo "======================================="

echo ""
echo "1. Checking current alert status..."
curl -s http://localhost:8000/alerts/stats | jq

echo ""
echo "2. Triggering quality alerts with low-quality responses..."
echo "Sending vague questions to trigger low relevance..."

for i in {1..12}
do
  curl -s -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d '{"message": "Tell me about stuff", "user_id": "test_user"}' \
    > /dev/null
  echo "Vague request $i sent"
  sleep 0.5
done

echo ""
echo "3. Checking for quality alerts..."
curl -s http://localhost:8000/alerts/history?limit=5 | jq

echo ""
echo "4. Triggering drift alert..."
curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Completely unrelated topic about cooking and recipes",
    "user_id": "test_user"
  }' | jq '.metadata.alerts'

echo ""
echo "5. Viewing alert history..."
curl -s http://localhost:8000/alerts/history | jq '.alerts[] | {type: .type, severity: .severity, message: .message}'

echo ""
echo "6. Alert statistics..."
curl -s http://localhost:8000/alerts/stats | jq

echo ""
echo "7. Checking alert log file..."
if [ -f /app/data/alerts.log ]; then
  echo "Recent alerts from file:"
  tail -5 /app/data/alerts.log | jq -r '.message'
else
  echo "Alert log file will be created when first alert is triggered"
fi

echo ""
echo "✅ Step 6 tests complete!"
echo ""
echo "Note: To test Slack/Email alerts:"
echo "1. Set SLACK_WEBHOOK_URL in .env"
echo "2. Set email credentials (SMTP_USER, SMTP_PASSWORD, ALERT_EMAIL)"
echo "3. Restart the application"
echo "4. Trigger alerts again"
