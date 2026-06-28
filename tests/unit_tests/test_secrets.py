from src.services.secrets import verify_password, hash_password


def test_hash_password__returs_str():
    hashed = hash_password(password="password")
    assert type(hashed) == str
    
def test_hash_password__different_passwords__different_hashes():
    h1 = hash_password(password="password1")
    h2 = hash_password(password="password2")
    assert h1 != h2

def test_hash_password__same_passwords__different_hashes():
    h1 = hash_password(password="password")
    h2 = hash_password(password="password")
    assert h1 != h2


def test_verify_password__ok():
    password = "password"
    hashed = hash_password(password=password)
    assert verify_password(password=password, password_hash=hashed)
    
def test_verify_password__wrong_password():
    wrong_password = "wrong_password"
    hashed = hash_password(password="password")
    assert not verify_password(password=wrong_password, password_hash=hashed)
    