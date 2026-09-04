from backend.password_manager.core.crypto import (
    create_random_salt,
    derive_key,
    create_dek,
    decrypt_dek,
    encrypt_vault_passwords,
    decrypt_vault_passwords,
)
from backend.password_manager.schemas.passwords import Passwords, Password

def test_create_random_salt__different_salt():
    salt1 = create_random_salt()
    salt2 = create_random_salt()
    assert salt1 != salt2

def test_create_and_decrypt_dek():
    master_password = 'Password'
    salt = create_random_salt()
    kek = derive_key(master_password=master_password, salt_b64=salt)
    assert type(kek) == bytes
    
    dek, encrypted_dek = create_dek(kek=kek)
    decrypted_dek = decrypt_dek(kek=kek, encrypted_dek=encrypted_dek)
    assert decrypted_dek == dek

def test_encrypt_decrypt_passwords():
    master_password = 'Password'
    salt = create_random_salt()
    kek = derive_key(master_password=master_password, salt_b64=salt)
    assert type(kek) == bytes
    
    dek, encrypted_dek = create_dek(kek=kek)
    decrypted_dek = decrypt_dek(kek=kek, encrypted_dek=encrypted_dek)
    assert decrypted_dek == dek
    
    password = Password(
        service="service",
        username="username",
        password="password",
        note="note"
    )
    passwords = Passwords(passwords=[password])
    encrypted_passwords = encrypt_vault_passwords(passwords=passwords, key=dek)
    decrypted_passwords = decrypt_vault_passwords(encrypted_passwords=encrypted_passwords, key=dek)
    assert passwords == decrypted_passwords
    
    

