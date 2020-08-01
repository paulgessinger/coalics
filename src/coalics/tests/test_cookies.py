import pytest
from coalics import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    app.secret_key = "ABCDEF"

    with app.test_client() as client:
        yield client


def test_no_cookies(client):
    for url in ("/", "/imprint", "/privacy"):
        r = client.get(url)
        assert "Set-Cookie" not in r.headers
