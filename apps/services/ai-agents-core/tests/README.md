# AI Agents Core - Test Suite

# مجموعة اختبارات نواة وكلاء الذكاء الاصطناعي

Comprehensive test suite for the AI Agents Core service.

## Overview

This test suite provides comprehensive coverage for:

- **Agent orchestration logic** - Multi-agent coordination and decision making
- **Request/response validation** - API endpoint validation
- **Error handling** - Graceful error recovery
- **Rate limiting** - API rate limit enforcement
- **Integration workflows** - End-to-end agent workflows

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures and configuration
├── unit/                    # Unit tests for individual components
│   ├── test_base_agent.py          # Base agent functionality
│   ├── test_iot_agent.py           # IoT edge agent
│   ├── test_disease_expert_agent.py # Disease expert agent
│   ├── test_coordinator_agent.py    # Coordinator agent
│   └── test_api_endpoints.py       # API endpoints
├── integration/             # Integration tests
│   ├── test_agent_workflows.py     # Multi-agent workflows
│   └── test_api_integration.py     # API integration tests
└── mocks/                   # Mock utilities
    ├── __init__.py
    └── ai_service_mocks.py         # AI service mocks
```

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Agent tests
pytest -m agent

# API tests
pytest -m api

# Fast tests only (exclude slow tests)
pytest -m "not slow"
```

### Run Specific Test Files

```bash
# Test base agent
pytest tests/unit/test_base_agent.py

# Test IoT agent
pytest tests/unit/test_iot_agent.py

# Test coordinator
pytest tests/unit/test_coordinator_agent.py

# Test API endpoints
pytest tests/unit/test_api_endpoints.py

# Test workflows
pytest tests/integration/test_agent_workflows.py
```

### Run with Coverage

```bash
# Generate coverage report
pytest --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Run with Verbose Output

```bash
pytest -v
```

## Test Markers

Tests are organized using pytest markers:

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.agent` - Agent-related tests
- `@pytest.mark.coordinator` - Coordinator agent tests
- `@pytest.mark.specialist` - Specialist agent tests
- `@pytest.mark.edge` - Edge agent tests
- `@pytest.mark.api` - API endpoint tests
- `@pytest.mark.slow` - Slow-running tests
- `@pytest.mark.mock` - Tests using mocked services
- `@pytest.mark.asyncio` - Async tests

## Test Coverage

### Base Agent Tests

- Agent initialization and lifecycle
- Perceive-Think-Act cycle
- State management
- Rule-based behavior
- Utility-based decision making
- Learning mechanisms
- Performance metrics
- Error handling

### IoT Agent Tests

- Sensor data processing
- Threshold detection
- Automated irrigation triggers
- Anomaly detection
- Trend analysis
- Edge response time
- Actuator control

### Disease Expert Agent Tests

- Disease diagnosis from symptoms
- Disease diagnosis from images
- Treatment selection (utility-based)
- Severity assessment
- Yemen-specific disease knowledge

### Coordinator Agent Tests

- Multi-agent orchestration
- Conflict detection and resolution
- Priority-based decision making
- Resource allocation
- Unified recommendation generation

### API Endpoint Tests

- Health check endpoint
- Analysis endpoint with validation
- Edge agent endpoints
- Feedback endpoint
- System status endpoint
- Rate limiting
- Error handling
- Request/response validation

### Integration Tests

- Disease detection and treatment workflow
- Irrigation management workflow
- Multi-agent coordination
- Emergency response workflow
- Feedback loop workflow
- End-to-end field analysis

## Mock Services

The test suite includes comprehensive mocks for external services:

### MockAIService

Generic AI service for predictions

### MockDiseaseDetectionModel

Mock disease detection model for testing disease workflows

### MockYieldPredictionModel

Mock yield prediction model

### MockWeatherAPI

Mock weather API service

### MockIrrigationController

Mock irrigation controller for testing actuator commands

### MockSensorDevice

Mock sensor device for testing sensor readings

## Fixtures

Common fixtures available in `conftest.py`:

### Agent Fixtures

- `sample_context` - Sample agent context
- `sample_percept` - Sample agent percept
- `sample_action` - Sample agent action
- `iot_agent` - IoT agent instance
- `disease_expert_agent` - Disease expert instance
- `coordinator_agent` - Coordinator instance

### API Fixtures

- `api_client` - Synchronous test client
- `async_api_client` - Async test client

### Mock Data Fixtures

- `mock_sensor_data` - Mock sensor readings
- `mock_weather_data` - Mock weather data
- `mock_image_data` - Mock image analysis
- `mock_disease_symptoms` - Mock disease symptoms

### Utility Fixtures

- `reset_agent_state` - Reset agent state between tests
- `rate_limit_headers` - Headers for rate limit testing

## Writing New Tests

### Unit Test Template

```python
@pytest.mark.unit
@pytest.mark.agent
@pytest.mark.asyncio
async def test_new_feature():
    """Test description"""
    # Arrange
    agent = TestAgent()

    # Act
    result = await agent.run(percept)

    # Assert
    assert result["success"] is True
```

### Integration Test Template

```python
@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.slow
async def test_new_workflow():
    """Test workflow description"""
    # Setup
    coordinator = MasterCoordinatorAgent()

    # Execute workflow
    result = await coordinator.run_full_analysis(context)

    # Verify
    assert result["success"] is True
```

## Best Practices

1. **Use descriptive test names** - Test names should clearly describe what is being tested
2. **Test one thing at a time** - Each test should focus on a single aspect
3. **Use fixtures** - Leverage shared fixtures for common setup
4. **Mock external services** - Always mock external API calls
5. **Test edge cases** - Include tests for error conditions and edge cases
6. **Use appropriate markers** - Mark tests with relevant pytest markers
7. **Keep tests fast** - Unit tests should run quickly; mark slow tests with `@pytest.mark.slow`
8. **Test async code properly** - Use `@pytest.mark.asyncio` for async tests

## Continuous Integration

Tests are automatically run on:

- Pull requests
- Merges to main branch
- Scheduled nightly runs

## Performance Benchmarks

### Target Response Times

- **Edge agents**: < 100ms
- **Specialist agents**: < 500ms
- **Coordinator**: < 2000ms
- **API endpoints**: < 5000ms

## Troubleshooting

### Common Issues

**Import errors**

```bash
# Ensure src is in PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"
```

**Async test failures**

```bash
# Install pytest-asyncio
pip install pytest-asyncio
```

**Coverage not showing**

```bash
# Install coverage dependencies
pip install pytest-cov
```

## Contributing

When adding new features:

1. Write tests first (TDD approach recommended)
2. Ensure all tests pass
3. Maintain or improve coverage
4. Update this README if adding new test categories

## Contact

For questions about testing, contact the development team.

---

**اختبارات شاملة لضمان جودة نظام الوكلاء الذكية**
