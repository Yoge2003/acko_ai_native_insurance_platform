"""
Startup coordinator for ACKO AI Native Insurance Platform.
Validates dependencies and system connectivity before running the Streamlit app.
"""

import sys
import subprocess
from verify_environment import verify_all

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


def main() -> None:
    """Orchestrates validation and runs the Streamlit system."""
    if not verify_all():
        print("\n[FAIL] Diagnostics failed. Startup terminated.")
        sys.exit(1)
        
    print("\n[ OK ] Setup checks complete. Launching Streamlit Portal...")
    try:
        # Spawn Streamlit app
        subprocess.run(["streamlit", "run", "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n[INFO] Platform shutdown signal received.")
    except Exception as e:
        print(f"\n[FAIL] Error starting application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
