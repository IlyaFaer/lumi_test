import atexit
from pathlib import Path
import uuid
import sys

from sqlalchemy import text
from sqlmodel import SQLModel, create_engine
from fastapi.testclient import TestClient
import pytest

# the original path
root = Path(__file__).resolve().parent.parent.joinpath("app")
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

# maintenance connection
ADMIN_DB_URL = "postgresql+psycopg://postgres:postgres@127.0.0.1:5432/postgres"

# create test database
_admin_engine = create_engine(ADMIN_DB_URL, isolation_level="AUTOCOMMIT")
_test_db_name = f"luminary_test_{uuid.uuid4().hex[:8]}"
with _admin_engine.connect() as conn:
    conn.execute(text(f'CREATE DATABASE "{_test_db_name}"'))

TEST_DB_URL = (
    "postgresql+psycopg://postgres:postgres" f"@127.0.0.1:5432/{_test_db_name}"
)
_test_engine = create_engine(TEST_DB_URL)

# create tables in the test DB
SQLModel.metadata.create_all(_test_engine)

# patch the db module so startup uses the test DB.
import db as db_module  # noqa: E402

db_module.engine = _test_engine


# drop db on exit
def _teardown():
    try:
        _test_engine.dispose()
        with _admin_engine.connect() as conn:
            conn.execute(
                text(
                    (
                        "SELECT pg_terminate_backend(pid) FROM"
                        " pg_stat_activity WHERE datname=:d AND "
                        "pid <> pg_backend_pid()"
                    )
                ),
                {"d": _test_db_name},
            )
            conn.execute(text(f'DROP DATABASE IF EXISTS "{_test_db_name}"'))
    finally:
        _admin_engine.dispose()


atexit.register(_teardown)


@pytest.fixture(scope="session")
def client():
    from main import app

    with TestClient(app) as c:
        yield c
