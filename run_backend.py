#!/usr/bin/env python3
"""Run the FastAPI backend from repo root. Uses backend/ as cwd so 'app' is found and .env is loaded."""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND = os.path.join(ROOT, "backend")

def main():
    subprocess.run(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--host", "127.0.0.1", "--port", "8000"],
        cwd=BACKEND,
        env=os.environ.copy(),
    )

if __name__ == "__main__":
    main()
