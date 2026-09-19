from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import time
from loguru import logger

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        ms = round((time.perf_counter() - start) * 1000, 2)
        logger.info(f"{request.method} {request.url.path} -> {response.status_code} ({ms}ms)")
        return response
