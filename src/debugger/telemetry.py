import logging
import time

# System telemetry configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [System Telemetry] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("DebuggerArchitecture")

class PerformanceTracker:
    """Tracks system execution metrics and architectural efficiency."""
    
    def __init__(self):
        self.start_time = time.perf_counter()
        self.metrics = []

    def log_cycle(self, iteration: int, test_duration: float, llm_duration: float):
        """Records granular timing data for a completed state cycle."""
        record = {
            "iteration": iteration,
            "test_duration": test_duration,
            "llm_duration": llm_duration,
            "total_cycle_time": test_duration + llm_duration
        }
        self.metrics.append(record)
        logger.info(
            f"Cycle {iteration} Telemetry | IO & Tests: {test_duration:.2f}s | "
            f"LLM Inference: {llm_duration:.2f}s | Net: {record['total_cycle_time']:.2f}s"
        )

    def log_summary(self):
        """Outputs the final architectural run metrics."""
        total_time = time.perf_counter() - self.start_time
        logger.info("=== Architectural Run Terminated ===")
        logger.info(f"Total System Uptime: {total_time:.2f}s")
        logger.info(f"State Machine Iterations: {len(self.metrics)}")