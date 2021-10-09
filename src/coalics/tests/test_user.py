import pytest
from coalics import User
from flask import url_for
from sqlalchemy.orm.exc import NoResultFound


def test_user_login(client):
    r = client.get("/calendar")
    assert r.status_code == 302
    assert r.headers["Location"].endswith(url_for("login", next="/calendar"))

    r = client.post("/login", data=dict(email="test@example.com", password="hallo"))
    assert r.status_code == 302

    r = client.get("/calendar")
    assert r.status_code == 200
    assert b"logout" in r.data, "There is no logout button"

    r = client.get("/logout")
    assert r.status_code == 405

    r = client.post("/logout")
    assert r.status_code == 302
    assert r.headers["Location"].endswith(url_for("login"))

    # after logout, not logged in anymore
    r = client.get("/calendar")
    assert r.status_code == 302
    assert r.headers["Location"].endswith(url_for("login", next="/calendar"))


def test_user_registration(app, client):
    email = "new@example.com"
    password = "123456"

    with pytest.raises(NoResultFound):
        User.query.filter_by(email=email).one()

    r = client.post("/login", data=dict(email=email, password=password))
    assert b"Invalid login info" in r.data
    assert r.status_code == 403

    r = client.post(
        "/register", data=dict(email=email, password=password, password2="nope")
    )
    assert b"Error creating account" in r.data
    assert r.status_code == 400

    r = client.post(
        "/register",
        data=dict(email="not an email", password=password, password2=password),
    )
    assert b"Error creating account" in r.data
    assert r.status_code == 400

    r = client.post(
        "/register", data=dict(email=email, password=password, password2=password)
    )
    assert r.status_code == 400

    r = client.post(
        "/register",
        data=dict(email=email, password=password, password2=password, gdpr1=True),
    )
    assert r.status_code == 302
    assert r.headers["Location"].endswith(url_for("calendars"))

    User.query.filter_by(email=email).one()

    r = client.post("/login", data=dict(email=email, password="nope"))
    assert r.status_code == 403

    r = client.post("/login", data=dict(email=email, password=password))
    assert r.status_code == 302
    assert r.headers["Location"].endswith(url_for("calendars"))
