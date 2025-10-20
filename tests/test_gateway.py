"""Integration tests for Gateway service."""

import pytest
import httpx
from hypothesis import given, strategies as st


class TestGatewayIntegration:
    """Integration tests for Gateway API."""

    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test health check endpoint."""
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8001/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_create_ride(self):
        """Test ride creation."""
        async with httpx.AsyncClient() as client:
            payload = {
                "rider_id": "test_rider_001",
                "origin": {"latitude": 37.7749, "longitude": -122.4194},
                "destination": {"latitude": 37.7849, "longitude": -122.4094},
                "ride_type": "ECONOMY",
                "passenger_count": 1,
                "payment_method_id": "pm_test_123",
            }

            response = await client.post("http://localhost:8001/api/rides", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert "ride_id" in data
            assert data["rider_id"] == "test_rider_001"
            assert data["status"] == "REQUESTED"

    @pytest.mark.asyncio
    async def test_get_ride(self):
        """Test get ride endpoint."""
        # First create a ride
        async with httpx.AsyncClient() as client:
            create_payload = {
                "rider_id": "test_rider_002",
                "origin": {"latitude": 37.7749, "longitude": -122.4194},
                "destination": {"latitude": 37.7849, "longitude": -122.4094},
                "ride_type": "ECONOMY",
                "passenger_count": 1,
                "payment_method_id": "pm_test_123",
            }

            create_response = await client.post(
                "http://localhost:8001/api/rides", json=create_payload
            )
            ride_id = create_response.json()["ride_id"]

            # Then get the ride
            get_response = await client.get(f"http://localhost:8001/api/rides/{ride_id}")
            assert get_response.status_code == 200
            data = get_response.json()
            assert data["ride_id"] == ride_id

    @pytest.mark.asyncio
    async def test_cancel_ride(self):
        """Test ride cancellation."""
        async with httpx.AsyncClient() as client:
            create_payload = {
                "rider_id": "test_rider_003",
                "origin": {"latitude": 37.7749, "longitude": -122.4194},
                "destination": {"latitude": 37.7849, "longitude": -122.4094},
                "ride_type": "ECONOMY",
                "passenger_count": 1,
                "payment_method_id": "pm_test_123",
            }

            create_response = await client.post(
                "http://localhost:8001/api/rides", json=create_payload
            )
            ride_id = create_response.json()["ride_id"]

            # Cancel the ride
            cancel_response = await client.post(
                f"http://localhost:8001/api/rides/{ride_id}/cancel",
                params={"reason": "Test cancellation"},
            )
            assert cancel_response.status_code == 200
            data = cancel_response.json()
            assert data["status"] == "CANCELLED"


class TestIdempotency:
    """Property-based tests for idempotency."""

    @given(
        rider_id=st.text(min_size=5, max_size=20),
        lat=st.floats(min_value=-90, max_value=90),
        lon=st.floats(min_value=-180, max_value=180),
    )
    @pytest.mark.asyncio
    async def test_duplicate_ride_creation_idempotent(self, rider_id, lat, lon):
        """Test that duplicate ride creations are idempotent."""
        async with httpx.AsyncClient() as client:
            payload = {
                "rider_id": rider_id,
                "origin": {"latitude": lat, "longitude": lon},
                "destination": {"latitude": lat + 0.01, "longitude": lon + 0.01},
                "ride_type": "ECONOMY",
                "passenger_count": 1,
                "payment_method_id": "pm_test_123",
            }

            # Send same request twice
            response1 = await client.post(
                "http://localhost:8001/api/rides",
                json=payload,
                headers={"X-Idempotency-Key": "test-key-123"},
            )
            response2 = await client.post(
                "http://localhost:8001/api/rides",
                json=payload,
                headers={"X-Idempotency-Key": "test-key-123"},
            )

            # Should get same ride_id
            assert response1.status_code == 200
            assert response2.status_code == 200
            assert response1.json()["ride_id"] == response2.json()["ride_id"]


class TestRateLimiting:
    """Tests for rate limiting."""

    @pytest.mark.asyncio
    async def test_rate_limit_exceeded(self):
        """Test that rate limiting works."""
        async with httpx.AsyncClient() as client:
            payload = {
                "rider_id": "test_rider_rate_limit",
                "origin": {"latitude": 37.7749, "longitude": -122.4194},
                "destination": {"latitude": 37.7849, "longitude": -122.4094},
                "ride_type": "ECONOMY",
                "passenger_count": 1,
                "payment_method_id": "pm_test_123",
            }

            # Send many requests quickly
            responses = []
            for _ in range(150):  # Exceed rate limit of 100/min
                response = await client.post(
                    "http://localhost:8001/api/rides",
                    json=payload,
                    headers={"X-Client-ID": "rate-limit-test"},
                )
                responses.append(response)

            # Should eventually get 429 Too Many Requests
            status_codes = [r.status_code for r in responses]
            assert 429 in status_codes





