from typing import Literal



from backend.password_manager.core.crypto import(
    create_random_salt,
    derive_key,
    create_dek,
    encrypt_vault_passwords
    
)
from backend.password_manager.core.config import (
    VAULTS,
    BASE_DIR
)
from backend.password_manager.schemas.passwords import (
    EncryptedData,
    Passwords
)
# from backend.password_manager.services.file_utils import (
#     load_encrypted_vault, is_vault_files_exists, get_vault_usernames
# )


# new_vault = VAULTS / username / f"{vault_name}.json"

        


def create_user_vault(master_password: str) -> EncryptedData:
    salt = create_random_salt()
    kek = derive_key(master_password=master_password, salt_b64=salt)
    dek, encrypted_dek = create_dek(kek=kek)
    encrypted_passwords = encrypt_vault_passwords(passwords=Passwords(passwords=[]), key=dek)
    
    return EncryptedData(
        encrypted_passwords=encrypted_passwords,
        encrypted_dek=encrypted_dek,
        salt=salt
    )
    


def check_is_vault_exists(username: str, vault_name: str) -> bool:
    new_vault = VAULTS / username / f"{vault_name}.json"
    if new_vault.exists():
        return True
    return False 

def find_digits_in_a_row(row: str) -> int:
    result = 0
    left = 0
    while left < len(row):
        while left < len(row) and not row[left].isdigit():
            left += 1
        right = left + 1
        while right < len(row) and row[right].isdigit():
            right += 1
        result = max(result, right - left + 1)
        left = right
    return result


def is_common_pattern(password: str) -> bool:
    """Check for common weak patterns (sequential, repeated chars, etc)."""
    common_patterns = [
        "123", "321", "012", "456", "789",
        "abc", "bcd", "xyz", "qwerty", "qwertyuiop",
        "aaa", "bbb", "ccc", "111", "222", "000",
        "password", "pass", "admin", "user", "test"
    ]
    
    pwd_lower = password.lower()
    for pattern in common_patterns:
        if pattern in pwd_lower:
            return True
    return False


PASSWORD_STRENGTH_LEVEL = Literal["HIGH", "MEDIUM", "LOW"]
def check_password_strength(password: str) -> PASSWORD_STRENGTH_LEVEL:
    score = 0
    
    data_folder = BASE_DIR / "data"
    data_files = [f for f in data_folder.rglob("*.txt")]
    for file in data_files:
        if not file.exists():
            continue
        data = file.read_text()
        if password in data:
            return "LOW"
    
    if is_common_pattern(password):
        return "LOW"
    
    if len(password) < 8:
        return "LOW"
    elif len(password) >= 16:
        score += 3
    elif len(password) >= 12:
        score += 2
    else:
        score += 1
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)
    
    variety = sum([has_upper, has_lower, has_digit, has_special])
    if variety >= 4:
        score += 3
    elif variety >= 3:
        score += 2
    elif variety >= 2:
        score += 1
    else:
        return "LOW"
    
    digits = find_digits_in_a_row(row=password)
    
    if digits >= 3:
        score -= 1
    
    if score >= 6:
        return "HIGH"
    elif score >= 3:
        return "MEDIUM"
    else:
        return "LOW"
        



