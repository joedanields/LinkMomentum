from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from typing import List
import os
import shutil
import uuid
from datetime import datetime

from app.core import UPLOAD_DIR, image_processor
from app.db import SessionLocal, Event, Image
from app.celery_app import celery
from app.tasks import process_event_images_task

router = APIRouter()

MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 10 * 1024 * 1024))  # 10 MB default
ALLOWED_MIMES = {"image/jpeg", "image/png", "image/webp"}


def _save_fileobj_to(path, fileobj):
    with open(path, "wb") as buffer:
        shutil.copyfileobj(fileobj, buffer)


def process_event_images(event_id: int, saved_files: list):
    db = SessionLocal()
    try:
        # mark processing
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            return
        event.processing_status = "processing"
        db.commit()

        # run batch processor
        paths = [f["path"] for f in saved_files]
        processor = image_processor()
        results = processor.batch_process(paths)

        # update image rows
        for res in results["all_results"]:
            img = db.query(Image).filter(Image.filepath == res["path"]).first()
            if not img:
                continue
            img.quality_score = res.get("quality_score", 0)
            img.sharpness_score = res.get("sharpness_score", 0)
            img.brightness_score = res.get("brightness_score", 0)
            img.contrast_score = res.get("contrast_score", 0)
            img.is_blur = bool(res.get("is_blur", False))
            img.is_duplicate = bool(res.get("is_duplicate", False))
            # leave is_selected untouched
            db.add(img)

        # update event with totals
        event.total_selected = len(results.get("selected_images", []))
        event.processing_status = "completed"
        event.processed_at = datetime.utcnow()
        db.commit()

    except Exception as e:
        if event:
            event.processing_status = "failed"
            db.add(event)
            db.commit()
    finally:
        db.close()


@router.post("/upload")
async def upload_images(background_tasks: BackgroundTasks, files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    if len(files) > 20:
        raise HTTPException(status_code=400, detail="Maximum 20 files allowed")

    # Create event and save files
    db = SessionLocal()
    event = Event(name=f"Event {datetime.utcnow().strftime('%Y%m%d_%H%M%S')}", total_uploaded=len(files), processing_status="pending")
    db.add(event)
    db.commit()
    db.refresh(event)

    event_dir = os.path.join(UPLOAD_DIR, f"event_{event.id}")
    os.makedirs(event_dir, exist_ok=True)

    saved_files = []
    for file in files:
        if file.content_type not in ALLOWED_MIMES:
            continue

        # attempt to check size
        try:
            file.file.seek(0, os.SEEK_END)
            size = file.file.tell()
            file.file.seek(0)
        except Exception:
            size = None

        if size and size > MAX_FILE_SIZE:
            continue

        ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{ext}"
        path = os.path.join(event_dir, unique_filename)
        _save_fileobj_to(path, file.file)

        img = Image(event_id=event.id, filename=file.filename, filepath=path)
        db.add(img)
        db.flush()
        saved_files.append({"filename": file.filename, "path": path, "db_id": img.id, "unique_filename": unique_filename})

    db.commit()
    db.close()

    # schedule background processing: prefer Celery if configured
    if celery:
        # convert saved_files to serializable form (dicts already serializable)
        process_event_images_task.delay(event.id, saved_files)
    else:
        background_tasks.add_task(process_event_images, event.id, saved_files)

    return {
        "success": True,
        "event_id": event.id,
        "total_uploaded": len(saved_files),
        "processing": True
    }
