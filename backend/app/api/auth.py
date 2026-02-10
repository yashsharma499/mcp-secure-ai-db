from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.api.deps import get_db
from app.schemas.auth import (
    SignupRequest,
    LoginRequest,
    TokenResponse,
    AuthUserResponse
)
from app.db.models.user import User
from app.core.security import (
    hash_password,
    verify_password,
    hash_refresh_token,
    verify_refresh_token
)
from app.core.jwt import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    TokenError
)

router = APIRouter(tags=["auth"])


@router.post("/signup", response_model=AuthUserResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):

    try:
        email = payload.email.lower().strip()

        existing = db.query(User).filter(User.email == email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )

        user = User(
            email=email,
            password_hash=hash_password(payload.password),
            role="user"
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return AuthUserResponse(
            id=user.id,
            email=user.email,
            role=user.role
        )

    except HTTPException:
        db.rollback()
        raise

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):

    try:
        email = payload.email.lower().strip()

        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        if not verify_password(payload.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        access_token = create_access_token(
            subject=user.id,
            extra_claims={"role": user.role}
        )

        refresh_token = create_refresh_token(
            subject=user.id
        )

        user.refresh_token_hash = hash_refresh_token(refresh_token)
        db.add(user)
        db.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            id=user.id,
            email=user.email,
            role=user.role
        )

    except HTTPException:
        raise

    except TokenError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/refresh", response_model=TokenResponse)
def refresh(
    refresh_token: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):

    try:
        payload = decode_refresh_token(refresh_token)

        user_id = payload.get("sub")

        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user or not user.refresh_token_hash:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        if not verify_refresh_token(refresh_token, user.refresh_token_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        new_access_token = create_access_token(
            subject=user.id,
            extra_claims={"role": user.role}
        )

        new_refresh_token = create_refresh_token(
            subject=user.id
        )

        user.refresh_token_hash = hash_refresh_token(new_refresh_token)
        db.add(user)
        db.commit()

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            id=user.id,
            email=user.email,
            role=user.role
        )

    except HTTPException:
        raise

    except TokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh token"
        )
