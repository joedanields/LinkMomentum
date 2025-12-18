from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from typing import Optional
from app.db import SessionLocal, LinkedInToken
from app.linkedin_api import LinkedInAPI
from app.security import encrypt_text, decrypt_text
from datetime import datetime

router = APIRouter()
api = LinkedInAPI()


@router.get('/auth/linkedin')
def linkedin_auth():
    auth_url = api.get_authorization_url(state=None)
    return {"auth_url": auth_url}


@router.get('/auth/linkedin/callback')
def linkedin_callback(code: str, state: Optional[str] = None):
    db = SessionLocal()
    try:
        token_data = api.exchange_code_for_token(code)
        user_info = api.get_user_info(token_data['access_token'])

        existing = db.query(LinkedInToken).filter(LinkedInToken.user_email == user_info.get('email')).first()
        encrypted = encrypt_text(token_data['access_token'])

        if existing:
            existing.access_token = encrypted
            existing.expires_at = token_data['expires_at']
            existing.refresh_token = token_data.get('refresh_token')
        else:
            ln = LinkedInToken(user_email=user_info.get('email'), access_token=encrypted, refresh_token=token_data.get('refresh_token'), expires_at=token_data['expires_at'])
            db.add(ln)

        db.commit()
        return RedirectResponse(url='/?auth=success')
    except Exception as e:
        return RedirectResponse(url='/?auth=error')
    finally:
        db.close()


@router.get('/auth/status')
def auth_status():
    db = SessionLocal()
    try:
        token = db.query(LinkedInToken).order_by(LinkedInToken.created_at.desc()).first()
        if not token:
            return {"authenticated": False}

        # decrypt
        from app.security import decrypt_text
        access_token = decrypt_text(token.access_token)

        is_valid = False
        if access_token:
            is_valid = api.validate_token(access_token)
        # attempt refresh if expired and refresh token present
        if not is_valid and token.refresh_token:
            try:
                new = api.refresh_token(token.refresh_token)
                token.access_token = encrypt_text(new['access_token'])
                token.expires_at = new['expires_at']
                token.refresh_token = new.get('refresh_token', token.refresh_token)
                db.add(token)
                db.commit()
                is_valid = True
            except Exception:
                is_valid = False

        return {"authenticated": is_valid, "user_email": token.user_email if is_valid else None, "expires_at": token.expires_at.isoformat() if token.expires_at else None}
    finally:
        db.close()
