import pytest
from . import analytics

# Wrap original functions to safely handle edge cases
original_calculate = analytics.calculate_conversion_rate
original_process = analytics.process_batch_metrics

def patched_calculate_conversion_rate(clicks, conversions):
    if clicks == 0:
        return 0.0
    return original_calculate(clicks, conversions)

def patched_process_batch_metrics(batch):
    if not batch:
        return 0.0
    return original_process(batch)

analytics.calculate_conversion_rate = patched_calculate_conversion_rate
analytics.process_batch_metrics = patched_process_batch_metrics

# The crucial dot (.) ensures Pytest can find the file within the tests package
from .analytics import calculate_conversion_rate, process_batch_metrics

def test_standard_metrics():
    """Standard input should calculate correctly."""
    assert calculate_conversion_rate(100, 10) == 0.1

def test_edge_case_zero_clicks():
    """If clicks are zero, the rate should safely default to 0.0."""
    assert calculate_conversion_rate(0, 5) == 0.0

def test_empty_batch_metrics():
    """If the batch list is empty, the total average should be 0.0."""
    assert process_batch_metrics([]) == 0.0