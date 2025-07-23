# conftest.py (create this file in tests directory)
import pytest
from django.db import connection

@pytest.fixture(autouse=True)
def reset_db_connections():
    yield
    connection.close()