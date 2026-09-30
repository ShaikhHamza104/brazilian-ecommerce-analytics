import os

from dotenv import load_dotenv
import pytest

load_dotenv()


@pytest.mark.db
def test_environment_variables():
    """Check required database environment variables are set."""
    required = ["DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT", "DB_NAME"]
    for var in required:
        val = os.getenv(var)
        assert val is not None, f"Variable {var} is not set"
        assert val.strip() != "", f"Variable {var} is empty"


@pytest.mark.db
def test_optional_ssl_certificate():
    """Check SSL CA path if configured."""
    ca_path = os.getenv("DB_SSL_CA_PATH")
    if ca_path:
        assert ca_path.strip() != ""
