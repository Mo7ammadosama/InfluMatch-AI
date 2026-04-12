from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from collections import defaultdict
from datetime import datetime, timedelta
from loguru import logger

class RateLimiter(BaseHTTPMiddleware):
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = timedelta(seconds=period)
        self._store: dict = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        now = datetime.utcnow()
        self._store[client_ip] = [t for t in self._store[client_ip] if now - t < self.period]
        if len(self._store[client_ip]) >= self.calls:
            logger.warning(f"[ARIA::RATELIMIT] Rate limit exceeded: {client_ip}")
            return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded. Try again later."})
        self._store[client_ip].append(now)
        return await call_next(request)
