from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
import httpx

from app.db import get_db
from app.models.user import User
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, verify_token

router = APIRouter()


class OAuthRequest(BaseModel):
    code: str
    redirect_uri: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int = 900
    user: dict


@router.post("/google", response_model=TokenResponse)
async def google_login(
    request: OAuthRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    # Exchange code for tokens
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": request.code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": request.redirect_uri,
                "grant_type": "authorization_code",
            },
        )

        if token_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange code for token",
            )

        tokens = token_response.json()

        # Get user info
        user_response = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )

        if user_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user info",
            )

        user_info = user_response.json()

    # Find or create user
    result = await db.execute(
        select(User).where(
            User.provider == "google",
            User.provider_id == user_info["id"],
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        # Check if email already exists
        result = await db.execute(select(User).where(User.email == user_info["email"]))
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered with different provider",
            )

        user = User(
            email=user_info["email"],
            name=user_info.get("name"),
            profile_image=user_info.get("picture"),
            provider="google",
            provider_id=user_info["id"],
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    # Create tokens
    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    # Set refresh token as HttpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return TokenResponse(
        access_token=access_token,
        user=user.to_dict(),
    )


@router.post("/kakao", response_model=TokenResponse)
async def kakao_login(
    request: OAuthRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    # Exchange code for tokens
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://kauth.kakao.com/oauth/token",
            data={
                "grant_type": "authorization_code",
                "client_id": settings.KAKAO_CLIENT_ID,
                "client_secret": settings.KAKAO_CLIENT_SECRET,
                "redirect_uri": request.redirect_uri,
                "code": request.code,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if token_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange code for token",
            )

        tokens = token_response.json()

        # Get user info
        user_response = await client.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )

        if user_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user info",
            )

        user_info = user_response.json()

    kakao_account = user_info.get("kakao_account", {})
    profile = kakao_account.get("profile", {})

    email = kakao_account.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email permission required",
        )

    # Find or create user
    result = await db.execute(
        select(User).where(
            User.provider == "kakao",
            User.provider_id == str(user_info["id"]),
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        result = await db.execute(select(User).where(User.email == email))
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered with different provider",
            )

        user = User(
            email=email,
            name=profile.get("nickname"),
            profile_image=profile.get("profile_image_url"),
            provider="kakao",
            provider_id=str(user_info["id"]),
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    # Create tokens
    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return TokenResponse(
        access_token=access_token,
        user=user.to_dict(),
    )


@router.post("/refresh")
async def refresh_token(
    request_obj: Response,
    db: AsyncSession = Depends(get_db),
):
    from fastapi import Request

    # This is a placeholder - in real implementation, get from cookie
    # refresh_token = request.cookies.get("refresh_token")
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Token refresh not implemented in this example",
    )


@router.delete("/logout")
async def logout(response: Response):
    response.delete_cookie("refresh_token")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
