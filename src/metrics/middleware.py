from datetime import datetime, timezone
from fastapi import Request

from src.metrics.storage import metrics
from src.core.logger import get_logger

logger = get_logger(name=__name__)

async def logging_for_metrics(request: Request, call_next):
    is_include = True
    start = datetime.now(timezone.utc)
    try:
        bad_paths = ["/metrics", "/static", "/docs", ".", "/openai"]
        for path in bad_paths:
            if request.url.path.startswith(path):
                is_include = False
                break
        response = await call_next(request)
        if is_include:
            metrics.active_requests[request.method, request.url.path] += 1
            metrics.count_requests[(request.method, request.url.path, response.status_code)] += 1 
        return response
    except Exception as e:
        logger.exception(e)
        if is_include:
            metrics.count_requests[(request.method, request.url.path, 500)] += 1
        raise e
    finally:
        if is_include:
            duration = datetime.now(timezone.utc) - start
            metrics.duration[request.method, request.url.path].append(duration)
            metrics.active_requests[request.method, request.url.path] -= 1