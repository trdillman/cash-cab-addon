# Testing Procedure Template

This template provides the standard testing structure for all agent prompts.

## Pre-Agent Testing

Before starting work, run baseline tests if required:

### Performance Baseline (Phase 2 only)
```bash
# Measure import speed and memory usage
python tests/performance/baseline_import_speed.py
python tests/performance/baseline_memory_usage.py
```

### Quality Baseline (Phase 3 only)
```bash
# Measure current type hint coverage
mypy cashcab/ --strict | tee reports/mypy_baseline.txt

# Measure code duplication
pylint cashcab/ --disable=all --enable=duplicate-code | tee reports/duplication_baseline.txt
```

### Coverage Baseline (Phase 4 only)
```bash
# Measure current test coverage
python -m pytest tests/ -v --cov=cashcab --cov-report=term
```

## Post-Agent Testing

After completing work, run validation tests:

### Performance Tests (Phase 2)
```bash
# Validate import speed improvement (must show 40-60% reduction)
python tests/performance/validate_import_speed.py

# Validate memory usage reduction (must show 50% reduction)
python tests/performance/validate_memory_usage.py

# Run agent-specific unit tests
python -m pytest tests/unit/test_agent_002_xml_parsing.py -v
```

### Quality Tests (Phase 3)
```bash
# Validate type hint coverage (must show 80%+ coverage)
mypy cashcab/ --strict | tee reports/mypy_final.txt

# Validate code duplication reduction (must show <5%)
pylint cashcab/ --disable=all --enable=duplicate-code | tee reports/duplication_final.txt

# Run agent-specific tests
python -m pytest tests/unit/test_agent_006_god_object.py -v
python -m pytest tests/unit/test_agent_007_type_hints.py -v
python -m pytest tests/unit/test_agent_008_error_handling.py -v
python -m pytest tests/unit/test_agent_009_deduplication.py -v
```

### Coverage Tests (Phase 4)
```bash
# Security tests (target: 30% coverage)
python -m pytest tests/security/ -v --cov=cashcab.security --cov-report=html

# Route services tests (target: 60% coverage)
python -m pytest tests/unit/test_route_services.py -v --cov=cashcab.route.services --cov-report=html

# Overall coverage (target: 40% coverage)
python -m pytest tests/ -v --cov=cashcab --cov-report=html --cov-report=term
```

## Integration Testing

After each phase, run integration tests:

```bash
# Phase 2 integration
blender -b --python tests/integration/test_phase2_performance.py

# Phase 3 integration
blender -b --python tests/integration/test_phase3_quality.py

# Phase 4 integration
blender -b --python tests/integration/test_phase4_complete.py
```

## Success Criteria

Each agent is considered complete when:

1. **All files modified/created** according to the agent prompt
2. **All tests pass** (zero failures in tests_failed array)
3. **Metrics meet targets** (metrics object values)
4. **Checkpoint written** to `progress/phase-N-agent-XXX-checkpoint.json`
5. **Completion report written** to `reports/agent-XXX-completion-report.md`

## Test Creation Guidelines

When creating new tests, follow these patterns:

### Unit Test Structure
```python
def test_specific_feature():
    # Arrange
    input_data = [...]

    # Act
    result = function_under_test(input_data)

    # Assert
    assert result == expected_value
    assert result.metric >= target_value
```

### Performance Test Structure
```python
def test_import_speed_improvement():
    # Measure current performance
    current_time = measure_import_speed()

    # Assert target met
    baseline_time = get_baseline_import_speed()
    assert current_time <= baseline_time * 0.6  # 40% improvement
```

### Mocked API Test Structure
```python
def test_geocoding_error_handling():
    # Mock external API
    with mock('googlemaps.Client.geocode') as mock_geocode:
        mock_geocode.return_value = None
        mock_geocode.side_effect = Exception("API Error")

        # Test error handling
        with pytest.raises(GeocodingError):
            service.geocode("address")

        # Verify logging
        assert "Geocoding failed" in caplog.text
```
