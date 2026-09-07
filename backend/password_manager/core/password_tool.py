import secrets
from sqlalchemy.ext.asyncio import AsyncSession
from cryptography.fernet import InvalidToken

from backend.dao.vaultDao import VaultDao
from backend.models.model import Vaults
from backend.password_manager.schemas.passwords import Password, Passwords
from backend.password_manager.core.crypto import (
    decrypt_vault_passwords,
    encrypt_vault_passwords
)



class PasswordTool:
    def __init__(self, user_id: int, vault: Vaults, dek: bytes, session: AsyncSession) -> None:
        self.user_id = user_id
        self.session = session
        self.dao = VaultDao(session=session)
        self.dek: bytes = dek   
        self.vault: Vaults = vault
        
        
        
        
    def _load_passwords(self) -> Passwords:
        try:
            if self.vault and self.dek:
                decrypted_passwords = decrypt_vault_passwords(encrypted_passwords=self.vault.encrypted_passwords, key=self.dek)
            else:
                raise ValueError("No vault or no dek")
            return decrypted_passwords
        
        except InvalidToken:
            raise ValueError("Wrong master password")
        except Exception as e:
            raise e
            
    async def _save_passwords(self, passwords: Passwords) -> None:
        if self.vault:
            encrypted_passwords = encrypt_vault_passwords(passwords=passwords, key=self.dek)
            self.vault.encrypted_passwords = encrypted_passwords
            await self.session.commit()
        else:
            raise ValueError("No vault or no dek")
        
        
    
    async def add_command(self,
                    service: str,
                    username: str,
                    password: str = "",
                    note: str = "",):
        if not password:
            password = secrets.token_urlsafe(24)
        
        passwords = self._load_passwords()
        
        labels = set(p.service for p in passwords.passwords)
        candidate = service.strip()
        i = 1
        while candidate in labels:
            candidate = service + '-' + str(i)
            i += 1
        
        password_to_add = Password(
            service=candidate,
            username=username,
            password=password,
            note=note
        )
        passwords.passwords.append(password_to_add)
        
        await self._save_passwords(passwords=passwords)
            
    async def get_command(
                    self,
                    service: str,
                    get_all: bool = False,
                    strict: bool = False
                        ) -> Password | list[Password]:
        data = self._load_passwords()
        
        
        if not data:
            raise ValueError("No entries were found")

        if get_all:
            passwords = sorted([p for p in data.passwords], key=lambda x: x.service)
        elif strict:
            for p in data.passwords:
                if p.service.lower() == service.lower():
                    return p
            return []
        else:
            passwords = sorted([p for p in data.passwords if p.service.lower().startswith(service.lower())],
                            key=lambda p: p.service)
            
        return passwords
    
    async def delete_command(
        self,
        service: str,
        delete_all: bool = False
    ):
        passwords = self._load_passwords()
        
        is_deleted = False
        if delete_all:
            passwords.passwords = []
            is_deleted = True
        else:
            for pas in passwords.passwords:
                if pas.service == service:
                    passwords.passwords.remove(pas)
                    is_deleted = True
                    break
        
        if not is_deleted:
            raise ValueError("Wrong service")
        
        await self._save_passwords(passwords=passwords)
        
    async def edit_command(
        self,
        serivce: str,
        username: str | None = None,
        password: str | None = None,
        note: str | None = None
    ):
        passwords = self._load_passwords()
        
        #Finding password to edit
        pas_to_change = None
        for pas in passwords.passwords:
            if pas.service == serivce.strip():
                pas_to_change = pas
                break
        
        if not pas_to_change:
            raise ValueError("Wrong service label to edit")
        
        pas_to_change.username = (username if username is not None else pas_to_change.username)
        pas_to_change.password = (password if password is not None else pas_to_change.password)
        pas_to_change.note = (note if note is not None else pas_to_change.note)
        
        await self._save_passwords(passwords=passwords)
        
        
    
        