import subprocess
import sys
import time
import re
from typing import Tuple, Optional
from debugger.telemetry import logger

class TestRunner:
    """Handles isolated subprocess execution and traceback state extraction."""
    
    def __init__(self, target_dir: str):
        self.target_dir = target_dir

    def execute_suite(self) -> Tuple[bool, str, float]:
        """Runs the test boundary and captures execution duration."""
        start = time.perf_counter()
        
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-vv", "--tb=short", self.target_dir],
            capture_output=True,
            text=True
        )
        
        duration = time.perf_counter() - start
        is_success = (result.returncode == 0)
        return is_success, result.stdout + "\n" + result.stderr, duration

    def parse_failure(self, test_output: str) -> Tuple[Optional[str], str]:
        """Extracts target file boundaries and exceptions from telemetry logs."""
        lines = test_output.splitlines()
        failing_file = None
        error_messages = []
        is_capture_zone = False

        for line in lines:
            if any(marker in line for marker in ["FAILURES", "FAILED", "ERRORS"]):
                is_capture_zone = True
            
            match = re.search(r'([\w\-/\\\.]+\.py):(\d+): (.+)', line)
            if match and is_capture_zone:
                failing_file = match.group(1)
                error_messages.append(match.group(3))
                break

        if not failing_file:
            for line in lines:
                if self.target_dir in line and ".py" in line:
                    match = re.search(r'([\w\-/\\\.]+\.py)', line)
                    if match:
                        failing_file = match.group(1)
                        break

        error_summary = "\n".join(error_messages) if error_messages else "Unhandled execution state."
        return failing_file, error_summary