def test_no_cookies(client):
    for url in ("/", "/imprint", "/privacy"):
        r = client.get(url)
        assert "Set-Cookie" not in r.headers, url
