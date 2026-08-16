# import json
# import os
# from pathlib import Path

# import typer
# from cryptography.fernet import InvalidToken

# from backend.password_manager.core.crypto import (
#     decrypt_vault_passwords,
#     encrypt_vault_passwords,
# )
# from backend.password_manager.core.config import (
#     BASE_DIR,
#     VAULTS,
# )
# from backend.password_manager.schemas.passwords import (
#     Passwords,
#     UserVault,
#     EncryptedUserVault,
# )
# from backend.password_manager.schemas.users import UserData



# def load_encrypted_vault(username: str, vault_name: str) -> EncryptedUserVault:
#     vault_file = VAULTS / username / f"{vault_name}.json"
#     try:
#         with open(vault_file, "r", encoding="utf-8") as f:
#             data = f.read()

#         return EncryptedUserVault.model_validate_json(data)

#     except FileNotFoundError as e:
#         raise FileNotFoundError(
#             f"Файл хранилища пользователя {username}.json не найден"
#         ) from e

#     except OSError as e:
#         raise RuntimeError(
#             f"Ошибка чтения файла хранилища {username}.json"
#         ) from e


# def load_data(user_data: UserData, vault_name: str) -> UserVault:
#     from backend.password_manager.services.password import get_key
    
#     encrypted = load_encrypted_vault(username=user_data.username, vault_name=vault_name)

#     try:
#         key = get_key(user_data=user_data, vault_name=vault_name)
#     except InvalidToken as e:
#         typer.echo("Wrong master password")
#         raise typer.Exit(code=1) from e

#     if key is None:
#         raise RuntimeError("Ключ из текущей сессии отсутствует")

#     decoded_passwords = decrypt_vault_passwords(
#         encrypted.encrypted_passwords,
#         key,
#     )

#     vault_data = UserVault(
#         name=encrypted.name,
#         username=encrypted.username,
#         salt=encrypted.salt,
#         user_passwords=decoded_passwords.passwords,
#     )

#     return vault_data


# def save_data(user_data: UserData, vault_data: UserVault) -> None:
#     from backend.password_manager.services.password import get_key

#     vault_file = VAULTS / user_data.username / f"{vault_data.name}.json"

#     if not vault_file.exists():
#         raise FileExistsError(
#             f"Файл {vault_data.username}.json не существует"
#         )

#     key = get_key(user_data=user_data, vault_name=vault_data.name)

#     if key is None:
#         raise RuntimeError("Ключ из текущей сессии отсутствует")

#     encrypted_passwords = encrypt_vault_passwords(
#         Passwords(passwords=vault_data.user_passwords),
#         key,
#     )

#     encrypted_vault = EncryptedUserVault(
#         name=vault_data.name,
#         username=vault_data.username,
#         salt=vault_data.salt,
#         encrypted_passwords=encrypted_passwords,
#     )

#     try:
#         with open(vault_file, "w", encoding="utf-8") as f:
#             f.write(encrypted_vault.model_dump_json())

#     except OSError as e:
#         raise RuntimeError(
#             f"Ошибка сохранения файла {vault_data.username}.json"
#         ) from e

#     typer.echo("Данные успешно сохранены.")


# def delete_file(filename: Path) -> None:
#     file_to_delete = BASE_DIR / filename

#     if not file_to_delete.exists():
#         raise FileNotFoundError(
#             f"Файл {filename} не обнаружен"
#         )

#     try:
#         os.remove(file_to_delete)

#     except OSError as e:
#         raise RuntimeError(
#             f"Ошибка при удалении файла {filename}"
#         ) from e

#     typer.echo(f"Файл {filename} успешно удалён.")


# def get_user_vault_files() -> list[Path]:
#     return list(VAULTS.glob("*.json"))


# def is_vault_files_exists() -> bool:
#     return bool(get_user_vault_files())


# def get_vault_usernames() -> list[str]:
#     vaults = get_user_vault_files()

#     if not vaults:
#         raise FileNotFoundError(
#             "Нет файлов хранилищ для получения имён пользователей"
#         )

#     usernames: list[str] = []

#     for vault_file in vaults:
#         try:
#             with open(vault_file, "r", encoding="utf-8") as f:
#                 data = f.read()

#             encrypted = EncryptedUserVault.model_validate_json(data)
#             usernames.append(encrypted.username)

#         except OSError as e:
#             raise RuntimeError(
#                 f"Ошибка чтения файла {vault_file.name}"
#             ) from e

#     return usernames