"""
Social Media Integration Service

Handles automatic posting to various social media platforms.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import asyncio
import logging
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class SocialPlatform(Enum):
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"


class PostStatus(Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    PROCESSING = "processing"
    PUBLISHED = "published"
    FAILED = "failed"


@dataclass
class SocialAccount:
    platform: SocialPlatform
    account_id: str
    account_name: str
    access_token: str
    refresh_token: Optional[str]
    token_expires_at: Optional[datetime]
    connected_at: datetime
    is_active: bool = True


@dataclass
class PostContent:
    title: str
    description: str
    video_url: str
    thumbnail_url: Optional[str]
    tags: List[str]
    scheduled_time: Optional[datetime] = None
    visibility: str = "public"
    custom_settings: Optional[Dict[str, Any]] = None


@dataclass
class PostResult:
    platform: SocialPlatform
    post_id: Optional[str]
    post_url: Optional[str]
    status: PostStatus
    error_message: Optional[str]
    published_at: Optional[datetime]


class SocialMediaService:
    """
    Service for managing social media integrations and auto-posting.
    """

    def __init__(self):
        self.connected_accounts: Dict[str, List[SocialAccount]] = {}

    async def connect_account(
        self,
        user_id: str,
        platform: SocialPlatform,
        auth_code: str,
        redirect_uri: str,
    ) -> Optional[SocialAccount]:
        """
        Connect a social media account using OAuth.
        """
        try:
            # Exchange auth code for tokens
            tokens = await self._exchange_auth_code(platform, auth_code, redirect_uri)

            if not tokens:
                return None

            # Get account info
            account_info = await self._get_account_info(platform, tokens["access_token"])

            account = SocialAccount(
                platform=platform,
                account_id=account_info["id"],
                account_name=account_info["name"],
                access_token=tokens["access_token"],
                refresh_token=tokens.get("refresh_token"),
                token_expires_at=tokens.get("expires_at"),
                connected_at=datetime.utcnow(),
            )

            # Store account
            if user_id not in self.connected_accounts:
                self.connected_accounts[user_id] = []
            self.connected_accounts[user_id].append(account)

            logger.info(f"Connected {platform.value} account for user {user_id}")
            return account

        except Exception as e:
            logger.error(f"Failed to connect {platform.value}: {e}")
            return None

    async def disconnect_account(
        self,
        user_id: str,
        platform: SocialPlatform,
        account_id: str,
    ) -> bool:
        """
        Disconnect a social media account.
        """
        if user_id not in self.connected_accounts:
            return False

        accounts = self.connected_accounts[user_id]
        for i, account in enumerate(accounts):
            if account.platform == platform and account.account_id == account_id:
                accounts.pop(i)
                logger.info(f"Disconnected {platform.value} account for user {user_id}")
                return True

        return False

    def get_connected_accounts(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all connected accounts for a user.
        """
        accounts = self.connected_accounts.get(user_id, [])
        return [
            {
                "platform": acc.platform.value,
                "account_id": acc.account_id,
                "account_name": acc.account_name,
                "is_active": acc.is_active,
                "connected_at": acc.connected_at.isoformat(),
            }
            for acc in accounts
        ]

    async def publish_video(
        self,
        user_id: str,
        platform: SocialPlatform,
        content: PostContent,
    ) -> PostResult:
        """
        Publish a video to a specific platform.
        """
        # Find connected account
        account = self._find_account(user_id, platform)
        if not account:
            return PostResult(
                platform=platform,
                post_id=None,
                post_url=None,
                status=PostStatus.FAILED,
                error_message="No connected account found",
                published_at=None,
            )

        # Refresh token if needed
        if account.token_expires_at and account.token_expires_at < datetime.utcnow():
            await self._refresh_token(account)

        # Platform-specific publishing
        try:
            if platform == SocialPlatform.YOUTUBE:
                result = await self._publish_to_youtube(account, content)
            elif platform == SocialPlatform.INSTAGRAM:
                result = await self._publish_to_instagram(account, content)
            elif platform == SocialPlatform.TIKTOK:
                result = await self._publish_to_tiktok(account, content)
            elif platform == SocialPlatform.FACEBOOK:
                result = await self._publish_to_facebook(account, content)
            elif platform == SocialPlatform.TWITTER:
                result = await self._publish_to_twitter(account, content)
            elif platform == SocialPlatform.LINKEDIN:
                result = await self._publish_to_linkedin(account, content)
            else:
                result = PostResult(
                    platform=platform,
                    post_id=None,
                    post_url=None,
                    status=PostStatus.FAILED,
                    error_message="Unsupported platform",
                    published_at=None,
                )

            return result

        except Exception as e:
            logger.error(f"Failed to publish to {platform.value}: {e}")
            return PostResult(
                platform=platform,
                post_id=None,
                post_url=None,
                status=PostStatus.FAILED,
                error_message=str(e),
                published_at=None,
            )

    async def publish_to_multiple(
        self,
        user_id: str,
        platforms: List[SocialPlatform],
        content: PostContent,
    ) -> Dict[str, PostResult]:
        """
        Publish a video to multiple platforms simultaneously.
        """
        tasks = [
            self.publish_video(user_id, platform, content)
            for platform in platforms
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        return {
            platform.value: result if isinstance(result, PostResult) else PostResult(
                platform=platform,
                post_id=None,
                post_url=None,
                status=PostStatus.FAILED,
                error_message=str(result),
                published_at=None,
            )
            for platform, result in zip(platforms, results)
        }

    async def schedule_post(
        self,
        user_id: str,
        platform: SocialPlatform,
        content: PostContent,
        scheduled_time: datetime,
    ) -> Dict[str, Any]:
        """
        Schedule a video post for later.
        """
        content.scheduled_time = scheduled_time

        # In production, store in database and use a scheduler
        return {
            "status": "scheduled",
            "platform": platform.value,
            "scheduled_time": scheduled_time.isoformat(),
            "content": {
                "title": content.title,
                "description": content.description[:100] + "...",
            },
        }

    async def get_post_analytics(
        self,
        user_id: str,
        platform: SocialPlatform,
        post_id: str,
    ) -> Dict[str, Any]:
        """
        Get analytics for a published post.
        """
        account = self._find_account(user_id, platform)
        if not account:
            return {"error": "No connected account found"}

        # Platform-specific analytics (mock data for demonstration)
        return {
            "post_id": post_id,
            "platform": platform.value,
            "metrics": {
                "views": 12500,
                "likes": 890,
                "comments": 45,
                "shares": 123,
                "engagement_rate": 0.075,
                "watch_time_avg": 28.5,
                "click_through_rate": 0.042,
            },
            "demographics": {
                "age_groups": {
                    "18-24": 0.35,
                    "25-34": 0.42,
                    "35-44": 0.15,
                    "45+": 0.08,
                },
                "top_countries": ["KR", "US", "JP"],
            },
            "updated_at": datetime.utcnow().isoformat(),
        }

    def _find_account(
        self,
        user_id: str,
        platform: SocialPlatform,
    ) -> Optional[SocialAccount]:
        """Find a connected account for a user and platform."""
        accounts = self.connected_accounts.get(user_id, [])
        for account in accounts:
            if account.platform == platform and account.is_active:
                return account
        return None

    async def _exchange_auth_code(
        self,
        platform: SocialPlatform,
        auth_code: str,
        redirect_uri: str,
    ) -> Optional[Dict[str, Any]]:
        """Exchange OAuth authorization code for tokens."""
        # Platform-specific token exchange
        endpoints = {
            SocialPlatform.YOUTUBE: "https://oauth2.googleapis.com/token",
            SocialPlatform.INSTAGRAM: "https://api.instagram.com/oauth/access_token",
            SocialPlatform.FACEBOOK: "https://graph.facebook.com/v18.0/oauth/access_token",
            SocialPlatform.TIKTOK: "https://open-api.tiktok.com/oauth/access_token/",
            SocialPlatform.TWITTER: "https://api.twitter.com/2/oauth2/token",
            SocialPlatform.LINKEDIN: "https://www.linkedin.com/oauth/v2/accessToken",
        }

        # Mock token response for demonstration
        return {
            "access_token": f"mock_access_token_{platform.value}",
            "refresh_token": f"mock_refresh_token_{platform.value}",
            "expires_at": datetime.utcnow(),
        }

    async def _get_account_info(
        self,
        platform: SocialPlatform,
        access_token: str,
    ) -> Dict[str, str]:
        """Get account information from platform."""
        # Mock account info
        return {
            "id": f"account_{platform.value}_123",
            "name": f"{platform.value.title()} Account",
        }

    async def _refresh_token(self, account: SocialAccount) -> bool:
        """Refresh an expired access token."""
        if not account.refresh_token:
            return False

        # Platform-specific token refresh
        # Mock refresh
        account.access_token = f"refreshed_token_{account.platform.value}"
        account.token_expires_at = datetime.utcnow()
        return True

    async def _publish_to_youtube(
        self,
        account: SocialAccount,
        content: PostContent,
    ) -> PostResult:
        """Publish video to YouTube."""
        # YouTube Data API v3 upload
        # In production: use google-api-python-client

        # Mock successful upload
        post_id = f"yt_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        return PostResult(
            platform=SocialPlatform.YOUTUBE,
            post_id=post_id,
            post_url=f"https://youtube.com/watch?v={post_id}",
            status=PostStatus.PUBLISHED,
            error_message=None,
            published_at=datetime.utcnow(),
        )

    async def _publish_to_instagram(
        self,
        account: SocialAccount,
        content: PostContent,
    ) -> PostResult:
        """Publish video to Instagram (Reels)."""
        # Instagram Graph API
        # In production: use Meta Business SDK

        post_id = f"ig_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        return PostResult(
            platform=SocialPlatform.INSTAGRAM,
            post_id=post_id,
            post_url=f"https://instagram.com/reel/{post_id}",
            status=PostStatus.PUBLISHED,
            error_message=None,
            published_at=datetime.utcnow(),
        )

    async def _publish_to_tiktok(
        self,
        account: SocialAccount,
        content: PostContent,
    ) -> PostResult:
        """Publish video to TikTok."""
        # TikTok API for Business

        post_id = f"tt_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        return PostResult(
            platform=SocialPlatform.TIKTOK,
            post_id=post_id,
            post_url=f"https://tiktok.com/@user/video/{post_id}",
            status=PostStatus.PUBLISHED,
            error_message=None,
            published_at=datetime.utcnow(),
        )

    async def _publish_to_facebook(
        self,
        account: SocialAccount,
        content: PostContent,
    ) -> PostResult:
        """Publish video to Facebook."""
        # Facebook Graph API

        post_id = f"fb_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        return PostResult(
            platform=SocialPlatform.FACEBOOK,
            post_id=post_id,
            post_url=f"https://facebook.com/watch/?v={post_id}",
            status=PostStatus.PUBLISHED,
            error_message=None,
            published_at=datetime.utcnow(),
        )

    async def _publish_to_twitter(
        self,
        account: SocialAccount,
        content: PostContent,
    ) -> PostResult:
        """Publish video to Twitter/X."""
        # Twitter API v2

        post_id = f"tw_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        return PostResult(
            platform=SocialPlatform.TWITTER,
            post_id=post_id,
            post_url=f"https://twitter.com/user/status/{post_id}",
            status=PostStatus.PUBLISHED,
            error_message=None,
            published_at=datetime.utcnow(),
        )

    async def _publish_to_linkedin(
        self,
        account: SocialAccount,
        content: PostContent,
    ) -> PostResult:
        """Publish video to LinkedIn."""
        # LinkedIn Marketing API

        post_id = f"li_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        return PostResult(
            platform=SocialPlatform.LINKEDIN,
            post_id=post_id,
            post_url=f"https://linkedin.com/posts/{post_id}",
            status=PostStatus.PUBLISHED,
            error_message=None,
            published_at=datetime.utcnow(),
        )


# Global instance
social_media_service = SocialMediaService()
