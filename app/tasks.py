from app.celery_app import celery
from app.db import SessionLocal, Event, Image
from app.image_processor import ImageProcessor
from datetime import datetime
import os


def _process_event_images(event_id: int, saved_files: list):
    db = SessionLocal()
    event = None
    try:
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            return {'error': 'event not found'}

        event.processing_status = 'processing'
        db.add(event)
        db.commit()

        processor = ImageProcessor()
        paths = [f['path'] for f in saved_files]
        results = processor.batch_process(paths)

        for res in results.get('all_results', []):
            img = db.query(Image).filter(Image.filepath == res.get('path')).first()
            if not img:
                continue
            img.quality_score = res.get('quality_score', 0)
            img.sharpness_score = res.get('sharpness_score', 0)
            img.brightness_score = res.get('brightness_score', 0)
            img.contrast_score = res.get('contrast_score', 0)
            img.is_blur = bool(res.get('is_blur', False))
            img.is_duplicate = bool(res.get('is_duplicate', False))
            db.add(img)

        event.total_selected = len(results.get('selected_images', []))
        event.processing_status = 'completed'
        event.processed_at = datetime.utcnow()
        db.add(event)
        db.commit()

        return {'success': True}

    except Exception as e:
        if event:
            event.processing_status = 'failed'
            db.add(event)
            db.commit()
        return {'error': str(e)}
    finally:
        db.close()


# Expose a callable task function. If Celery is configured, wrap it with retries and acks_late.
def _task_wrapper(event_id: int, saved_files: list):
    return _process_event_images(event_id, saved_files)


if celery:
    # bind=True to allow retries, autoretry on exceptions
    @celery.task(bind=True, name='app.tasks.process_event_images', autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 10}, acks_late=True)
    def process_event_images_task(self, event_id: int, saved_files: list):
        return _task_wrapper(event_id, saved_files)
else:
    # Fallback synchronous callable
    def process_event_images_task(event_id: int, saved_files: list):
        return _task_wrapper(event_id, saved_files)
