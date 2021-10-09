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
