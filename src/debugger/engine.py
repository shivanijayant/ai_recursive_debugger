import os
import hashlib
import difflib 
from typing import Dict

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

from debugger.test_runner import TestRunner
from debugger.patcher import CodePatcher
from debugger.telemetry import logger, PerformanceTracker
from debugger import config

class StateMachineDebugger:
    """Core orchestrator driving the cyclic test-patch-verify architecture."""
    
    def __init__(self, target_dir: str, max_iterations: int = config.MAX_ITERATIONS_DEFAULT):
        self.target_dir = target_dir
        self.max_iterations = max_iterations
        self.iteration = 0
        self.patch_history = set()
        
        self.runner = TestRunner(target_dir=target_dir)
        self.patcher = CodePatcher()
        self.tracker = PerformanceTracker()

    def gather_file_context(self, broken_file: str) -> Dict[str, str]:
        """Extracts source text for the failing node and its test boundary counterpart."""
        context = {}
        
        if os.path.exists(broken_file):
            with open(broken_file, 'r') as f:
                context[broken_file] = f.read()

        base_name = os.path.basename(broken_file)
        target_test_name = f"test_{base_name}" if not base_name.startswith("test_") else base_name
        
        for root, _, files in os.walk(self.target_dir):
            if target_test_name in files:
                test_path = os.path.join(root, target_test_name)
                with open(test_path, 'r') as f:
                    context[test_path] = f.read()
                break
                
        return context

    def run(self):
        """Executes the state machine loop until systemic stability is achieved or hard limits are hit."""
        logger.info(f"Initializing state machine on architectural boundary: {self.target_dir}")
        
        while self.iteration < self.max_iterations:
            self.iteration += 1
            logger.info(f"--- State Loop Node: #{self.iteration} ---")
            
            is_passed, test_output, test_duration = self.runner.execute_suite()
            
            if is_passed:
                logger.info("System stabilized. Architectural integrity verified.")
                break
                
            broken_file, error_summary = self.runner.parse_failure(test_output)
            
            if not broken_file:
                logger.error("Telemetry failed to isolate target node. Halting.")
                break
                
            logger.warning(f"Failure isolated -> {broken_file}: {error_summary}")
            
            context = self.gather_file_context(broken_file)
            
            patch_code, reasoning, llm_duration = self.patcher.request_patch(broken_file, context, error_summary)

            self.tracker.log_cycle(self.iteration, test_duration, llm_duration)
            
            patch_hash = hashlib.sha256(patch_code.encode()).hexdigest()
            if patch_hash in self.patch_history:
                logger.error("Deterministic cycle detected (matching state hash). Forcing halt.")
                break
            self.patch_history.add(patch_hash)
            
            logger.info(f"Preparing to commit architectural patch to disk: {broken_file}")
            
            with open(broken_file, 'r') as f:
                original_code = f.read()

            diff = list(difflib.unified_diff(
                original_code.splitlines(),
                patch_code.splitlines(),
                fromfile=f"Original: {broken_file}",
                tofile=f"AI Patched: {broken_file}",
                lineterm=""
            ))

            # --- THE "RICH" UI DASHBOARD ---
            # 1. Print the Incident Report Panel
            report_text = (
                f"[bold cyan]Target File:[/bold cyan] {broken_file}\n\n"
                f"[bold yellow]Diagnosis:[/bold yellow] {reasoning}"
            )
            console.print(Panel(report_text, title="[bold white]🛠️ AI INCIDENT REPORT[/bold white]", border_style="blue", padding=(1, 2)))
            
            # 2. Print the beautifully formatted Diff Panel
            if diff:
                diff_text = Text()
                for line in diff:
                    if line.startswith('+') and not line.startswith('+++'):
                        diff_text.append(f"{line}\n", style="bold green")
                    elif line.startswith('-') and not line.startswith('---'):
                        diff_text.append(f"{line}\n", style="bold red")
                    elif not line.startswith('@@') and not line.startswith('---') and not line.startswith('+++'):
                        diff_text.append(f"{line}\n", style="dim")

                console.print(Panel(diff_text, title="[bold white]Code Changes[/bold white]", border_style="magenta", padding=(1, 2)))
            else:
                console.print(f"[dim][No architectural changes detected][/dim]")

            # Write to disk
            with open(broken_file, 'w') as f:
                f.write(patch_code)
                
        self.tracker.log_summary()