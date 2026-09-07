import bcrypt
import base64
import hashlib
from cryptography.fernet import Fernet

from backend.dependencies import get_settings

def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


class DekFernet:
    def __init__(self) -> None:
        settings = get_settings()
        key_bytes = hashlib.sha256(settings.SERVER_SECRET_KEY.encode()).digest()
        safe_key_bytes = base64.urlsafe_b64encode(key_bytes)
        
        self.fernet = Fernet(safe_key_bytes)
    
    def encrypt_dek(self, dek: bytes) -> str:
        encrypted = self.fernet.encrypt(dek)
        return encrypted.decode('utf-8')
    
    def decrypt_dek(self, encrypted_dek: str) -> bytes:
        decrypted = self.fernet.decrypt(encrypted_dek)
        return decrypted
            

    