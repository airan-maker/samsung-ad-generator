"""
Security Middleware

Provides security-related middleware for the FastAPI application.
"""

from fastapi import Request, HTTPException, status
from fastapi.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Callable, Dict, Set, Optional
import time
import hashlib
import re
import logging
from collections import defaultdict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using token bucket algorithm.
    """

    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        burst_size: int = 10,
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.buckets: Dict[str, dict] = defaultdict(
            lambda: {"tokens": burst_size, "last_update": time.time()}
        )

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/api/v1/health"]:
            return await call_next(request)

        client_ip = self._get_client_ip(request)
        bucket = self.buckets[client_ip]

        # Refill tokens
        now = time.time()
        time_passed = now - bucket["last_update"]
        tokens_to_add = time_passed * (self.requests_per_minute / 60)
        bucket["tokens"] = min(self.burst_size, bucket["tokens"] + tokens_to_add)
        bucket["last_update"] = now

        if bucket["tokens"] < 1:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
                headers={"Retry-After": "60"},
            )

        bucket["tokens"] -= 1
        response = await call_next(request)
        return response

    def _get_client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Adds security headers to all responses.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "accelerometer=(), camera=(), geolocation=(), gyroscope=(), "
            "magnetometer=(), microphone=(), payment=(), usb=()"
        )

        # Content Security Policy (adjust for your needs)
        if not request.url.path.startswith("/api/"):
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self' https://api.saiad.io; "
                "frame-ancestors 'none';"
            )

        return response


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """
    Validates and sanitizes incoming requests.
    """

    # Patterns to detect potential attacks
    SQL_INJECTION_PATTERNS = [
        r"(\%27)|(\')|(\-\-)|(\%23)|(#)",
        r"(\%3D)|(=)[^\n]*(\')|(\-\-)|(\%3B)|(\;)",
        r"\w*((\%27)|(\'))((\%6F)|o|(\%4F))((\%72)|r|(\%52))",
        r"((\%27)|(\'))union",
    ]

    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"onerror\s*=",
        r"onload\s*=",
        r"<iframe[^>]*>",
    ]

    PATH_TRAVERSAL_PATTERNS = [
        r"\.\./",
        r"\.\.\\",
        r"%2e%2e%2f",
        r"%2e%2e/",
    ]

    def __init__(self, app):
        super().__init__(app)
        self.sql_patterns = [re.compile(p, re.IGNORECASE) for p in self.SQL_INJECTION_PATTERNS]
        self.xss_patterns = [re.compile(p, re.IGNORECASE) for p in self.XSS_PATTERNS]
        self.path_patterns = [re.compile(p, re.IGNORECASE) for p in self.PATH_TRAVERSAL_PATTERNS]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check URL path
        if self._contains_malicious_content(request.url.path, "path"):
            logger.warning(f"Blocked path traversal attempt: {request.url.path}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid request",
            )

        # Check query parameters
        query_string = str(request.url.query)
        if self._contains_malicious_content(query_string, "sql"):
            logger.warning(f"Blocked SQL injection attempt in query: {query_string}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid request",
            )

        if self._contains_malicious_content(query_string, "xss"):
            logger.warning(f"Blocked XSS attempt in query: {query_string}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid request",
            )

        return await call_next(request)

    def _contains_malicious_content(self, content: str, check_type: str) -> bool:
        if check_type == "sql":
            patterns = self.sql_patterns
        elif check_type == "xss":
            patterns = self.xss_patterns
        elif check_type == "path":
            patterns = self.path_patterns
        else:
            return False

        for pattern in patterns:
            if pattern.search(content):
                return True
        return False


class IPBlocklistMiddleware(BaseHTTPMiddleware):
    """
    Blocks requests from blacklisted IPs.
    """

    def __init__(self, app, blocked_ips: Optional[Set[str]] = None):
        super().__init__(app)
        self.blocked_ips = blocked_ips or set()
        self.failed_attempts: Dict[str, list] = defaultdict(list)
        self.max_failed_attempts = 10
        self.block_duration = timedelta(hours=1)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = self._get_client_ip(request)

        # Check if IP is permanently blocked
        if client_ip in self.blocked_ips:
            logger.warning(f"Blocked request from blacklisted IP: {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        # Check if IP is temporarily blocked due to failed attempts
        if self._is_temporarily_blocked(client_ip):
            logger.warning(f"Blocked request from temporarily blocked IP: {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Too many failed attempts. Please try again later.",
            )

        response = await call_next(request)

        # Track failed authentication attempts
        if response.status_code == 401:
            self._record_failed_attempt(client_ip)

        return response

    def _get_client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _record_failed_attempt(self, ip: str):
        now = datetime.utcnow()
        self.failed_attempts[ip].append(now)

        # Clean old attempts
        cutoff = now - self.block_duration
        self.failed_attempts[ip] = [
            t for t in self.failed_attempts[ip] if t > cutoff
        ]

    def _is_temporarily_blocked(self, ip: str) -> bool:
        if ip not in self.failed_attempts:
            return False

        now = datetime.utcnow()
        cutoff = now - self.block_duration
        recent_attempts = [
            t for t in self.failed_attempts[ip] if t > cutoff
        ]

        return len(recent_attempts) >= self.max_failed_attempts


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Logs all requests for audit purposes.
    """

    def __init__(self, app, log_body: bool = False):
        super().__init__(app)
        self.log_body = log_body

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        # Generate request ID
        request_id = hashlib.sha256(
            f"{time.time()}{request.client.host if request.client else ''}"
            .encode()
        ).hexdigest()[:12]

        # Log request
        logger.info(
            f"[{request_id}] {request.method} {request.url.path} "
            f"- Client: {self._get_client_ip(request)}"
        )

        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Log response
        logger.info(
            f"[{request_id}] Completed {response.status_code} "
            f"in {duration:.3f}s"
        )

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response

    def _get_client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"


def setup_security_middleware(app):
    """
    Sets up all security middleware for the application.
    """
    # Order matters - outermost middleware runs first
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(IPBlocklistMiddleware)
    app.add_middleware(RequestValidationMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=60,
        burst_size=20,
    )
