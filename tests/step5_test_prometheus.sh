#!/bin/bash
# Step 5: Test Prometheus Metrics

echo "======================================="
echo "Step 5: Testing Prometheus Metrics"
echo "======================================="

echo ""
echo "1. Generating traffic to create metrics..."
for i in {1..5}
do
  curl -s -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d "{\"message\": \"Question $i: What is MLOps?\", \"user_id\": \"user_$i\"}" \
    > /dev/null
  echo "Request $i sent"
done

echo ""
echo "2. Checking /metrics endpoint..."
echo "Sample metrics:"
curl -s http://localhost:8000/metrics | grep -E "^(llm_request_count|llm_quality_score|llm_drift_detected)" | head -10

echo ""
echo "3. Full metrics available at: http://localhost:8000/metrics"
echo ""
echo "4. Prometheus UI available at: http://localhost:9090"
echo "   Try these queries in Prometheus:"
echo "   - rate(llm_request_count[1m])"
echo "   - llm_quality_score"
echo "   - llm_drift_detected"
echo "   - histogram_quantile(0.95, llm_request_duration_seconds_bucket)"

echo ""
echo "5. Grafana available at: http://localhost:3000 (admin/admin)"
echo "   Dashboard: LLM Responsible AI Monitoring"

echo ""
echo "6. Example Prometheus queries:"
echo ""
echo "Request rate:"
curl -s 'http://localhost:9090/api/v1/query?query=rate(llm_request_count[1m])' | jq -r '.data.result[0].value[1]' 2>/dev/null || echo "Run more requests first"

echo ""
echo "✅ Step 5 tests complete!"
echo ""
echo "Next: Open Grafana at http://localhost:3000 to visualize metrics"
