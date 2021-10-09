from flask.globals import current_app


def test_no_cookies(client):

    for url in ("/", "/imprint", "/privacy"):
        r = client.get(url)
        assert "Set-Cookie" not in r.headers, url

    current_app.testing = False  # disable: forms only show CSRF when not in testing
    for url in ("/login", "/register"):
        r = client.get(url)
        # these do set a cookie because of CSRF
        assert "Set-Cookie" in r.headers, url
