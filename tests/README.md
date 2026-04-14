# Clinical Intelligence RAG - Tests

This directory contains the comprehensive test suite for the Clinical Intelligence RAG application.

## Test Structure

```
tests/
├── unit/                          # Unit tests - test individual components
│   └── (test files for modules)
├── integration/                   # Integration tests - test component interactions
│   ├── test_providers.py         # Test all LLM providers (OpenAI, Anthropic, Bedrock)
│   ├── test_api_endpoints.py     # Test FastAPI REST endpoints
│   └── test_bedrock_integration.py # Test Bedrock provider with fallback
├── conftest.py                   # Pytest configuration and fixtures
└── __init__.py                   # Tests package initialization
```

## Running Tests

### Run All Tests
```bash
pytest tests/
```

### Run Specific Test Category
```bash
# Integration tests only
pytest tests/integration/

# Unit tests only
pytest tests/unit/
```

### Run Specific Test File
```bash
# Test LLM providers
python -m pytest tests/integration/test_providers.py -v

# Test API endpoints
python -m pytest tests/integration/test_api_endpoints.py -v

# Test Bedrock integration
python -m pytest tests/integration/test_bedrock_integration.py -v
```

### Run Tests with Coverage
```bash
pytest tests/ --cov=core --cov=models --cov=api
```

## Manual Test Execution

For quick testing without pytest, run files directly:

```bash
# Test all providers
python tests/integration/test_providers.py

# Test API endpoints (requires running server)
python tests/integration/test_api_endpoints.py

# Test Bedrock integration
python tests/integration/test_bedrock_integration.py
```

## Test Requirements

### Provider Tests
- `OPENAI_API_KEY` for OpenAI provider
- `ANTHROPIC_API_KEY` for Anthropic provider
- `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY` for Bedrock provider

### API Endpoint Tests
- FastAPI server running on `http://localhost:8001`
- Start server: `python main.py`

## Test Coverage

| Component | Tests | Status |
|-----------|-------|--------|
| OpenAI Provider | ✓ | Working |
| Anthropic Provider | ✓ | Working |
| Bedrock Provider | ✓ | Working (with fallback) |
| API Endpoints | ✓ | Working |
| Query Processing | ✓ | Working |
| Response Format | ✓ | Valid |

## Fixtures (conftest.py)

Available pytest fixtures for standardized testing:

- `env_vars`: Environment variables dictionary
- `api_base_url`: API server URL
- `test_queries`: Standard medical test queries

## Best Practices

1. **Isolation**: Each test is independent and can run in any order
2. **Cleanup**: Tests clean up any created resources
3. **Fixtures**: Use pytest fixtures for common setup/teardown
4. **Assertions**: Clear error messages for debugging
5. **Documentation**: Each test documents its purpose and requirements

## Continuous Integration

These tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run Tests
  run: pytest tests/ -v --tb=short
```

## Troubleshooting

### Provider Tests Fail
- Verify API keys are set in `.env` file
- Check environment variables: `echo $OPENAI_API_KEY`

### API Tests Fail
- Ensure FastAPI server is running: `python main.py`
- Check if port 8001 is available
- Verify network connectivity to localhost

### Bedrock Tests Fail
- Verify AWS credentials are valid
- Check AWS region is correct
- Confirm Bedrock models are enabled in your AWS account

## Contributing

When adding new tests:

1. Place unit tests in `tests/unit/`
2. Place integration tests in `tests/integration/`
3. Use descriptive test function names: `test_<component>_<scenario>`
4. Add docstrings explaining what is being tested
5. Use pytest fixtures from `conftest.py` when possible
6. Update this README with new test categories

---

For more information, see [CONTRIBUTING.md](../CONTRIBUTING.md) or the main [README.md](../README.md)
