from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.utils.auth_utils import verify_password, hash_password, create_access_token, get_current_user
from app.schemas.user import UserCreate, UserResponse, TokenResponse
from app.config import settings
import httpx
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=201, tags=["auth"])
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user with email and password.
    
    - **email**: Valid email address (must be unique)
    - **password**: Password (min 8 characters recommended)
    - **full_name**: Optional display name
    """
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hash_password(user_data.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info(f"New user registered: {user.email}")
    return user

@router.post("/login", response_model=TokenResponse, tags=["auth"])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT token.
    
    Uses OAuth2 password flow - send username (email) and password in form data.
    Returns access token for use in subsequent API calls.
    """
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password or ""):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive")
    token = create_access_token({"sub": str(user.id)})
    logger.info(f"User logged in: {user.email}")
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse, tags=["auth"])
def get_me(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user's profile.
    
    Requires valid JWT token in Authorization header.
    """
    return current_user

@router.post("/google/callback", tags=["auth"])
async def google_oauth_callback(
    code: str,
    db: Session = Depends(get_db)
):
    """
    Exchange Google OAuth code for tokens.
    
    Frontend sends the authorization code received from Google OAuth flow.
    Google OAuth setup: https://developers.google.com/identity/protocols/oauth2/web-server
    Required scopes: openid, email, profile, https://www.googleapis.com/auth/youtube.readonly
    """
    async with httpx.AsyncClient() as client:
        try:
            token_resp = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": f"{settings.FRONTEND_URL}/auth/callback",
                    "grant_type": "authorization_code"
                }
            )
            tokens = token_resp.json()
            if "error" in tokens:
                logger.error(f"Google OAuth error: {tokens.get('error_description', tokens['error'])}")
                raise HTTPException(status_code=400, detail=tokens.get("error_description", tokens["error"]))

            access_token = tokens["access_token"]
            refresh_token = tokens.get("refresh_token")
        except httpx.HTTPError as e:
            logger.error(f"Google token exchange failed: {e}")
            raise HTTPException(status_code=500, detail="Failed to exchange OAuth code")

    # Get user info from Google
    async with httpx.AsyncClient() as client:
        try:
            user_info = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            profile = user_info.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to get Google user info: {e}")
            raise HTTPException(status_code=500, detail="Failed to get user profile from Google")

    user = db.query(User).filter(User.email == profile["email"]).first()
    if not user:
        user = User(
            email=profile["email"],
            full_name=profile.get("name"),
            avatar_url=profile.get("picture"),
            google_access_token=access_token,
            google_refresh_token=refresh_token
        )
        db.add(user)
        logger.info(f"New user registered via Google OAuth: {user.email}")
    else:
        user.google_access_token = access_token
        if refresh_token:
            user.google_refresh_token = refresh_token
        logger.info(f"User updated Google tokens: {user.email}")

    db.commit()
    db.refresh(user)
    jwt_token = create_access_token({"sub": str(user.id)})
    return {"access_token": jwt_token, "token_type": "bearer", "user": user}

@router.put("/plan", response_model=UserResponse, tags=["auth"])
def update_user_plan(
    plan_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update the subscription plan of the current user.
    """
    new_plan = plan_data.get("plan")
    if new_plan not in ["free", "starter", "pro", "agency"]:
        raise HTTPException(status_code=400, detail="Invalid plan name")
    
    current_user.plan = new_plan
    db.commit()
    db.refresh(current_user)
    logger.info(f"User {current_user.email} updated plan to {new_plan}")
    return current_user


@router.get("/usage", tags=["auth"])
def get_usage(current_user: User = Depends(get_current_user)):
    """
    Return current token usage and budget status for the authenticated user.
    Used by the frontend usage bar in settings / sidebar.
    """
    from app.services.token_budget import TokenBudgetManager
    plan = current_user.plan or "free"
    return TokenBudgetManager.get_usage(str(current_user.id), plan)
