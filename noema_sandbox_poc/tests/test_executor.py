import pytest
import unittest.mock as mock
from sandbox.executor import SandboxExecutor, ExecutionResult

class TestSandboxExecutor:
    def setup_method(self):
        self.executor = SandboxExecutor(image="python:3.11-slim", timeout_sec=60)

    @mock.patch('sandbox.executor.subprocess.run')
    def test_successful_execution(self, mock_run):
        # Symulacja udanego wykonania kodu w Dockerze
        mock_result = mock.Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Hello World\n"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        result = self.executor.run_task("print('Hello World')")

        assert result.success is True
        assert result.output == "Hello World"
        assert result.error == ""
        assert len(result.attestation_hash) == 64  # SHA256 hex length

    @mock.patch('sandbox.executor.subprocess.run')
    def test_failed_execution(self, mock_run):
        # Symulacja błędu w kodzie (np. SyntaxError)
        mock_result = mock.Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "SyntaxError: invalid syntax"
        mock_run.return_value = mock_result

        result = self.executor.run_task("print('broken")

        assert result.success is False
        assert "SyntaxError" in result.error

    def test_attestation_is_deterministic(self):
        # Hash attestation musi być identyczny dla tych samych danych
        res1 = self.executor._generate_attestation("code", "out", "err", 1.0)
        res2 = self.executor._generate_attestation("code", "out", "err", 1.0)
        assert res1 == res2
