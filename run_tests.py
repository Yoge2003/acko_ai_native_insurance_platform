"""
Automated test runner for ACKO AI Native Insurance Platform.
Cross-platform encoding safe.
"""

import sys
import subprocess

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


def main() -> None:
    """Executes the pytest test suite."""
    print("[TEST] Executing all unit and integration tests across the platform...")
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", "-p", "no:warnings", "--tb=short"], 
            check=False
        )
        sys.exit(result.returncode)
    except Exception as e:
        print(f"[FAIL] Error running pytest suite: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
