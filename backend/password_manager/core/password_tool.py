import secrets
from sqlalchemy.ext.asyncio import AsyncSession
from cryptography.fernet import InvalidToken

from backend.dao.vaultDao import VaultDao, VaultFields
from backend.models.model import Vaults
from backend.password_manager.schemas.passwords import Password, Passwords
from backend.password_manager.core.crypto import (
    derive_key,
    decrypt_dek,
    decrypt_vault_passwords,
    encrypt_vault_passwords
)



class PasswordTool:
    def __init__(self, user_id: int, vault_id: int, dek: bytes, session: AsyncSession) -> None:
        self.user_id = user_id
        self.vault_id = vault_id
        self.session = session
        self.dao = VaultDao(session=session)
        self.dek: bytes = dek   
        self.vault: Vaults | None = None
        
        
        
        
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
                    get_all: bool = False
                        ):
        passwords = self._load_passwords()
        
        
        if not passwords:
            raise ValueError("No entries were found")

        if get_all:
            passwords = sorted([p for p in passwords.passwords], key=lambda x: x.service)
        else:
            passwords = sorted([p for p in passwords.passwords if p.service.lower().startswith(service.lower())],
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
        username: str = '',
        password: str = '',
        note: str = ''
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
        
        pas_to_change.username = (username if username else pas_to_change.username)
        pas_to_change.password = (password if password else pas_to_change.password)
        pas_to_change.note = (note if note else pas_to_change.note)
        
        await self._save_passwords(passwords=passwords)
        
        
    
        