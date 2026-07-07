import re
import time
import sys
import threading
import itertools
from typing import Dict, Tuple
from google import genai
from debugger import config

class CodePatcher:
    """Interfaces with the LLM to generate isolated architectural patches."""
    
    def __init__(self):
        self.client = genai.Client()

    def request_patch(self, broken_file: str, context: Dict[str, str], error_msg: str) -> Tuple[str, str, float]:
        """Formulates context payloads and requests patches, with a live progress UI."""
        start = time.perf_counter()
        
        # Build the context payload
        context_payload = "".join(
            f"\n--- System File: {path} ---\n```python\n{code}\n```\n" 
            for path, code in context.items()
        )

        prompt = f"""
        You are a deterministic code repair module in a continuous integration loop.

        ### System Telemetry & Traceback:
        Target Boundary: {broken_file}
        Exception: {error_msg}

        ### Architectural Context:
        {context_payload}

        ### Directives:
        1. Resolve the localized failure in {broken_file}.
        2. You MUST structure your response exactly like this:

        <reasoning>
        Write 1-2 clear sentences explaining exactly what the bug was and how you fixed it.
        </reasoning>
        
        ```python
        # Your fully revised code for {broken_file} here
        ```
        3. Exclude all other natural language processing output, conversational filler, and markdown.
        """

        # --- LIVE PROGRESS UI (Runs in a background thread) ---
        is_running = True
        
        def spinner_animation():
            spinner_chars = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
            while is_running:
                elapsed = time.perf_counter() - start
                # Use carriage return (\r) to rewrite the same line dynamically
                sys.stdout.write(f"\r  {next(spinner_chars)} Gemini is analyzing context & writing patch... [{elapsed:.1f}s]")
                sys.stdout.flush()
                time.sleep(0.1)

        # Start the UI thread
        ui_thread = threading.Thread(target=spinner_animation)
        ui_thread.start()
        # -----------------------------------------------------

        try:
            # The synchronous API call that hangs the main thread
            response = self.client.models.generate_content(
                model=config.MODEL_NAME,
                contents=prompt,
            )
        finally:
            # --- STOP THE PROGRESS UI ---
            is_running = False
            ui_thread.join()
            duration = time.perf_counter() - start
            
            # Clear the line and print success
            sys.stdout.write(f"\r✅ Gemini patch generated successfully! [{duration:.2f}s]               \n")
            sys.stdout.flush()

        # --- EXTRACT REASONING AND CODE ---
        reasoning_match = re.search(r'<reasoning>(.*?)</reasoning>', response.text, re.DOTALL)
        reasoning = reasoning_match.group(1).strip() if reasoning_match else "No diagnostic reasoning provided."

        code_match = re.search(r'```python\n(.*?)\n```', response.text, re.DOTALL)
        clean_code = code_match.group(1).strip() if code_match else response.text.strip()
        
        # Returns the code, the English explanation, and the timer
        return clean_code, reasoning, duration