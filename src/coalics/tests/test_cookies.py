import pytest


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client


def test_no_cookies(client):
    for url in ("/", "/imprint", "/privacy"):
        r = client.get(url)
        assert "Set-Cookie" not in r.headers, url
