import time
from enum import StrEnum
from starletter.middleware.base import BaseHTTPMiddleware
from typing import Dict, List, Optional
from collections import defaultdict
from .logging import getLogger
from fastapi import Response, Request
from .settings import Settings

settings = Settings()




class MiddlewareTypes(StrEnum):
    jwt_authentication = "jwt_authentication"
    api_key = "api_key"
    cors = "cors"
    limit_rate = "limit_rate"


class JWTAuthenticationMiddleware(BaseHTTPMiddleware):
    pass


class APIKeyMiddleware(BaseHTTPMiddleware):
    """Middleware for API Key authentication"""
    
    def __init__(self, app, public_paths: Optional[List[str]] = None):
        super().__init__(app)
        self.public_paths = public_paths or ["/docs", "/openapi.json", "/redoc", "/health"]
        self.logger = getLogger()
    
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        
        # Skip API key validation for public paths
        if any(path.startswith(public_path) for public_path in self.public_paths):
            return await call_next(request)
        
        # Check API key
        api_key = request.headers.get(settings.APP_API_KEY_HEADER)
        
        if not api_key or api_key not in settings.APP_API_KEY.split(","):
            self.logger.warning(f"Invalid API key attempt from {request.client.host} to {path}")
            return Response(
                content='{"detail": "Invalid or missing API key"}',
                status_code=401,
                media_type="application/json"
            )
        
        self.logger.info(f"Valid API key from {request.client.host} to {path}")
        return await call_next(request)


class CORSMiddleware(BaseHTTPMiddleware):
    """Custom CORS middleware with configurable origins"""
    
    def __init__(self, app):
        super().__init__(app)
        self.logger = getLogger()
    
    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin")
        
        # Handle preflight requests
        if request.method == "OPTIONS":
            if origin in settings.CORS_ALLOWED_ORIGINS:
                return Response(
                    status_code=200,
                    headers=self._get_cors_headers(origin)
                )
            return Response(status_code=403)
        
        # Process the request
        response = await call_next(request)
        
        # Add CORS headers to response if origin is allowed
        if origin in settings.CORS_ALLOWED_ORIGINS:
            for header, value in self._get_cors_headers(origin).items():
                response.headers[header] = value
        
        return response
    
    def _get_cors_headers(self, origin: str) -> Dict[str, str]:
        """Get CORS headers for allowed origin"""
        return {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": str(settings.CORS_ALLOW_CREDENTIALS).lower(),
            "Access-Control-Allow-Methods": ", ".join(settings.CORS_ALLOW_METHODS),
            "Access-Control-Allow-Headers": ", ".join(settings.CORS_ALLOW_HEADERS),
            "Access-Control-Max-Age": str(settings.CORS_MAX_AGE),
        }


class LimitRateHeaderMiddleware(BaseHTTPMiddleware):
    """Middleware for custom headers and rate limiting"""
    
    def __init__(self, app, header_name: str, header_value: str):
        super().__init__(app)
        self.header_name = header_name
        self.header_value = header_value
        self.rate_limit_record: Dict[str, float] = defaultdict(float)

    async def log_message(self, message: str):
        logger = getLogger()
        logger.info(message)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()
        
        # Simple rate limiting: allow one request every N seconds per IP
        if current_time - self.rate_limit_record[client_ip] < settings.RATE_LIMIT_SECONDS:
            return Response(content="Too Many Requests", status_code=429)
        
        self.rate_limit_record[client_ip] = current_time
        path = request.url.path
        await self.log_message(f"Request from {client_ip} to {path}")
        
        # process the request
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        custom_headers = {self.header_name: self.header_value,
                          "X-Process-Time": str(process_time)}
        
        for header, value in custom_headers.items():
            response.headers[header] = value

        await self.log_message(f"Response to {client_ip} from {path} with headers {custom_headers}")
        return response