from pathlib import Path
from pydantic import BaseModel
import os

BASE_DIR = Path(__file__).resolve().parent.parent
NGINX_FILE = BASE_DIR / "nginx" / "nginx.conf"

class NginxSettings(BaseModel):    
    SERVER_NAME: str = os.getenv("SERVER_NAME", "localhost")
    PROXY_PASS: str = os.getenv("PROXY_PASS", "http://api:8000")
    


def main() -> None:
    try:
        if not NGINX_FILE.exists():
            raise FileExistsError(f"File {NGINX_FILE} does not exist")
        
        config = NginxSettings()
        
        lines = NGINX_FILE.read_text(encoding="utf-8")

        lines = (lines
                .replace("SERVER_NAME", config.SERVER_NAME)
                .replace("PROXY_PASS", config.PROXY_PASS)    
            )

        NGINX_FILE.write_text(lines, encoding="utf-8")
        print("Nginx was successfully configurated")
    except Exception as e:
        raise e    
    
if __file__ == "__main__":
    main()