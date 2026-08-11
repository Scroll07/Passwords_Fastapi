import secrets

from backend.password_manager.services.file_utils import (
    load_data,
    save_data
)
from backend.password_manager.schemas.users import UserData
from backend.password_manager.schemas.passwords import Password

class PasswordTool:
    def __init__(self, user_data: UserData, vault_name: str) -> None:
        self.user_data = user_data
        self.vault_name = vault_name
        
    def add_command(self,
                    service: str,
                    username: str,
                    password: str = "",
                    note: str = "",):
        if not password:
            password = secrets.token_urlsafe(24)
        
        data = load_data(user_data=self.user_data, vault_name=self.vault_name)
        
        labels = set(b.service for b in data.user_passwords)
        candidate = service.strip()
        i = 1
        while candidate in labels:
            candidate = service + '-' + str(i)
        
        password_to_add = Password(
            service=candidate,
            username=username,
            password=password,
            note=note
        )
        data.user_passwords.append(password_to_add)
        
        save_data(user_data=self.user_data, vault_data=data)
            
    def get_command(
                    self,
                    service: str,
                    get_all: bool = False
                        ):
        data = load_data(user_data=self.user_data, vault_name=self.vault_name)
        passwords = data.user_passwords

        if not data or passwords:
            raise ValueError("No entries were found")

        if get_all:
            passwords = sorted([p for p in passwords], key=lambda x: x.service)
        else:
            passwords = sorted([p for p in passwords if p.service.lower().startswith(service.lower())],
                            key=lambda p: p.service)
            
        return passwords
    
    def delete_command(
        self,
        service: str,
        delete_all: bool = False
    ):
        data = load_data(user_data=self.user_data, vault_name=self.vault_name)
        
        is_deleted = False
        if delete_all:
            data.user_passwords = []
            is_deleted = True
        else:
            for pas in data.user_passwords:
                if pas.service == service:
                    data.user_passwords.remove(pas)
                    is_deleted = True
                    break
        
        if not is_deleted:
            raise ValueError("Wrong service")
        
        save_data(user_data=self.user_data, vault_data=data)
        
    def edit_command(
        self,
        serivce: str,
        username: str = '',
        password: str = '',
        note: str = ''
    ):
        data = load_data(user_data=self.user_data, vault_name=self.vault_name)
        
        #Finding password to edit
        pas_to_change = None
        for pas in data.user_passwords:
            if pas.service == serivce.strip():
                pas_to_change = pas
                break
        
        if not pas_to_change:
            raise ValueError("Wrong service label to edit")
        
        pas_to_change.username = (username if username else pas_to_change.username)
        pas_to_change.password = (password if password else pas_to_change.password)
        pas_to_change.note = (note if note else pas_to_change.note)
        
        save_data(user_data=self.user_data, vault_data=data)
        
        
    
        