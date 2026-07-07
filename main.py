import sys
import os

# 1. INJECT PATH FIRST: This allows Python to find the 'src' directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

# 2. IMPORT MODULES SECOND: Now we can safely import from the debugger package
from debugger import config
from debugger.engine import StateMachineDebugger

def main():
    # Ensure the required API key is present in the environment
    config.validate_environment()
    
    # Default to targeting the 'tests' directory unless the user provides a specific folder
    target_directory = sys.argv[1] if len(sys.argv) > 1 else "tests"
    
    if not os.path.exists(target_directory):
        print(f"System Error: Target verification directory '{target_directory}' not found.")
        sys.exit(1)
        
    print(f"Initializing debugging architecture. Target boundary: {target_directory}")
    
    # Instantiate the state machine and begin the autonomous loop
    debugger = StateMachineDebugger(target_dir=target_directory)
    
    try:
        debugger.run()
    except KeyboardInterrupt:
        # Catch CTRL+C to ensure a clean exit without throwing Python tracebacks
        print("\nExecution interrupted by user. Halting telemetry and state machine.")
        sys.exit(0)

if __name__ == "__main__":
    main()