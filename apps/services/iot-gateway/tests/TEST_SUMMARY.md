# IoT Gateway - Comprehensive Test Suite

## Overview

This directory contains comprehensive test coverage for the SAHOOL IoT Gateway service. The test suite includes **143 test functions** organized into **43 test classes** across 4 main test files, providing thorough validation of all IoT gateway functionality.

## Test Files

### 1. test_iot_api.py (529 lines, 19KB)
**FastAPI Endpoint Testing**

Tests all HTTP API endpoints including health checks, sensor readings, device management, and field operations.

**Test Classes:**
- `TestHealthEndpoints` - Health check and readiness endpoints
- `TestSensorEndpoints` - Sensor reading submission (single and batch)
- `TestDeviceEndpoints` - Device registration, retrieval, status, and deletion
- `TestFieldEndpoints` - Field-level device and reading queries
- `TestStatsEndpoint` - Gateway statistics
- `TestValidation` - Request validation and tenant isolation
- `TestAsyncEndpoints` - Async client behavior

**Key Features Tested:**
- ✅ Health check endpoints (`/health`, `/healthz`)
- ✅ Sensor reading submission (`POST /sensor/reading`)
- ✅ Batch sensor readings (`POST /sensor/batch`)
- ✅ Device registration (`POST /device/register`)
- ✅ Device CRUD operations (get, list, delete)
- ✅ Device status tracking
- ✅ Field-level queries
- ✅ Request validation and error handling
- ✅ Tenant isolation security
- ✅ Publisher unavailability handling
- ✅ Value range validation
- ✅ Async client testing with httpx

### 2. test_sensor_data.py (833 lines, 28KB)
**Sensor Data Normalization Testing**

Comprehensive tests for sensor data normalization, format conversion, and validation.

**Test Classes:**
- `TestNormalizedReading` - NormalizedReading dataclass
- `TestBasicNormalization` - Standard payload normalization
- `TestSensorTypeNormalization` - Sensor type alias mapping (30+ aliases)
- `TestUnitNormalization` - Unit conversion and standardization
- `TestDefaultUnits` - Default unit assignment
- `TestMetadataHandling` - Battery, RSSI, and custom metadata
- `TestTimestampHandling` - ISO timestamps, Unix timestamps, auto-generation
- `TestTopicExtraction` - MQTT topic parsing
- `TestBatchNormalization` - Multi-sensor batch processing
- `TestErrorHandling` - Validation and error cases
- `TestRealWorldPayloads` - Real-world sensor formats
- `TestEdgeCases` - Boundary conditions and special cases

**Key Features Tested:**
- ✅ Standard and compact payload formats
- ✅ Sensor type alias mapping (soil_moisture, temperature, EC, etc.)
- ✅ Unit normalization (%, °C, mS/cm, etc.)
- ✅ Default unit assignment per sensor type
- ✅ Battery and RSSI metadata extraction
- ✅ Timestamp parsing (ISO, Unix, auto-generation)
- ✅ MQTT topic parsing and extraction
- ✅ Batch reading normalization
- ✅ Error handling for invalid JSON, missing fields
- ✅ Real-world payload formats (LoRaWAN, weather stations)
- ✅ Edge cases (zero values, negative values, Unicode)

### 3. test_device_management.py (841 lines, 27KB)
**Device Registry and Management Testing**

Comprehensive tests for device lifecycle management, status tracking, and registry operations.

**Test Classes:**
- `TestDevice` - Device dataclass and online/offline detection
- `TestDeviceStatus` - Status enum values
- `TestDeviceType` - Device type enum values
- `TestDeviceRegistration` - Device registration and updates
- `TestDeviceRetrieval` - Device queries (by ID, field, tenant, type)
- `TestDeviceStatusTracking` - Status updates and battery monitoring
- `TestOfflineDeviceDetection` - Offline device detection
- `TestDeviceDeletion` - Device removal
- `TestRegistryStatistics` - Registry stats and metrics
- `TestAutoRegistration` - Auto-registration and type inference
- `TestRegistrySingleton` - Singleton pattern
- `TestConcurrentOperations` - Concurrent access patterns
- `TestEdgeCases` - Boundary conditions

**Key Features Tested:**
- ✅ Device registration with required and optional fields
- ✅ Device updates and field changes
- ✅ Device retrieval by ID, field, tenant, and type
- ✅ Online/offline status detection
- ✅ Last seen timestamp tracking
- ✅ Battery level monitoring and low battery warnings
- ✅ Signal strength (RSSI) tracking
- ✅ Last reading storage
- ✅ Offline device detection (configurable timeout)
- ✅ Device deletion
- ✅ Registry statistics (total, online, offline, by type)
- ✅ Auto-registration from first MQTT message
- ✅ Device type inference from sensor type
- ✅ Singleton registry pattern
- ✅ Concurrent operations
- ✅ Unicode support in device names

### 4. test_mqtt_handler.py (781 lines, 25KB)
**MQTT Message Handling Testing**

Comprehensive tests for MQTT connectivity, message processing, and error recovery.

**Test Classes:**
- `TestMqttMessage` - MqttMessage dataclass
- `TestMqttClient` - MQTT client connectivity
- `TestMockMqttClient` - Mock client for testing
- `TestMqttMessageHandling` - Message processing logic
- `TestMqttTopicPatterns` - Topic pattern matching
- `TestMqttSubscription` - Subscription handling
- `TestMqttReconnection` - Reconnection logic
- `TestMqttIntegration` - End-to-end integration tests
- `TestMqttSecurity` - Authentication and authorization
- `TestMqttPerformance` - High-frequency and large payloads
- `TestMqttErrorRecovery` - Error recovery mechanisms

**Key Features Tested:**
- ✅ MQTT client initialization and configuration
- ✅ MQTT connection (success and failure)
- ✅ MQTT publish with QoS levels (0, 1, 2)
- ✅ MQTT subscribe with wildcards (#, +)
- ✅ Message handler execution
- ✅ Mock MQTT client for testing
- ✅ Message queue processing
- ✅ Valid and invalid JSON payloads
- ✅ Registered vs unregistered devices
- ✅ Auto-registration on MQTT message
- ✅ Out-of-range value rejection
- ✅ Metadata extraction (battery, RSSI)
- ✅ Topic pattern matching
- ✅ Subscription error handling
- ✅ Reconnection on connection loss
- ✅ End-to-end message flow (MQTT → NATS)
- ✅ Batch processing multiple sensors
- ✅ MQTT authentication (username/password)
- ✅ Device authorization validation
- ✅ High-frequency message handling
- ✅ Large payload handling
- ✅ Malformed message recovery
- ✅ Handler exception recovery

## Running the Tests

### Prerequisites

Install required dependencies:

```bash
cd /home/user/sahool-unified-v15-idp/apps/services/iot-gateway
pip install -r requirements.txt
```

The requirements.txt includes:
- pytest==8.3.4
- pytest-asyncio==0.24.0
- pytest-cov==4.1.0
- pytest-mock==3.12.0
- fastapi==0.115.5
- httpx==0.28.1

### Run All Tests

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=src --cov-report=html --cov-report=term
```

### Run Specific Test Files

```bash
# API tests
pytest tests/test_iot_api.py -v

# Sensor data normalization tests
pytest tests/test_sensor_data.py -v

# Device management tests
pytest tests/test_device_management.py -v

# MQTT handler tests
pytest tests/test_mqtt_handler.py -v
```

### Run Specific Test Classes

```bash
# Test health endpoints only
pytest tests/test_iot_api.py::TestHealthEndpoints -v

# Test sensor normalization only
pytest tests/test_sensor_data.py::TestBasicNormalization -v

# Test device registration only
pytest tests/test_device_management.py::TestDeviceRegistration -v

# Test MQTT client only
pytest tests/test_mqtt_handler.py::TestMqttClient -v
```

### Run Specific Test Functions

```bash
# Test single health check
pytest tests/test_iot_api.py::TestHealthEndpoints::test_health_simple -v

# Test sensor reading submission
pytest tests/test_iot_api.py::TestSensorEndpoints::test_post_sensor_reading_success -v

# Test device registration
pytest tests/test_device_management.py::TestDeviceRegistration::test_register_new_device -v

# Test MQTT message handling
pytest tests/test_mqtt_handler.py::TestMqttMessageHandling::test_handle_valid_mqtt_message -v
```

### Run Tests with Markers

```bash
# Run only async tests
pytest tests/ -k "async" -v

# Run only integration tests
pytest tests/test_mqtt_handler.py::TestMqttIntegration -v

# Run only security tests
pytest tests/test_mqtt_handler.py::TestMqttSecurity -v
```

## Test Coverage Summary

### API Endpoints
- ✅ All HTTP endpoints tested
- ✅ Request validation
- ✅ Error handling
- ✅ Async client support
- ✅ Tenant isolation

### Sensor Data Processing
- ✅ 30+ sensor type aliases
- ✅ 15+ unit conversions
- ✅ Multiple payload formats
- ✅ Metadata extraction
- ✅ Timestamp handling
- ✅ Batch processing

### Device Management
- ✅ Full CRUD operations
- ✅ Status tracking
- ✅ Battery monitoring
- ✅ Offline detection
- ✅ Auto-registration
- ✅ Type inference

### MQTT Integration
- ✅ Client connectivity
- ✅ Message processing
- ✅ Topic patterns
- ✅ QoS levels
- ✅ Error recovery
- ✅ Authentication
- ✅ Performance testing

## Test Statistics

| Metric | Value |
|--------|-------|
| **Total Test Files** | 4 |
| **Total Test Classes** | 43 |
| **Total Test Functions** | 143 |
| **Total Lines of Code** | ~3,000 |
| **Coverage Areas** | API, Sensors, Devices, MQTT |

## Key Testing Features

### Mocking Strategy
- NATS client mocked for all tests
- MQTT broker mocked with MockMqttClient
- Registry and publisher fixtures for isolation
- Async mock support for FastAPI endpoints

### Test Fixtures
- `test_client` - FastAPI TestClient
- `mock_registry` - Populated DeviceRegistry
- `mock_publisher` - Mocked IoTPublisher
- `populated_registry` - Registry with test data

### Async Testing
- All async endpoints tested with pytest-asyncio
- AsyncClient for real async behavior
- Mock async functions for NATS/MQTT

### Error Handling
- Invalid JSON payloads
- Missing required fields
- Out-of-range values
- Unregistered devices
- Network failures
- Malformed messages

### Security Testing
- Tenant isolation validation
- Device authorization checks
- MQTT authentication
- Field-level access control

## Integration with CI/CD

These tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run IoT Gateway Tests
  run: |
    cd apps/services/iot-gateway
    pip install -r requirements.txt
    pytest tests/ -v --cov=src --cov-report=xml

- name: Upload Coverage
  uses: codecov/codecov-action@v3
  with:
    files: ./coverage.xml
```

## Test Maintenance

### Adding New Tests
1. Follow existing test class patterns
2. Use descriptive test function names (test_verb_noun_condition)
3. Include docstrings for complex tests
4. Mock external dependencies (NATS, MQTT)
5. Use fixtures for common setup

### Best Practices
- ✅ One assertion focus per test
- ✅ Clear test names describing behavior
- ✅ Mock external services
- ✅ Test both success and failure cases
- ✅ Include edge cases and boundary conditions
- ✅ Use pytest fixtures for reusable setup
- ✅ Test async code with pytest-asyncio

## Troubleshooting

### Common Issues

**Import Errors:**
```bash
# Ensure PYTHONPATH includes the project root
export PYTHONPATH=/home/user/sahool-unified-v15-idp:$PYTHONPATH
```

**Async Test Warnings:**
```bash
# Ignore async warnings
pytest tests/ -W ignore::DeprecationWarning
```

**NATS/MQTT Connection Errors:**
- Tests mock these services, no real brokers needed
- Check that mocking is applied before imports

## Contributing

When adding new features to the IoT Gateway:
1. Write tests first (TDD approach)
2. Ensure tests cover success and failure cases
3. Update this README with new test information
4. Run full test suite before committing
5. Maintain >90% code coverage

## Related Documentation

- [IoT Gateway README](../README.md)
- [MQTT Client Documentation](../src/mqtt_client.py)
- [Device Registry Documentation](../src/registry.py)
- [Sensor Normalizer Documentation](../src/normalizer.py)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pytest Documentation](https://docs.pytest.org/)

---

**Created:** January 2026
**Version:** 16.0.0
**Maintainer:** SAHOOL Platform Team
