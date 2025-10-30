import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import uuid
import shutil
import os
from .utils import UPLOAD_DIR, save_upload_file_bytes
from .duplicates import find_duplicates
from .quality_assessment import score_image
from .enhancer import auto_enhance
from .linkedin_client import get_auth_url, exchange_code_for_access_token, upload_images_and_create_post
from .database import init_db, SessionLocal, create_audit_log
from dotenv import load_dotenv
import json

load_dotenv()

app = FastAPI(title="AI Photo Curator - Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

# Simple in-memory store for processed results per session (MVP)
PROCESS_STORE = {}

@app.post('/upload')
async def upload(files: list[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail='No files uploaded')
    session_id = str(uuid.uuid4())
    session_dir = UPLOAD_DIR / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    saved_paths = []
    for f in files:
        ext = Path(f.filename).suffix.lower()
        if ext not in {'.jpg', '.jpeg', '.png'}:
            continue
        dest = session_dir / f.filename
        contents = await f.read()
        save_upload_file_bytes(contents, dest)
        saved_paths.append(str(dest))
    # Create audit log with uploaded count
    db = SessionLocal()
    create_audit_log(db_session=db, user_id=None, num_photos_uploaded=len(saved_paths), num_photos_selected=0, status='uploaded')
    db.close()
    return {'session_id': session_id, 'num_uploaded': len(saved_paths)}

@app.post('/process')
async def process(session_id: str = Form(...)):
    session_dir = UPLOAD_DIR / session_id
    if not session_dir.exists():
        raise HTTPException(status_code=404, detail='Session not found')
    # list images
    imgs = sorted([str(p) for p in session_dir.iterdir() if p.suffix.lower() in ('.jpg','.jpeg','.png')])
    # remove duplicates
    unique = find_duplicates(imgs)
    scored = []
    metadata_map = {}
    for p in unique:
        score, meta = score_image(p)
        metadata_map[p] = meta
        scored.append((p, score))
    # sort desc and keep conservative top N (10)
    scored_sorted = sorted(scored, key=lambda x: x[1], reverse=True)
    top = [p for p, s in scored_sorted[:10] if s > 0.05]

    # Enhance and write to processed/ subfolder
    processed_dir = session_dir / 'processed'
    processed_dir.mkdir(exist_ok=True)
    processed_paths = []
    for i, p in enumerate(top):
        out = processed_dir / f"selected_{i+1}.jpg"
        auto_enhance(p, out)
        processed_paths.append(str(out))

    # Save to store
    PROCESS_STORE[session_id] = {
        'selected': processed_paths,
        'meta': metadata_map
    }
    # Update audit log
    db = SessionLocal()
    create_audit_log(db_session=db, user_id=None, num_photos_uploaded=len(imgs), num_photos_selected=len(processed_paths), status='processed', metadata={'selected': len(processed_paths)})
    db.close()
    return {'session_id': session_id, 'selected_count': len(processed_paths), 'selected': processed_paths}

@app.get('/results')
async def results(session_id: str):
    if session_id not in PROCESS_STORE:
        raise HTTPException(status_code=404, detail='Not processed or invalid session')
    return PROCESS_STORE[session_id]

@app.get('/download')
async def download(session_id: str, filename: str):
    session_dir = UPLOAD_DIR / session_id / 'processed'
    path = session_dir / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail='File not found')
    return FileResponse(path)

@app.post('/post_to_linkedin')
async def post_to_linkedin(session_id: str = Form(...), text: str = Form(...)):
    # For MVP we assume OAuth is handled externally; accept an access_token optionally in form
    access_token = None
    if session_id not in PROCESS_STORE:
        raise HTTPException(status_code=404, detail='Not processed or invalid session')
    images = PROCESS_STORE[session_id]['selected']
    # Call linkedin client (stub)
    result = upload_images_and_create_post(access_token, images, text)
    # Save audit log with post id
    db = SessionLocal()
    create_audit_log(db_session=db, user_id=None, num_photos_uploaded=0, num_photos_selected=len(images), linkedin_post_id=result.get('post_id'), status='posted')
    db.close()
    return {'status': 'posted', 'result': result}

# LinkedIn OAuth endpoints (basic)
@app.get('/auth/linkedin')
async def linkedin_auth():
    state = str(uuid.uuid4())
    url = get_auth_url(state)
    return JSONResponse({'auth_url': url, 'state': state})

@app.get('/auth/linkedin/callback')
async def linkedin_callback(code: str = None, state: str = None):
    if code is None:
        raise HTTPException(status_code=400, detail='Missing code')
    token = exchange_code_for_access_token(code)
    return {'token': token}

@app.get('/audit')
async def audit(limit: int = 20):
    db = SessionLocal()
    logs = db.query(__import__('backend.database', fromlist=['AuditLog']).AuditLog).order_by(__import__('sqlalchemy').desc(__import__('backend.database', fromlist=['AuditLog']).AuditLog.timestamp)).limit(limit).all()
    db.close()
    return [{'id': l.id, 'timestamp': l.timestamp.isoformat(), 'num_uploaded': l.num_photos_uploaded, 'num_selected': l.num_photos_selected, 'status': l.status, 'post_id': l.linkedin_post_id} for l in logs]

if __name__ == '__main__':
    uvicorn.run('backend.main:app', host='0.0.0.0', port=8000, reload=True)
