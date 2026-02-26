import subprocess
import sys
from datetime import date
import requests


def run_pipeline():
    today = date.today().isoformat()
    print(f"Generating board artifact for {today}...")
    subprocess.run([sys.executable, "-m", "app.cli.main", "board"], check=True)


def check_api_health():
    print("Checking FastAPI health endpoint...")
    try:
        resp = requests.get("http://localhost:8000/health", timeout=5)
        if resp.status_code == 200 and resp.json().get("status") == "OK":
            print("API health check passed.")
            return True
        else:
            print(f"API health check failed: {resp.status_code} {resp.text}")
            return False
    except Exception as e:
        print(f"API health check error: {e}")
        return False


def launch_dashboard():
    print("Launching Streamlit dashboard...")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "nba_dashboard.py"], check=True)


def main():
    try:
        run_pipeline()
    except subprocess.CalledProcessError as e:
        print(f"Pipeline failed: {e}")
        sys.exit(1)
    if not check_api_health():
        print("Aborting: FastAPI backend is not healthy or not running on port 8000.")
        sys.exit(1)
    try:
        launch_dashboard()
    except subprocess.CalledProcessError as e:
        print(f"Dashboard failed to launch: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
