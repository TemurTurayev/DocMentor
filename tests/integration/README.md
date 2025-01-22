# Integration Tests for DocMentor

This directory contains integration tests that verify the interaction between different components of DocMentor.

## Test Structure

1. `test_pdf_to_vector.py`
   - Tests the integration between PDF processor and vector storage
   - Verifies mode-specific storage behavior
   - Tests error handling across components

2. `test_streamlit_interface.py`
   - Tests UI integration with backend components
   - Verifies file upload functionality
   - Tests chat interface integration
   - Validates error handling in the UI

## Running Tests

To run the integration tests:

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all integration tests
python -m pytest tests/integration/

# Run with coverage report
python -m pytest --cov=core tests/integration/
```

## Test Data

The tests use sample data in the `test_data` directory. This data is automatically generated during test execution.

## Adding New Tests

When adding new integration tests:
1. Create a new test file for each major integration point
2. Follow the existing pattern of setUp/tearDown
3. Include both happy path and error handling tests
4. Keep resource usage in mind (clean up test data)

## Test Configuration

Tests use a separate configuration file (`test_config.json`) to avoid interfering with production settings.

## Common Issues and Solutions

1. If tests fail with permission errors:
   - Check file permissions in test_data directory
   - Ensure write access to test_config.json

2. For Streamlit-related test failures:
   - Verify Streamlit test dependencies are installed
   - Check if UI components are properly initialized

3. For vector storage tests:
   - Ensure enough disk space for test indices
   - Clear test indices between test runs