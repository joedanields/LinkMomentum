from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
import uuid
from datetime import datetime
from dotenv import load_dotenv

from backend.database import init_db, get_db, Event, Image, Post, LinkedInToken
from backend.image_processor import ImageProcessor
from backend.linkedin_api import LinkedInAPI

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="LinkedIn Event Photo Curator", version="1.0.0")

# Create necessary directories
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
STATIC_DIR = "static"
TEMPLATE_DIR = "templates"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "css"), exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "js"), exist_ok=True)
os.makedirs(TEMPLATE_DIR, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Templates
templates = Jinja2Templates(directory=TEMPLATE_DIR)

# Initialize services
image_processor = ImageProcessor(
    quality_threshold=float(os.getenv("QUALITY_THRESHOLD", 0.6)),
    blur_threshold=float(os.getenv("BLUR_THRESHOLD", 100)),
    duplicate_threshold=int(os.getenv("DUPLICATE_THRESHOLD", 5))
)
linkedin_api = LinkedInAPI()

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    print("\n" + "="*70)
    print("🎯 LinkedIn Event Photo Curator - AI-Powered Content Generation")
    print("="*70)
    print("\n📦 Initializing application...")
    
    init_db()
    print("   ✅ Database initialized")
    print(f"   ✅ Upload directory: {UPLOAD_DIR}")
    print("   ✅ AI engine ready")
    print("   ✅ LinkedIn API configured")
    
    print("\n" + "="*70)
    print("🚀 SERVER READY!")
    print("="*70)
    print(f"\n   🌐 Open your browser to: http://localhost:8000")
    print(f"   📖 Documentation: README.md")
    print(f"   🆘 Need help? Check SETUP_GUIDE.md")
    print("\n" + "="*70)
    print("💡 Tips:")
    print("   • Connect LinkedIn before uploading photos")
    print("   • Upload 10-15 images for best results")
    print("   • AI selects best 10 images automatically")
    print("   • Press Ctrl+C to stop the server")
    print("="*70 + "\n")


# ============= Frontend Routes =============

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve main application page"""
    return templates.TemplateResponse("index.html", {"request": request})


# ============= Upload & Processing Endpoints =============

@app.post("/api/upload")
async def upload_images(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process event images"""
    
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")
    
    if len(files) > 20:
        raise HTTPException(status_code=400, detail="Maximum 20 files allowed")
    
    # Create new event
    event = Event(
        name=f"Event {datetime.now().strftime('%Y%m%d_%H%M%S')}",
        total_uploaded=len(files)
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    
    # Create event directory
    event_dir = os.path.join(UPLOAD_DIR, f"event_{event.id}")
    os.makedirs(event_dir, exist_ok=True)
    
    # Save uploaded files
    saved_files = []
    for file in files:
        # Validate file type
        if not file.content_type.startswith("image/"):
            continue
        
        # Generate unique filename
        file_ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(event_dir, unique_filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        saved_files.append({
            "filename": file.filename,
            "unique_filename": unique_filename,
            "path": file_path
        })
    
    # Process images with AI
    image_paths = [f["path"] for f in saved_files]
    processing_results = image_processor.batch_process(image_paths)
    
    # Save image records to database
    for i, result in enumerate(processing_results["all_results"]):
        is_selected = result["filename"] in [
            img["filename"] for img in processing_results["selected_images"]
        ]
        
        image_record = Image(
            event_id=event.id,
            filename=saved_files[i]["filename"],
            filepath=result["path"],
            quality_score=result["quality_score"],
            sharpness_score=result["sharpness_score"],
            brightness_score=result["brightness_score"],
            contrast_score=result["contrast_score"],
            is_blur=result["is_blur"],
            is_duplicate=result["is_duplicate"],
            is_selected=is_selected
        )
        db.add(image_record)
    
    # Update event stats
    event.total_selected = len(processing_results["selected_images"])
    db.commit()
    
    return {
        "success": True,
        "event_id": event.id,
        "total_uploaded": len(saved_files),
        "total_selected": event.total_selected,
        "summary": processing_results["summary"],
        "images": [
            {
                "filename": result["filename"],
                "url": f"/uploads/event_{event.id}/{saved_files[i]['unique_filename']}",
                "quality_score": result["quality_score"],
                "sharpness_score": result["sharpness_score"],
                "brightness_score": result["brightness_score"],
                "contrast_score": result["contrast_score"],
                "is_blur": result["is_blur"],
                "is_duplicate": result["is_duplicate"],
                "is_selected": result["filename"] in [
                    img["filename"] for img in processing_results["selected_images"]
                ]
            }
            for i, result in enumerate(processing_results["all_results"])
        ]
    }


@app.get("/api/events/{event_id}/images")
async def get_event_images(event_id: int, db: Session = Depends(get_db)):
    """Get all images for an event"""
    
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    images = db.query(Image).filter(Image.event_id == event_id).all()
    
    return {
        "event_id": event_id,
        "event_name": event.name,
        "total_images": len(images),
        "total_selected": event.total_selected,
        "images": [
            {
                "id": img.id,
                "filename": img.filename,
                "url": f"/uploads/{img.filepath.replace(UPLOAD_DIR, '').lstrip(os.sep).replace(os.sep, '/')}",
                "quality_score": img.quality_score,
                "is_blur": img.is_blur,
                "is_duplicate": img.is_duplicate,
                "is_selected": img.is_selected,
                "is_posted": img.is_posted
            }
            for img in images
        ]
    }


@app.post("/api/images/{image_id}/toggle-select")
async def toggle_image_selection(image_id: int, db: Session = Depends(get_db)):
    """Toggle image selection status"""
    
    image = db.query(Image).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    image.is_selected = not image.is_selected
    
    # Update event selected count
    event = db.query(Event).filter(Event.id == image.event_id).first()
    event.total_selected = db.query(Image).filter(
        Image.event_id == image.event_id,
        Image.is_selected == True
    ).count()
    
    db.commit()
    
    return {
        "success": True,
        "image_id": image_id,
        "is_selected": image.is_selected,
        "total_selected": event.total_selected
    }


# ============= LinkedIn OAuth Endpoints =============

@app.get("/api/auth/linkedin")
async def linkedin_auth():
    """Initiate LinkedIn OAuth flow"""
    auth_url = linkedin_api.get_authorization_url(state=str(uuid.uuid4()))
    return {"auth_url": auth_url}


@app.get("/auth/linkedin/callback")
async def linkedin_callback(code: str, state: Optional[str] = None, db: Session = Depends(get_db)):
    """Handle LinkedIn OAuth callback"""
    
    try:
        # Exchange code for token
        token_data = linkedin_api.exchange_code_for_token(code)
        
        # Get user info
        user_info = linkedin_api.get_user_info(token_data["access_token"])
        
        # Store token in database
        existing_token = db.query(LinkedInToken).filter(
            LinkedInToken.user_email == user_info["email"]
        ).first()
        
        if existing_token:
            existing_token.access_token = token_data["access_token"]
            existing_token.expires_at = token_data["expires_at"]
        else:
            new_token = LinkedInToken(
                user_email=user_info["email"],
                access_token=token_data["access_token"],
                expires_at=token_data["expires_at"]
            )
            db.add(new_token)
        
        db.commit()
        
        # Redirect back to main app with success message
        return RedirectResponse(url="/?auth=success")
    
    except Exception as e:
        print(f"LinkedIn auth error: {e}")
        return RedirectResponse(url="/?auth=error")


@app.get("/api/auth/status")
async def auth_status(db: Session = Depends(get_db)):
    """Check if user is authenticated with LinkedIn"""
    
    token = db.query(LinkedInToken).order_by(LinkedInToken.created_at.desc()).first()
    
    if not token:
        return {"authenticated": False}
    
    # Check if token is still valid
    is_valid = linkedin_api.validate_token(token.access_token)
    
    return {
        "authenticated": is_valid,
        "user_email": token.user_email if is_valid else None,
        "expires_at": token.expires_at.isoformat() if is_valid else None
    }


# ============= LinkedIn Posting Endpoint =============

@app.post("/api/post/linkedin/{event_id}")
async def post_to_linkedin(
    event_id: int,
    caption: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Post selected images to LinkedIn"""
    
    # Get event and selected images
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    selected_images = db.query(Image).filter(
        Image.event_id == event_id,
        Image.is_selected == True
    ).all()
    
    if not selected_images:
        raise HTTPException(status_code=400, detail="No images selected")
    
    # Get LinkedIn token
    token = db.query(LinkedInToken).order_by(LinkedInToken.created_at.desc()).first()
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated with LinkedIn")
    
    # Validate token
    if not linkedin_api.validate_token(token.access_token):
        raise HTTPException(status_code=401, detail="LinkedIn token expired. Please re-authenticate.")
    
    # Create post record
    post = Post(
        event_id=event_id,
        num_images=len(selected_images),
        status="pending"
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    
    try:
        # Get user info for person URN
        user_info = linkedin_api.get_user_info(token.access_token)
        person_urn = f"urn:li:person:{user_info['id']}"
        
        # Prepare image paths
        image_paths = [img.filepath for img in selected_images]
        
        # Post to LinkedIn
        if len(image_paths) > 0:
            linkedin_response = linkedin_api.create_image_post(
                access_token=token.access_token,
                person_urn=person_urn,
                image_paths=image_paths[:9],  # LinkedIn max 9 images
                caption=caption or f"Event highlights from {event.name} 📸 #professional #networking #events"
            )
            
            # Update post record
            post.status = "success"
            post.linkedin_post_id = linkedin_response.get("id")
            
            # Mark images as posted
            for img in selected_images:
                img.is_posted = True
            
            db.commit()
            
            return {
                "success": True,
                "post_id": post.id,
                "linkedin_post_id": post.linkedin_post_id,
                "num_images": len(image_paths)
            }
    
    except Exception as e:
        post.status = "failed"
        post.error_message = str(e)
        db.commit()
        
        raise HTTPException(status_code=500, detail=f"Failed to post to LinkedIn: {str(e)}")


# ============= Audit Logs =============

@app.get("/api/logs")
async def get_logs(db: Session = Depends(get_db)):
    """Get audit logs"""
    
    posts = db.query(Post).order_by(Post.posted_at.desc()).limit(50).all()
    
    return {
        "logs": [
            {
                "id": post.id,
                "event_id": post.event_id,
                "posted_at": post.posted_at.isoformat(),
                "linkedin_post_id": post.linkedin_post_id,
                "num_images": post.num_images,
                "status": post.status,
                "error_message": post.error_message
            }
            for post in posts
        ]
    }


@app.get("/api/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get application statistics"""
    
    total_events = db.query(Event).count()
    total_images = db.query(Image).count()
    total_posts = db.query(Post).filter(Post.status == "success").count()
    total_selected = db.query(Image).filter(Image.is_selected == True).count()
    
    return {
        "total_events": total_events,
        "total_images_processed": total_images,
        "total_images_selected": total_selected,
        "total_posts": total_posts
    }


# ============= Health Check =============

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
