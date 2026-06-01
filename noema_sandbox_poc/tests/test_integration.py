import pytest
import subprocess
import sys
from sandbox.executor import SandboxExecutor

def test_real_docker_execution():
    """Testuje rzeczywiste wykonanie kodu w kontenerze Docker."""
    # Sprawdź, czy Docker jest dostępny i działa
    try:
        result = subprocess.run(
            ["docker", "info"], 
            check=True, 
            capture_output=True, 
            timeout=10
        )
    except subprocess.CalledProcessError as e:
        pytest.skip(f"Docker daemon error: {e.stderr.decode()[:100]}")
    except FileNotFoundError:
        pytest.skip("Docker is not installed. Skipping integration test.")
    except subprocess.TimeoutExpired:
        pytest.skip("Docker daemon is not responding. Skipping integration test.")

    # Dłuższy timeout na pierwsze uruchomienie (pull image + run)
    executor = SandboxExecutor(image="python:3.11-slim", timeout_sec=120)
    
    # Test 1: Proste wykonanie
    res = executor.run_task("print('Hello from isolated sandbox!')")
    assert res.success is True, f"Expected success, got error: {res.error}"
    assert "Hello from isolated sandbox!" in res.output

    # Test 2: Izolacja sieciowa (--network none)
    res_net = executor.run_task("import urllib.request; urllib.request.urlopen('http://example.com')")
    # Oczekujemy błędu sieciowego, co potwierdza izolację
    assert res_net.success is False, "Network should be blocked in sandbox"
    assert any(kw in res_net.error.lower() for kw in ["network is unreachable", "gaierror", "timeout", "connection refused"]), \
        f"Expected network error, got: {res_net.error}"
