from coalics.models import HashedPassword, User, db, crypt_context


def test_password():
    pwd = "PASSWORT"
    hashed = HashedPassword.from_password(pwd)

    assert hashed == pwd
    assert hashed != HashedPassword.from_password(pwd)
    assert hashed == HashedPassword(hashed.hash)
    assert hashed != "NOPE"
    assert hashed != HashedPassword.from_password("NOPE")
    assert hashed == HashedPassword(hashed.hash)


def test_user_email(app):
    email = "abc@example.com"
    new_user = User(email=email, password="pwd")
    db.session.add(new_user)
    db.session.commit()

    assert new_user.email != email
    assert new_user.email == crypt_context.handler().using(
        salt=app.config["EMAIL_SALT"]
    ).hash(email)
    loaded = User.find_by_email(email)
    assert new_user == loaded
