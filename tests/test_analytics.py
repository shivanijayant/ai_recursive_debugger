import pytest

# The crucial dot (.) ensures Pytest can find the file within the tests package
from .analytics import calculate_conversion_rate, process_batch_metrics

def test_standard_metrics():
    """Standard input should calculate correctly."""
    assert calculate_conversion_rate(100, 10) == 0.1

def test_edge_case_zero_clicks():
    """If clicks are zero, the rate should safely default to 0.0."""
    # This will fail on the first loop iteration
    assert calculate_conversion_rate(0, 5) == 0.0

def test_empty_batch_metrics():
    """If the batch list is empty, the total average should be 0.0."""
    # This will also fail until the AI patches process_batch_metrics
    assert process_batch_metrics([]) == 0.0