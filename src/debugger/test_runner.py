import subprocess
import sys
import time
import os
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
                candidate_file = match.group(1)
                
                # --- UPDATED ANTI-CHEAT ---
                # Use os.path.basename to strip the folder path before checking
                filename = os.path.basename(candidate_file)
                if not filename.startswith("test_") and not filename.endswith("_test.py"):
                    failing_file = candidate_file
                    error_messages.append(match.group(3))
                    break

        # Fallback if the regex missed it
        if not failing_file:
            for line in lines:
                if self.target_dir in line and ".py" in line:
                    match = re.search(r'([\w\-/\\\.]+\.py)', line)
                    if match:
                        candidate_file = match.group(1)
                        if not "test_" in candidate_file:
                            failing_file = candidate_file
                            break

        error_summary = "\n".join(error_messages) if error_messages else "Unhandled execution state."
        return failing_file, error_summary