from fastapi import APIRouter, HTTPException
from app.db import SessionLocal, Image, Event
import os
from app.core import UPLOAD_DIR

router = APIRouter()


@router.get('/events/{event_id}/images')
def get_event_images(event_id: int):
    db = SessionLocal()
    try:
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail='Event not found')

        images = db.query(Image).filter(Image.event_id == event_id).all()

        return {
            'event_id': event_id,
            'event_name': event.name,
            'total_images': len(images),
            'total_selected': event.total_selected,
            'images': [
                {
                    'id': img.id,
                    'filename': img.filename,
                    'url': f"/uploads/{os.path.relpath(img.filepath, UPLOAD_DIR).replace(os.sep, '/').lstrip('./')}",
                    'quality_score': img.quality_score,
                    'is_blur': img.is_blur,
                    'is_duplicate': img.is_duplicate,
                    'is_selected': img.is_selected,
                    'is_posted': img.is_posted
                }
                for img in images
            ]
        }
    finally:
        db.close()


@router.post('/images/{image_id}/toggle-select')
def toggle_image_selection(image_id: int):
    db = SessionLocal()
    try:
        image = db.query(Image).filter(Image.id == image_id).first()
        if not image:
            raise HTTPException(status_code=404, detail='Image not found')

        image.is_selected = not image.is_selected

        event = db.query(Event).filter(Event.id == image.event_id).first()
        event.total_selected = db.query(Image).filter(Image.event_id == image.event_id, Image.is_selected == True).count()
        db.add(image)
        db.add(event)
        db.commit()

        return {"success": True, "image_id": image_id, "is_selected": image.is_selected, "total_selected": event.total_selected}
    finally:
        db.close()
