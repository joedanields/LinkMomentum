This backend is a FastAPI app that implements endpoints for uploading images, running
an AI-based selection/enhancement pipeline, storing audit logs, and (stub) integration
with LinkedIn for posting.


High-level files:
- main.py - FastAPI routes and app startup
- quality_assessment.py - scoring & blur detection
- duplicates.py - perceptual hashing & duplicate removal
- enhancer.py - simple enhancement helpers
- linkedin_client.py - LinkedIn OAuth + posting helpers (stubs)
- database.py - SQLAlchemy models for audit logs
- utils.py - small helpers


To run locally:
1. Create virtualenv and install requirements.
2. Set environment variables in a .env file (see .env.example in repo).
3. Start: `uvicorn backend.main:app --reload --port 8000`


Note: LinkedIn integration requires you to register an app at https://www.linkedin.com/developers/
and provide CLIENT_ID, CLIENT_SECRET, and REDIRECT_URI.