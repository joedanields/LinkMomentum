from fastapi import APIRouter
from app.db import SessionLocal, Post

router = APIRouter()


@router.get('/logs')
def get_logs():
    db = SessionLocal()
    try:
        posts = db.query(Post).order_by(Post.posted_at.desc()).limit(100).all()
        return {"posts": [{"id": p.id, "status": p.status, "event_id": p.event_id, "posted_at": p.posted_at.isoformat() if p.posted_at else None, "error": p.error_message} for p in posts]}
    finally:
        db.close()
