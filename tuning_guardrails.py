import os
import csv
import datetime
import shutil

# CONFIGURABLES
ACCURACY_STOP_LOSS = 0.05  # 5% drop triggers revert
TUNING_INTERVAL_DAYS = 14
ACCURACY_LOG = 'accuracy_log.csv'  # CSV: date, version, accuracy
ALGO_VERSION_FILE = 'algo_version.txt'  # Current version
ALGO_BACKUP_DIR = 'algo_backups'

# --- Utility Functions ---
def read_accuracy_log():
    if not os.path.exists(ACCURACY_LOG):
        return []
    with open(ACCURACY_LOG, 'r') as f:
        reader = csv.DictReader(f)
        return list(reader)

def write_accuracy_log(date, version, accuracy):
    exists = os.path.exists(ACCURACY_LOG)
    with open(ACCURACY_LOG, 'a') as f:
        writer = csv.DictWriter(f, fieldnames=['date', 'version', 'accuracy'])
        if not exists:
            writer.writeheader()
        writer.writerow({'date': date, 'version': version, 'accuracy': accuracy})

def get_current_version():
    if not os.path.exists(ALGO_VERSION_FILE):
        return 'unknown'
    with open(ALGO_VERSION_FILE, 'r') as f:
        return f.read().strip()

def set_current_version(version):
    with open(ALGO_VERSION_FILE, 'w') as f:
        f.write(version)

def backup_algo(version):
    if not os.path.exists(ALGO_BACKUP_DIR):
        os.makedirs(ALGO_BACKUP_DIR)
    backup_path = os.path.join(ALGO_BACKUP_DIR, f'{version}_{datetime.date.today()}.zip')
    shutil.make_archive(backup_path.replace('.zip',''), 'zip', 'app')
    return backup_path

def revert_algo(prev_version):
    backup_path = os.path.join(ALGO_BACKUP_DIR, f'{prev_version}_{datetime.date.today()}.zip')
    if os.path.exists(backup_path):
        shutil.unpack_archive(backup_path, 'app', 'zip')
        set_current_version(prev_version)
        print(f'Reverted to version {prev_version}')
    else:
        print(f'Backup for version {prev_version} not found.')

# --- Main Tuning Logic ---
def check_stop_loss():
    log = read_accuracy_log()
    if len(log) < 2:
        return False
    prev = float(log[-2]['accuracy'])
    curr = float(log[-1]['accuracy'])
    drop = prev - curr
    if drop > ACCURACY_STOP_LOSS * prev:
        print(f'Accuracy drop {drop:.2%} exceeds stop loss. Reverting...')
        revert_algo(log[-2]['version'])
        return True
    return False

def run_tuning(new_version, new_accuracy):
    date = str(datetime.date.today())
    backup_algo(get_current_version())
    set_current_version(new_version)
    write_accuracy_log(date, new_version, new_accuracy)
    stop_loss_triggered = check_stop_loss()
    if stop_loss_triggered:
        print('Stop loss triggered. Reverted to previous version.')
    else:
        print('Tuning successful. New version deployed.')

# Example usage:
# run_tuning('v1.2.3', 0.57)

if __name__ == '__main__':
    import sys
    try:
        if len(sys.argv) == 3:
            version = sys.argv[1]
            accuracy = float(sys.argv[2])
            run_tuning(version, accuracy)
        else:
            print("Usage: python tuning_guardrails.py <version> <accuracy>")
    except Exception as e:
        print(f"Error running guardrails: {e}")
