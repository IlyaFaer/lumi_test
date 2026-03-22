import atexit
from pathlib import Path
import sys

from sqlalchemy import text
from sqlmodel import SQLModel, create_engine
from fastapi.testclient import TestClient
import pytest

DRIVER = "postgresql+psycopg"
DB_USER = "postgres"
DB_PASS = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"
TEST_DB_NAME = "luminary_test"

ADMIN_DB_URL = f"{DRIVER}://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/postgres"
TEST_DB_URL = f"{DRIVER}://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{TEST_DB_NAME}"


@pytest.fixture(scope="session")
def client():
    """Test client fixture."""
    from main import app

    with TestClient(app) as c:
        yield c


def teardown():
    """Drop the test db on exit."""
    try:
        test_engine.dispose()
        with admin_engine.connect() as conn:
            conn.execute(
                text(
                    (
                        "SELECT pg_terminate_backend(pid) FROM"
                        " pg_stat_activity WHERE datname=:d AND "
                        "pid <> pg_backend_pid()"
                    )
                ),
                {"d": TEST_DB_NAME},
            )
            conn.execute(text(f'DROP DATABASE IF EXISTS "{TEST_DB_NAME}"'))
    finally:
        admin_engine.dispose()


def setup():
    """Create a test database and engines."""
    admin_engine = create_engine(ADMIN_DB_URL, isolation_level="AUTOCOMMIT")

    with admin_engine.connect() as conn:
        conn.execute(text(f'DROP DATABASE IF EXISTS "{TEST_DB_NAME}"'))
        conn.execute(text(f'CREATE DATABASE "{TEST_DB_NAME}"'))

    test_engine = create_engine(TEST_DB_URL)
    SQLModel.metadata.create_all(test_engine)
    return admin_engine, test_engine


# original path
root = Path(__file__).resolve().parent.parent.joinpath("app")
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

# patch the db module so startup uses the test DB
import db as db_module  # noqa: E402

admin_engine, test_engine = setup()

db_module.engine = test_engine
atexit.register(teardown)
