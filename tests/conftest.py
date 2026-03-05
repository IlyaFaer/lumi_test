# tests/conftest.py
import sys
from pathlib import Path
import uuid
import atexit

from sqlmodel import SQLModel, create_engine
from sqlalchemy import text
from fastapi.testclient import TestClient
import pytest

# keep original path insertion
ROOT = Path(__file__).resolve().parent.parent.joinpath("app")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Admin/maintenance connection (connects to the default 'postgres' DB on host)
ADMIN_DB_URL = "postgresql+psycopg://postgres:postgres@127.0.0.1:5432/postgres"

# Create a unique test database immediately so imports of `main` use the test engine.
_admin_engine = create_engine(ADMIN_DB_URL, isolation_level="AUTOCOMMIT")
_test_db_name = f"luminary_test_{uuid.uuid4().hex[:8]}"
with _admin_engine.connect() as conn:
    conn.execute(text(f'CREATE DATABASE "{_test_db_name}"'))

TEST_DB_URL = f"postgresql+psycopg://postgres:postgres@127.0.0.1:5432/{_test_db_name}"
_test_engine = create_engine(TEST_DB_URL)

# Create all tables in the test DB
SQLModel.metadata.create_all(_test_engine)

# Patch the app's db module engine so startup uses the test DB.
import db as db_module  # app/db/__init__.py is importable as `db` because ROOT was added

db_module.engine = _test_engine


# Ensure the test DB is dropped at process exit
def _teardown():
    try:
        _test_engine.dispose()
        with _admin_engine.connect() as conn:
            conn.execute(
                text(
                    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname=:d AND pid <> pg_backend_pid()"
                ),
                {"d": _test_db_name},
            )
            conn.execute(text(f'DROP DATABASE IF EXISTS "{_test_db_name}"'))
    finally:
        _admin_engine.dispose()


atexit.register(_teardown)


@pytest.fixture(scope="session")
def client():
    # Import main after we've patched db.engine above
    from main import app

    with TestClient(app) as c:
        yield c
