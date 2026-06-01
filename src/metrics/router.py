from fastapi import APIRouter

from src.core.logger import get_logger
from src.metrics.storage import metrics as storage

logger = get_logger(__name__)

metrics = APIRouter()


@metrics.get("/health")
async def health():
    #check db, nginx, api
    
    return {
        "ok": True
    }

@metrics.get("/metrics")
async def get_metrics():
    count = [{"method": method, "path": path, "status_code": code, "count": count} for (method, path, code), count in storage.count_requests.items()]
    active = [{"method": method, "path": path, "count": count} for (method, path), count in storage.active_requests.items()]
    duration = [{"method": method, "path": path, "count": count} for (method, path), count in storage.duration.items()]
    
    
    return {
        "request_count": count,
        "active_requests": active,
        "duration": duration
    }