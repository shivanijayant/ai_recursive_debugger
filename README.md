# Gemini AI Recursive Debugger

An autonomous, closed-loop AI debugging agent that intercepts test failures, analyzes source code context using Google's Gemini API, and self-heals Python applications in real-time.

## Architecture Overview

This system operates as a deterministic state machine that continuously tests, isolates, and patches code until the architectural boundary stabilizes. 

1. **Test Runner:** Executes `pytest` as a subprocess and captures the raw telemetry and traceback data.
2. **Isolation Engine:** Parses the traceback using anti-cheat regex to explicitly isolate the broken application code (ignoring test suite files).
3. **Patcher:** Injects the isolated code, error logs, and system context into the Gemini 3.5 Flash model, forcing the LLM to output explicit `<reasoning>` tags before generating a structural patch.
4. **UI Dashboard:** Renders a color-coded, human-readable Git-style diff and incident report using `rich` before committing the patch to disk.

## Key Features

* **Zero-Touch Self-Healing:** Run the engine and watch it recursively fix logic bugs, syntax errors, and edge cases without human intervention.
* **Anti-Cheat Routing:** Explicitly prevents the LLM from "Specification Gaming" (e.g., deleting or modifying the test suite just to force a passing grade). The agent is forced to fix the underlying application logic.
* **Rich Incident Reports:** No black-box operations. The engine outputs a beautiful terminal dashboard explaining exactly *why* the code crashed and highlighting the exact lines modified.
* **In-Place Execution:** Patches are written directly over the broken source files, relying on Git for version control safety.

## Prerequisites

* Python 3.10+
* A Google Gemini API Key (`GEMINI_API_KEY`)
* **Git:** (CRITICAL) Only run this engine on repositories tracked by Git. The AI overwrites files in place.

## Installation

To avoid global macOS/Conda namespace collisions, this tool must be installed in a strictly isolated virtual environment.

```bash
# 1. Create the isolated virtual environment
python3 -m venv .venv

# 2. Activate the environment
source .venv/bin/activate

# 3. Install the unified GenAI SDK and CLI UI tools
pip install pytest google-genai rich

## 🚀 Usage

### 1. Set your API Key
Export your Google Gemini API key to your environment variables:
```bash
export GEMINI_API_KEY="your_actual_api_key_here"
```

### 2. Run the Engine
**Do not use the standard `python` alias.** To guarantee the engine bypasses any lingering global Conda environments and executes within the isolated bubble, use the absolute executable path.

Point the engine at your target test directory (e.g., `tests`):
```bash
.venv/bin/python main.py tests
```

You can also point the engine at any other external Python project on your machine, provided it uses `pytest` and its dependencies are installed in the local virtual environment:
```bash
.venv/bin/python main.py /path/to/your/project/module
```

## Safety Warnings

* **Destructive Writes:** This AI has direct file system write access. It will modify your source code. Always ensure your Git working tree is clean before running the state machine so you can easily run `git restore .` if the model hallucinates.
* **Cost & Quotas:** The recursive loop will continue calling the Gemini API until the test suite passes or it hits the maximum iteration limit. Monitor your API usage to avoid unexpected quota exhaustion.
