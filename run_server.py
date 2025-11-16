# run_server.py  (place at repo root and run from repo root)
import os, sys, time, traceback, signal, atexit
import faulthandler

LOG_PATH = os.path.abspath("server.log")

# Ensure logs even on fatal crashes
faulthandler.enable(all_threads=True, file=open(LOG_PATH, "a"))

# Dump unhandled exceptions
def excepthook(exctype, value, tb):
    with open(LOG_PATH, "a") as f:
        f.write("\n=== sys.excepthook =====================================\n")
        traceback.print_exception(exctype, value, tb, file=f)
        f.write("========================================================\n")
    # also print to stderr
    traceback.print_exception(exctype, value, tb, file=sys.stderr)

sys.excepthook = excepthook

# Signal handlers
def _signal_dump(sig, frame):
    msg = f"Received signal {sig} -> dumping stacks"
    with open(LOG_PATH, "a") as f:
        f.write(f"\n=== {msg} ===\n")
        faulthandler.dump_traceback(file=f, all_threads=True)
    # re-raise default behavior
    signal.signal(sig, signal.SIG_DFL)
    os.kill(os.getpid(), sig)

for s in (signal.SIGTERM, signal.SIGINT, signal.SIGQUIT):
    try:
        signal.signal(s, _signal_dump)
    except Exception:
        pass

@atexit.register
def _on_exit():
    with open(LOG_PATH, "a") as f:
        f.write(f"\n[atexit] process exiting at {time.ctime()}\n")

def main():
    # Ensure repo root on sys.path
    repo_root = os.path.dirname(os.path.abspath(__file__))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    # Be explicit about env noise
    os.environ.setdefault("PYTHONFAULTHANDLER", "1")
    os.environ.setdefault("PYTHONWARNINGS", "default")

    # Import app carefully and loudly
    try:
        from backend.src.main import app  # absolute import
    except Exception as e:
        with open(LOG_PATH, "a") as f:
            f.write("\n=== Failed to import FastAPI app =========================\n")
            traceback.print_exc(file=f)
        raise

    # Start uvicorn with explicit config
    try:
        import uvicorn
        config = uvicorn.Config(
            app,
            host="0.0.0.0",
            port=8000,
            reload=False,         # set True if you want, but start with False to simplify
            log_level="debug",
            use_colors=False,
            access_log=True,
        )
        server = uvicorn.Server(config)
        with open(LOG_PATH, "a") as f:
            f.write(f"\n[launcher] Starting uvicorn server at {time.ctime()}\n")
        rc = server.run()
        with open(LOG_PATH, "a") as f:
            f.write(f"\n[launcher] Uvicorn server exited: {rc} at {time.ctime()}\n")
    except BaseException:
        with open(LOG_PATH, "a") as f:
            f.write("\n=== Uvicorn crashed =====================================\n")
            traceback.print_exc(file=f)
        raise

if __name__ == "__main__":
    try:
        main()
    except BaseException:
        # Ensure we log *something* even if logging broke
        with open(LOG_PATH, "a") as f:
            f.write("\n=== Top-level crash ===============================\n")
            traceback.print_exc(file=f)
        raise