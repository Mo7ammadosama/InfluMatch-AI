#!/usr/bin/env python3
"""ARIA WaslAI.jo — One-Command Launcher"""
import subprocess, sys, os, time, signal
from pathlib import Path

ROOT = Path(__file__).parent.parent / "waslai"
os.chdir(ROOT)

CYAN = "\033[96m"; GREEN = "\033[92m"; RED = "\033[91m"
YELLOW = "\033[93m"; RESET = "\033[0m"; BOLD = "\033[1m"

def banner():
    print(f"""{CYAN}{BOLD}
+--------------------------------------------------------------+
|   ARIA - WaslAI.jo Platform Launcher v1.0.0             |
|   Jordan Influencer Marketing Platform                       |
|   Powered by Claude AI + FastAPI + Streamlit                 |
+--------------------------------------------------------------+
{RESET}""")

def check_env():
    env_file = ROOT / ".env"
    if not env_file.exists():
        print(f"{RED}[ERROR] .env not found at {env_file}{RESET}")
        sys.exit(1)
    content = env_file.read_text()
    if "your_anthropic" in content or "ANTHROPIC_API_KEY=" not in content:
        print(f"{YELLOW}[WARN] ANTHROPIC_API_KEY not set — AI features disabled{RESET}")
    else:
        print(f"{GREEN}[OK] Environment validated{RESET}")

def init_database():
    print(f"{CYAN}[DB] Initializing database...{RESET}")
    result = subprocess.run(
        [sys.executable, str(Path(__file__).parent / "init_db.py")],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print(f"{GREEN}[OK] Database ready{RESET}")
    else:
        print(f"{YELLOW}[WARN] DB init: {result.stderr[:100]}{RESET}")

def start_services():
    processes = []

    print(f"\n{CYAN}[API] Starting FastAPI Backend (port 8000)...{RESET}")
    backend = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app",
         "--host", "0.0.0.0", "--port", "8000", "--reload", "--log-level", "warning"],
        cwd=ROOT
    )
    processes.append(("Backend", backend))
    time.sleep(3)

    print(f"{CYAN}[UI] Starting Streamlit Frontend (port 8501)...{RESET}")
    frontend = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "frontend/app.py",
         "--server.port", "8501", "--server.address", "0.0.0.0",
         "--server.headless", "true",
         "--theme.base", "dark",
         "--theme.primaryColor", "#533483",
         "--theme.backgroundColor", "#0a0a1a",
         "--theme.secondaryBackgroundColor", "#1a1a2e"],
        cwd=ROOT
    )
    processes.append(("Frontend", frontend))
    time.sleep(2)

    print(f"""{GREEN}{BOLD}
+--------------------------------------------------------------+
|  ARIA WaslAI.jo Platform ONLINE                         |
|                                                              |
|  FastAPI Backend:   http://localhost:8000                    |
|  API Documentation: http://localhost:8000/docs               |
|  Streamlit UI:      http://localhost:8501                    |
|  Health Check:      http://localhost:8000/health             |
|                                                              |
|  Press Ctrl+C to shutdown all services                      |
+--------------------------------------------------------------+
{RESET}""")

    def shutdown(sig, frame):
        print(f"\n{YELLOW}[ARIA] Shutting down...{RESET}")
        for name, proc in processes:
            proc.terminate()
            print(f"{RED}[STOP] {name}{RESET}")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)
    for _, proc in processes:
        proc.wait()

if __name__ == "__main__":
    banner()
    check_env()
    init_database()
    start_services()
