import os
import sys

# System and Model Configurations
MODEL_NAME = "gemini-3.5-flash"
MAX_ITERATIONS_DEFAULT = 20

def validate_environment():
    """Ensures required authorization tokens are present in the environment."""
    if not os.environ.get("GEMINI_API_KEY"):
        sys.exit(
            "CRITICAL: 'GEMINI_API_KEY' environment variable is missing.\n"
            "Export it to your environment before initializing the engine."
        )