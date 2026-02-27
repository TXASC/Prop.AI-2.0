import subprocess
import sys
import os
from datetime import date
import requests
def check_python_env():
    # Check if running inside .venv
    venv_path = os.environ.get('VIRTUAL_ENV')
    if not venv_path:
        venv_candidate = os.path.join(os.getcwd(), '.venv')
        if os.path.exists(venv_candidate):
            activate_script = os.path.join(venv_candidate, 'Scripts', 'activate_this.py')
            if os.path.exists(activate_script):
                print('Auto-activating .venv...')
                exec(open(activate_script).read(), {'__file__': activate_script})
            else:
                print('Warning: .venv exists but activate_this.py not found. Please activate manually.')
        else:
            print('Warning: .venv not found. Please create and activate your virtual environment.')
    # Check Python version
    if sys.version_info < (3, 8):
        print('Python 3.8+ is required. Please upgrade your Python environment.')
        sys.exit(1)


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
    check_python_env()
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
