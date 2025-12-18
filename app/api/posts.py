from fastapi import APIRouter, HTTPException
from typing import Optional
from app.db import SessionLocal, Post, Event, Image, LinkedInToken
from app.linkedin_api import LinkedInAPI
from app.security import decrypt_text

router = APIRouter()
api = LinkedInAPI()


@router.post('/post/linkedin/{event_id}')
def post_to_linkedin(event_id: int, caption: Optional[str] = None):
    db = SessionLocal()
    try:
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail='Event not found')

        selected_images = db.query(Image).filter(Image.event_id == event_id, Image.is_selected == True).all()
        if not selected_images:
            raise HTTPException(status_code=400, detail='No images selected')

        token = db.query(LinkedInToken).order_by(LinkedInToken.created_at.desc()).first()
        if not token:
            raise HTTPException(status_code=401, detail='Not authenticated with LinkedIn')

        access_token = decrypt_text(token.access_token)
        if not api.validate_token(access_token):
            raise HTTPException(status_code=401, detail='LinkedIn token invalid/expired')

        post = Post(event_id=event_id, num_images=len(selected_images), status='pending')
        db.add(post)
        db.commit()
        db.refresh(post)

        try:
            user_info = api.get_user_info(access_token)
            person_urn = f"urn:li:person:{user_info['id']}"
            image_paths = [img.filepath for img in selected_images]

            linkedin_response = api.create_image_post(access_token=access_token, person_urn=person_urn, image_paths=image_paths[:9], caption=caption or f"Event highlights from {event.name} 📸")

            post.status = 'success'
            post.linkedin_post_id = linkedin_response.get('id')
            for img in selected_images:
                img.is_posted = True
                db.add(img)

            db.add(post)
            db.commit()

            return {"success": True, "post_id": post.id, "linkedin_post_id": post.linkedin_post_id, "num_images": len(image_paths)}

        except Exception as e:
            post.status = 'failed'
            post.error_message = str(e)
            db.add(post)
            db.commit()
            raise HTTPException(status_code=500, detail=f"Failed to post to LinkedIn: {str(e)}")

    finally:
        db.close()
