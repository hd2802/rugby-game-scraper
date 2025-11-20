from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def check_file_exists(file_name):
    FILE_PATH = BASE_DIR / "out" / file_name

    if FILE_PATH.exists():
        if FILE_PATH.stat().st_size == 0:
            print(f"{file_name} exists but is empty")
            return False
        else:
            print(f"{file_name} exists and is non-empty")
            return True
    else:
        print(f"{file_name} does not exist")
        return False