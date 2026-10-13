from pathlib import Path


BASE_DIR = Path(Path(__file__).parent.parent.parent.parent / 'PASSWORDS_DATA').resolve()
EXPORT_DIR = BASE_DIR / "exports"
VAULTS = BASE_DIR / "vaults"
IMPORT_DIR = BASE_DIR / "imports"
TEMPORARY_FILES = BASE_DIR / 'temporary_files'
for dir in (BASE_DIR, EXPORT_DIR, VAULTS, IMPORT_DIR, TEMPORARY_FILES):
    dir.mkdir(parents=True, exist_ok=True)



