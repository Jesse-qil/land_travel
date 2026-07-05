"""
Land Travel Smart Recommender — One-click Launcher

Starts: AI Agent (8001) + Backend (8000)

Usage:
    python start.py                  # Start both services
    python start.py --backend        # Backend only
    python start.py --agent          # Agent only
    python start.py --no-open        # Don't auto-open browser
"""

import os
import sys
import subprocess
import time
import webbrowser
import signal
import threading
import argparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, "travel-app", "backend")
AGENT_DIR = os.path.join(BASE_DIR, "travel-agent")
FRONTEND_DIR = os.path.join(BASE_DIR, "travel-app", "frontend")

processes = []
stop_event = threading.Event()


def color(s, code=36):
    return f"\033[{code}m{s}\033[0m"


def log(service, msg, ok=True):
    icon = "✅" if ok else "❌"
    tag = color(f"[{service:>6}]", 33)
    print(f"{tag} {icon} {msg}")


def check_python():
    v = sys.version_info
    if v.major < 3 or (v.major == 3 and v.minor < 9):
        log("System", f"Python 3.9+ required, got {v.major}.{v.minor}", False)
        return False
    log("System", f"Python {v.major}.{v.minor}.{v.micro}")
    return True


def check_deps():
    ok = True

    # Backend deps
    req = os.path.join(BACKEND_DIR, "requirements.txt")
    if not _check_pip(req, "Backend"):
        ok = False

    # Agent deps
    req = os.path.join(AGENT_DIR, "requirements.txt")
    if not _check_pip(req, "Agent"):
        ok = False

    # Frontend deps
    node_modules = os.path.join(FRONTEND_DIR, "node_modules")
    if not os.path.isdir(node_modules):
        log("Frontend", "node_modules not found, running npm install...", False)
        r = subprocess.run(["npm", "install"], cwd=FRONTEND_DIR, shell=True)
        if r.returncode == 0:
            log("Frontend", "npm install done")
        else:
            log("Frontend", "npm install failed", False)
            ok = False
    else:
        log("Frontend", "node_modules ready")

    return ok


def _check_pip(req_file, name):
    if not os.path.exists(req_file):
        log(name, f"Requirements file not found: {req_file}", False)
        return False

    try:
        import pkg_resources
        with open(req_file) as f:
            required = {
                line.strip().split("==")[0].split(">=")[0].split("<")[0]
                for line in f if line.strip() and not line.startswith("#")
            }
        installed = {pkg.key for pkg in pkg_resources.working_set}
        missing = {pkg for pkg in required if pkg and pkg.lower() not in installed}
        if missing:
            log(name, f"Missing: {', '.join(missing)}, installing...", False)
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", req_file, "-q"],
                cwd=BASE_DIR,
            )
            log(name, "Dependencies installed")
        else:
            log(name, "Dependencies ready")
    except Exception:
        log(name, "Dependency check skipped", False)

    return True


def start_service(name, cwd, command, port=None):
    log(name, f"Starting (port {port})..." if port else "Starting...")

    try:
        proc = subprocess.Popen(
            command,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            universal_newlines=True,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
        )
        processes.append(proc)
        return proc
    except Exception as e:
        log(name, f"Failed to start: {e}", False)
        return None


def wait_for_health(url, name, timeout=15):
    import urllib.request

    log(name, f"Waiting for ready (timeout {timeout}s)...", True)
    start = time.time()

    while time.time() - start < timeout:
        try:
            resp = urllib.request.urlopen(url, timeout=2)
            if resp.status == 200:
                log(name, f"Ready ✅ ({url})")
                return True
        except Exception:
            pass
        time.sleep(1)

    log(name, f"Timeout, please check {url} manually", False)
    return False


def open_browser(url):
    def _open():
        stop_event.wait(3)
        if not stop_event.is_set():
            webbrowser.open(url)
            log("System", f"Browser opened: {url}")

    t = threading.Thread(target=_open, daemon=True)
    t.start()


def print_banner():
    banner = f"""
{color('═══════════════════════════════════════════', 35)}
{color('   Land Travel Smart Recommender  v3.2', 36)}
{color('   One-click Launcher', 33)}
{color('═══════════════════════════════════════════', 35)}
"""
    print(banner)


def print_urls():
    print(f"\n{color('── Service URLs ──', 35)}")
    print(f"  {color('Backend:', 33)}     http://localhost:8000")
    print(f"  {color('API Docs:', 33)}    http://localhost:8000/docs")
    print(f"  {color('AI Agent:', 33)}    http://localhost:8001/health")
    print()


def cleanup(_signum=None, _frame=None):
    print(f"\n{color('Shutting down services...', 31)}")
    stop_event.set()
    for proc in processes:
        if proc and proc.poll() is None:
            if sys.platform == "win32":
                proc.send_signal(signal.CTRL_BREAK_EVENT)
            proc.terminate()
    for proc in processes:
        proc.wait(timeout=5)
    print(color("All services stopped", 32))
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description="Land Travel Smart Recommender Launcher")
    parser.add_argument("--backend", action="store_true", help="Start backend only")
    parser.add_argument("--agent", action="store_true", help="Start agent only")
    parser.add_argument("--no-open", action="store_true", help="Don't open browser automatically")
    args = parser.parse_args()

    print_banner()

    start_backend = args.backend or not args.agent
    start_agent = args.agent or not args.backend

    if not check_python():
        sys.exit(1)

    check_deps()

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    if start_agent:
        start_service(
            "AI Agent", AGENT_DIR,
            [sys.executable, "-m", "uvicorn", "server:app", "--port", "8001", "--reload"],
            port=8001,
        )
        time.sleep(2)

    if start_backend:
        start_service(
            "Backend", BACKEND_DIR,
            [sys.executable, "-m", "uvicorn", "main:app", "--port", "8000", "--reload"],
            port=8000,
        )

    print_urls()

    ready_threads = []
    if start_agent:
        t = threading.Thread(
            target=wait_for_health,
            args=("http://localhost:8001/health", "AI Agent"),
            daemon=True,
        )
        t.start()
        ready_threads.append(t)

    if start_backend:
        t = threading.Thread(
            target=wait_for_health,
            args=("http://localhost:8000/health", "Backend"),
            daemon=True,
        )
        t.start()
        ready_threads.append(t)

    if not args.no_open and start_backend:
        open_browser("http://localhost:8000")

    print(color("Press Ctrl+C to stop all services", 33))

    try:
        for proc in processes:
            if proc:
                proc.wait()
    except KeyboardInterrupt:
        cleanup()


if __name__ == "__main__":
    main()
