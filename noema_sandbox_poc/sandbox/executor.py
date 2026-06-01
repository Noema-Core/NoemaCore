import subprocess
import hashlib
import time
import os
import sys
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Dodaj root projektu do PATH, żeby import z integration/ działał zawsze
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

load_dotenv(os.path.join(project_root, '.env'))

try:
    from integration.web3_submitter import submit_attestation
    WEB3_INTEGRATION = True
except ImportError:
    WEB3_INTEGRATION = False

@dataclass
class ExecutionResult:
    success: bool
    output: str
    error: str
    attestation_hash: str
    duration_sec: float
    tx_hash: Optional[str] = None

class SandboxExecutor:
    def __init__(self, image: str = "python:3.11-slim", timeout_sec: int = 60, submit_to_chain: bool = False):
        self.image = image
        self.timeout = timeout_sec
        self.submit_to_chain = submit_to_chain

    def run_task(self, task_code: str, execution_id: str = "0x0", cpu_limit: float = 0.5, mem_limit: str = "256m") -> ExecutionResult:
        start = time.time()
        cmd = [
            "docker", "run", "--rm",
            "--cpus", str(cpu_limit),
            "--memory", mem_limit,
            "--memory-swap", mem_limit,
            "--network", "none",
            self.image,
            "python", "-c", task_code
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=self.timeout + 5)
            duration = time.time() - start
            success = result.returncode == 0
            output = result.stdout.strip()
            error = result.stderr.strip() if not success else ""
        except subprocess.TimeoutExpired:
            duration = time.time() - start
            success = False
            output = ""
            error = "Execution timeout exceeded"
        except Exception as e:
            duration = time.time() - start
            success = False
            output = ""
            error = str(e)

        attestation_hash = self._generate_attestation(task_code, output, error, duration)
        tx_hash = None

        # Auto-submit on-chain jeśli sukces + flaga włączona
        if success and self.submit_to_chain and WEB3_INTEGRATION:
            print(f"[+] Submitting attestation to chain: {attestation_hash}")
            try:
                is_submitted = submit_attestation(execution_id, attestation_hash)
                tx_hash = "success" if is_submitted else "failed"
            except Exception as e:
                print(f"[-] Web3 submission error: {e}")
                tx_hash = "error"

        return ExecutionResult(success, output, error, attestation_hash, duration, tx_hash)

    def _generate_attestation(self, task: str, out: str, err: str, duration: float) -> str:
        payload = f"{task}|{out}|{err}|{duration}".encode()
        return hashlib.sha256(payload).hexdigest()
