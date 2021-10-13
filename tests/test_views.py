def test_robots(client):
    r = client.get("/robots.txt")
    assert r.data == b"User-agent: *\nDisallow: /"
