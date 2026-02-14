"""Run the app with auto-restart when Python files change. Use this for local dev."""

import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WATCH_FILES = [
    ROOT / "web.py",
    ROOT / "config.py",
    ROOT / "sheet_loader.py",
    ROOT / "serve.py",
    ROOT / "api" / "index.py",
]


def get_mtimes():
    out = {}
    for p in WATCH_FILES:
        try:
            out[p] = p.stat().st_mtime
        except OSError:
            out[p] = 0
    return out


def main():
    env = os.environ.copy()
    env.setdefault("PORT", "8000")
    prev_mtimes = get_mtimes()
    process = None

    print("Dev server with auto-reload. Editing .py files will restart the server.")
    print("Open http://localhost:8000  (Ctrl+C to stop)\n")

    while True:
        if process is None or process.poll() is not None:
            process = subprocess.Popen(
                [sys.executable, str(ROOT / "serve.py")],
                cwd=str(ROOT),
                env=env,
            )

        time.sleep(1)
        cur_mtimes = get_mtimes()
        if cur_mtimes != prev_mtimes:
            prev_mtimes = cur_mtimes
            process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
            process = None
            print("\n[Restarting server after file change...]\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.")
