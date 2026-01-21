"""
API Key Management Service

Handles API key generation, validation, and management for B2B API access.
"""

import secrets
import hashlib
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class APIKeyScope(Enum):
    """API key permission scopes."""
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    VIDEOS_CREATE = "videos:create"
    VIDEOS_READ = "videos:read"
    PROJECTS_CREATE = "projects:create"
    PROJECTS_READ = "projects:read"
    TEMPLATES_READ = "templates:read"
    PRODUCTS_READ = "products:read"


class APIKeyStatus(Enum):
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"


@dataclass
class APIKey:
    id: str
    user_id: str
    name: str
    key_prefix: str  # First 8 chars for identification
    key_hash: str    # SHA-256 hash of full key
    scopes: List[APIKeyScope]
    status: APIKeyStatus
    created_at: datetime
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    usage_count: int
    rate_limit: int  # Requests per minute
    metadata: Optional[Dict[str, Any]]


@dataclass
class APIKeyCreateResult:
    api_key: APIKey
    full_key: str  # Only returned once at creation


class APIKeyService:
    """Service for managing API keys."""

    KEY_PREFIX = "saiad"
    KEY_LENGTH = 32

    def __init__(self, db_session=None):
        self.db = db_session

    def generate_api_key(
        self,
        user_id: str,
        name: str,
        scopes: Optional[List[str]] = None,
        expires_in_days: Optional[int] = None,
        rate_limit: int = 60,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> APIKeyCreateResult:
        """
        Generate a new API key.

        Args:
            user_id: User ID who owns the key
            name: Descriptive name for the key
            scopes: List of permission scopes
            expires_in_days: Days until expiration (None for no expiry)
            rate_limit: Requests per minute limit
            metadata: Additional metadata

        Returns:
            APIKeyCreateResult with the API key (full key only shown once)
        """
        # Generate random key
        random_part = secrets.token_urlsafe(self.KEY_LENGTH)
        full_key = f"{self.KEY_PREFIX}_{random_part}"

        # Create hash for storage
        key_hash = self._hash_key(full_key)
        key_prefix = full_key[:12]

        # Parse scopes
        parsed_scopes = []
        if scopes:
            for scope in scopes:
                try:
                    parsed_scopes.append(APIKeyScope(scope))
                except ValueError:
                    logger.warning(f"Invalid scope: {scope}")
        else:
            # Default scopes for read-only access
            parsed_scopes = [
                APIKeyScope.READ,
                APIKeyScope.VIDEOS_READ,
                APIKeyScope.PROJECTS_READ,
                APIKeyScope.TEMPLATES_READ,
                APIKeyScope.PRODUCTS_READ,
            ]

        # Calculate expiration
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

        # Create API key object
        api_key = APIKey(
            id=secrets.token_urlsafe(16),
            user_id=user_id,
            name=name,
            key_prefix=key_prefix,
            key_hash=key_hash,
            scopes=parsed_scopes,
            status=APIKeyStatus.ACTIVE,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            last_used_at=None,
            usage_count=0,
            rate_limit=rate_limit,
            metadata=metadata,
        )

        # In production, save to database
        # await self.db.add(api_key_model)
        # await self.db.commit()

        return APIKeyCreateResult(
            api_key=api_key,
            full_key=full_key,
        )

    def _hash_key(self, key: str) -> str:
        """Create SHA-256 hash of API key."""
        return hashlib.sha256(key.encode()).hexdigest()

    def validate_api_key(
        self,
        key: str,
        required_scopes: Optional[List[str]] = None,
    ) -> Optional[APIKey]:
        """
        Validate an API key.

        Args:
            key: Full API key to validate
            required_scopes: Scopes required for the operation

        Returns:
            APIKey if valid, None otherwise
        """
        if not key or not key.startswith(f"{self.KEY_PREFIX}_"):
            return None

        key_hash = self._hash_key(key)

        # In production, query database by hash
        # api_key = await self.db.query(APIKeyModel).filter_by(key_hash=key_hash).first()

        # For now, return None (would be actual lookup)
        return None

    def check_scopes(
        self,
        api_key: APIKey,
        required_scopes: List[str],
    ) -> bool:
        """Check if API key has required scopes."""
        # Admin scope grants all permissions
        if APIKeyScope.ADMIN in api_key.scopes:
            return True

        # Write scope includes read
        if APIKeyScope.WRITE in api_key.scopes:
            api_key_scopes = set(api_key.scopes)
            api_key_scopes.add(APIKeyScope.READ)
        else:
            api_key_scopes = set(api_key.scopes)

        required = set()
        for scope in required_scopes:
            try:
                required.add(APIKeyScope(scope))
            except ValueError:
                return False

        return required.issubset(api_key_scopes)

    def revoke_api_key(self, key_id: str, user_id: str) -> bool:
        """Revoke an API key."""
        # In production, update database
        # api_key = await self.db.query(APIKeyModel).filter_by(
        #     id=key_id, user_id=user_id
        # ).first()
        # if api_key:
        #     api_key.status = APIKeyStatus.REVOKED
        #     await self.db.commit()
        #     return True
        return False

    def list_api_keys(self, user_id: str) -> List[APIKey]:
        """List all API keys for a user."""
        # In production, query database
        return []

    def record_usage(self, api_key: APIKey) -> None:
        """Record API key usage."""
        # In production, update last_used_at and increment usage_count
        pass

    def check_rate_limit(self, api_key: APIKey) -> bool:
        """Check if API key is within rate limit."""
        # In production, check Redis for request count
        # key = f"ratelimit:{api_key.id}"
        # count = redis.incr(key)
        # if count == 1:
        #     redis.expire(key, 60)
        # return count <= api_key.rate_limit
        return True


# Default scopes for different API access levels
DEFAULT_SCOPES = {
    "basic": [
        "read",
        "videos:read",
        "projects:read",
        "templates:read",
        "products:read",
    ],
    "standard": [
        "read",
        "write",
        "videos:create",
        "videos:read",
        "projects:create",
        "projects:read",
        "templates:read",
        "products:read",
    ],
    "full": [
        "read",
        "write",
        "admin",
        "videos:create",
        "videos:read",
        "projects:create",
        "projects:read",
        "templates:read",
        "products:read",
    ],
}


def get_scope_description(scope: str) -> str:
    """Get human-readable description for a scope."""
    descriptions = {
        "read": "Read-only access to resources",
        "write": "Create and modify resources",
        "admin": "Full administrative access",
        "videos:create": "Create new videos",
        "videos:read": "View video information",
        "projects:create": "Create new projects",
        "projects:read": "View project information",
        "templates:read": "View available templates",
        "products:read": "View product catalog",
    }
    return descriptions.get(scope, scope)
