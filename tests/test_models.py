import pytest

from coalics.models import HashedPassword


def test_hashedpassword():

    pw = HashedPassword.from_password("abcabc")
    assert pw == pw
    assert pw == "abcabc"
    assert pw != "nope"
    pw2 = HashedPassword.from_password("abcabc")
    assert pw != pw2
    with pytest.raises(TypeError):
        pw == 5

