from fastapi.templating import Jinja2Templates

from backend.core.settings import BASE_DIR

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))