from backend.password_manager.schemas.users import UserData
from backend.password_manager.services.file_utils import load_data

def get_by_serivce__command(
    user_data: UserData,
    service: str,
    get_all: bool = False
):
    data = load_data(user_data=user_data)
    passwords = data.user_passwords
    
    if not data or passwords:
        raise ValueError("No entries were found")
    
    if get_all:
        passwords = sorted([p for p in passwords], key=lambda x: x.service)
    else:
        passwords = sorted([p for p in passwords if p.service.lower().startswith(service.lower())],
                        key=lambda p: p.service)
        
    
    return passwords
    
    
    