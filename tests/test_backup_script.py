import os
import tempfile

from scripts.backup_sqlite import backup_sqlite


def test_backup_sqlite_creates_copy():
    with tempfile.TemporaryDirectory() as td:
        db_file = os.path.join(td, "taskassigner.db")
        with open(db_file, "wb") as f:
            f.write(b"sqlite-bytes")

        backup_dir = os.path.join(td, "backups")
        out = backup_sqlite(db_file, backup_dir)

        assert os.path.exists(out)
        with open(out, "rb") as f:
            assert f.read() == b"sqlite-bytes"


def test_backup_sqlite_raises_when_source_missing():
    with tempfile.TemporaryDirectory() as td:
        missing = os.path.join(td, "missing.db")
        backup_dir = os.path.join(td, "backups")
        try:
            backup_sqlite(missing, backup_dir)
            assert False, "expected FileNotFoundError"
        except FileNotFoundError:
            pass
