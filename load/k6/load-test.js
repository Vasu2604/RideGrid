import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const rideCreationDuration = new Trend('ride_creation_duration');
const ridesCreated = new Counter('rides_created');

// Test configuration
export const options = {
  stages: [
    { duration: '30s', target: 50 },   // Ramp up to 50 users
    { duration: '1m', target: 100 },   // Ramp up to 100 users
    { duration: '2m', target: 100 },   // Stay at 100 users
    { duration: '1m', target: 200 },   // Spike to 200 users
    { duration: '1m', target: 200 },   // Stay at 200 users
    { duration: '30s', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<250'], // 95% of requests must complete below 250ms
    http_req_failed: ['rate<0.01'],   // Error rate must be less than 1%
    errors: ['rate<0.01'],
  },
};

const API_BASE_URL = __ENV.API_URL || 'http://localhost:8001';

function getRandomLocation() {
  // San Francisco area coordinates
  const baseLat = 37.7749;
  const baseLon = -122.4194;
  
  return {
    latitude: baseLat + (Math.random() - 0.5) * 0.1,
    longitude: baseLon + (Math.random() - 0.5) * 0.1,
  };
}

export default function () {
  const origin = getRandomLocation();
  const destination = getRandomLocation();

  const payload = JSON.stringify({
    rider_id: `rider_${__VU}_${__ITER}`,
    origin: origin,
    destination: destination,
    ride_type: 'ECONOMY',
    passenger_count: Math.floor(Math.random() * 4) + 1,
    payment_method_id: `pm_${__VU}`,
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
      'X-Client-ID': `k6-test-${__VU}`,
    },
  };

  // Create ride
  const createStart = new Date();
  const createRes = http.post(`${API_BASE_URL}/api/rides`, payload, params);
  const createDuration = new Date() - createStart;

  const createSuccess = check(createRes, {
    'ride created successfully': (r) => r.status === 200,
    'has ride_id': (r) => JSON.parse(r.body).ride_id !== undefined,
  });

  errorRate.add(!createSuccess);
  rideCreationDuration.add(createDuration);

  if (createSuccess) {
    ridesCreated.add(1);
    const ride = JSON.parse(createRes.body);

    // Get ride details
    const getRes = http.get(`${API_BASE_URL}/api/rides/${ride.ride_id}`, params);
    check(getRes, {
      'ride retrieved successfully': (r) => r.status === 200,
    });

    // 10% chance to cancel ride
    if (Math.random() < 0.1) {
      const cancelRes = http.post(
        `${API_BASE_URL}/api/rides/${ride.ride_id}/cancel?reason=Test`,
        null,
        params
      );
      check(cancelRes, {
        'ride cancelled successfully': (r) => r.status === 200,
      });
    }
  }

  sleep(Math.random() * 2); // Random sleep between 0-2 seconds
}

export function handleSummary(data) {
  return {
    '/tmp/k6-summary.json': JSON.stringify(data),
    stdout: textSummary(data, { indent: ' ', enableColors: true }),
  };
}

function textSummary(data, options) {
  const indent = options.indent || '';
  const colors = options.enableColors;

  let summary = '\n' + indent + '=== K6 Load Test Summary ===' + '\n\n';

  // HTTP metrics
  summary += indent + 'HTTP Metrics:' + '\n';
  summary += indent + `  Requests: ${data.metrics.http_reqs.values.count}` + '\n';
  summary += indent + `  Failed: ${data.metrics.http_req_failed.values.rate * 100}%` + '\n';
  summary += indent + `  Duration (avg): ${data.metrics.http_req_duration.values.avg.toFixed(2)}ms` + '\n';
  summary += indent + `  Duration (p95): ${data.metrics.http_req_duration.values['p(95)'].toFixed(2)}ms` + '\n';
  summary += indent + `  Duration (p99): ${data.metrics.http_req_duration.values['p(99)'].toFixed(2)}ms` + '\n\n';

  // Custom metrics
  summary += indent + 'Custom Metrics:' + '\n';
  summary += indent + `  Rides Created: ${data.metrics.rides_created.values.count}` + '\n';
  summary += indent + `  Error Rate: ${(data.metrics.errors.values.rate * 100).toFixed(2)}%` + '\n';
  summary += indent + `  Ride Creation (avg): ${data.metrics.ride_creation_duration.values.avg.toFixed(2)}ms` + '\n\n';

  // Thresholds
  summary += indent + 'Thresholds:' + '\n';
  for (const [name, threshold] of Object.entries(data.thresholds)) {
    const passed = threshold.ok ? '✓' : '✗';
    summary += indent + `  ${passed} ${name}` + '\n';
  }

  return summary;
}





