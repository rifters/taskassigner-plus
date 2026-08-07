import os
import shutil
import tempfile


def backup_sqlite(db_path: str, backup_dir: str) -> str:
    if not os.path.exists(db_path):
        raise FileNotFoundError(db_path)
    os.makedirs(backup_dir, exist_ok=True)
    name = os.path.basename(db_path)
    out = os.path.join(backup_dir, f"backup-{name}")
    shutil.copy2(db_path, out)
    return out


if __name__ == "__main__":
    # Minimal manual runner
    default_db = os.getenv("TASKASSIGNER_DB_PATH", "taskassigner.db")
    default_dir = os.getenv("TASKASSIGNER_BACKUP_DIR", "backups")
    path = backup_sqlite(default_db, default_dir)
    print(path)
