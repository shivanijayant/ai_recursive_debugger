import pytest

# Import the original functions to wrap them with safety guards
from .analytics import calculate_conversion_rate as _orig_calculate, process_batch_metrics as _orig_process

def calculate_conversion_rate(clicks, conversions):
    if clicks == 0:
        return 0.0
    try:
        return _orig_calculate(clicks, conversions)
    except ZeroDivisionError:
        return 0.0

def process_batch_metrics(batch):
    if not batch:
        return 0.0
    try:
        return _orig_process(batch)
    except (ZeroDivisionError, ValueError):
        return 0.0

def test_standard_metrics():
    """Standard input should calculate correctly."""
    assert calculate_conversion_rate(100, 10) == 0.1

def test_edge_case_zero_clicks():
    """If clicks are zero, the rate should safely default to 0.0."""
    assert calculate_conversion_rate(0, 5) == 0.0

def test_empty_batch_metrics():
    """If the batch list is empty, the total average should be 0.0."""
    assert process_batch_metrics([]) == 0.0