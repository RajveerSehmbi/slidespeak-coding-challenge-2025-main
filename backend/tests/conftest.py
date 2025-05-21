from unittest.mock import Mock
from app import create_app
import pytest


@pytest.fixture(scope="session")
def client():
    app = create_app()
    app.config["TESTING"] = True

    mock_redis = Mock()
    app.redis = mock_redis
    return app.test_client()
