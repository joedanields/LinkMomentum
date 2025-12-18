# AI-Driven LinkedIn Event Content Generation

An intelligent web application that automatically curates, enhances, and posts event photos to LinkedIn, saving professionals hours of manual work.

## Problem Statement

Professionals spend 2-3 hours per event manually selecting, editing, and posting photos to LinkedIn. This application automates the entire process using AI-powered quality assessment, resulting in consistent, professional content sharing.

## Key Features

- **AI Quality Assessment**: Automatically evaluates images based on sharpness, composition, and lighting
- **Duplicate & Blur Removal**: Filters out low-quality and redundant images
- **Smart Selection**: Curates the top 10 shareable images from your event photos
- **Manual Override Controls**: Review and adjust AI selections before posting
- **LinkedIn Integration**: Direct posting to your personal LinkedIn profile
- **Audit Logging**: Tracks all activities for accountability

## Quick Start

### Prerequisites

- Python 3.9 or higher
- LinkedIn Developer Account (for API access)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/mourishantony/AI-Driven-LinkedIn-Event-Content-Generation.git
cd AI-Driven-LinkedIn-Event-Content-Generation
```

2. Create a virtual environment:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
copy .env.example .env
# Edit .env with your LinkedIn API credentials
```

### LinkedIn API Setup

1. Go to [LinkedIn Developers](https://www.linkedin.com/developers/apps)
2. Click **"Create app"**
3. Fill in your application details:
   - App name: "Event Photo Curator"
   - LinkedIn Page: Select or create a page
   - App logo: Upload a logo (optional)
4. In the **"Auth"** tab:
   - Add Redirect URL: `http://localhost:8000/auth/linkedin/callback`
5. In the **"Products"** tab:
   # AI-Driven LinkedIn Event Content Generation

   This repository contains an application that automates selection, processing, and
   posting of event photographs to LinkedIn. The service applies objective image
   quality metrics and configurable filters to produce a consistent set of
   publishable assets, and integrates with LinkedIn via OAuth for authenticated
   posting.

   Table of contents
   - Project overview
   - Features
   - Architecture and tech stack
   - Quickstart (local and Docker)
   - Configuration
   - API reference
   - Logging, testing, and troubleshooting
   - Contributing and license

   Project overview
   ----------------
   The application is intended to accelerate event photo workflows by:
   - Removing low-quality images (e.g., blurred or corrupted files)
   - Identifying and de-duplicating similar images
   - Scoring and ranking images using deterministic and AI-assisted metrics
   - Exposing a lightweight UI and API for review and publishing

   Key features
   ------------
   - Image quality assessment (sharpness, exposure, contrast, composition)
   - Duplicate detection using perceptual hashing
   - Configurable selection thresholds and output limits
   - Manual review and override for final selection
   - LinkedIn OAuth 2.0 integration for posting
   - Audit logging for traceability

   Architecture and technology stack
   ---------------------------------
   - Backend: FastAPI (Python)
   - Image processing: OpenCV, Pillow, scikit-image
   - Database: SQLite with SQLAlchemy (default, can be swapped)
   - Task queue: Celery (optional; see `celery_app.py`)
   - Frontend: static HTML/CSS and vanilla JavaScript served from `templates/` and `static/`

   Quickstart
   ----------
   Prerequisites: Python 3.9+ and access to a LinkedIn developer application.

   Local development

   1. Clone the repository and change to the project directory:

   ```powershell
   git clone https://github.com/mourishantony/AI-Driven-LinkedIn-Event-Content-Generation.git
   cd AI-Driven-LinkedIn-Event-Content-Generation
   ```

   2. Create and activate a virtual environment:

   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   ```

   3. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

   4. Copy the environment template and update credentials:

   ```powershell
   copy .env.example .env
   # Edit .env to add LinkedIn client ID/secret and any tuning parameters
   ```

   5. Run the application:

   ```powershell
   python main.py
   ```

   6. Open the service at `http://localhost:8000`.

   Docker (production-like)

   1. Ensure Docker and docker-compose are installed.
   2. Build and start the stack:

   ```powershell
   docker-compose up --build -d
   ```

   Configuration
   -------------
   Configuration is provided through environment variables. Important settings include:
   - `LINKEDIN_CLIENT_ID` and `LINKEDIN_CLIENT_SECRET` — OAuth credentials
   - `QUALITY_THRESHOLD` — minimum quality score (float, default: 0.6)
   - `MAX_SELECTED_IMAGES` — maximum images selected per event (default: 10)
   - `BLUR_THRESHOLD` and `DUPLICATE_THRESHOLD` — thresholds for filters

   Refer to `.env.example` for the complete list of variables supported by the
   application.

   API reference
   -------------
   Key HTTP endpoints include:
   - `POST /upload` — Upload images for processing
   - `POST /process` — Trigger image analysis and selection
   - `GET /images` — List processed images with metadata
   - `POST /select` — Modify the current selection
   - `GET /auth/linkedin` — Start OAuth flow
   - `GET /auth/linkedin/callback` — OAuth callback handler
   - `POST /post/linkedin` — Publish selected images to LinkedIn
   - `GET /logs` — Retrieve audit logs

   Implementation details and contract definitions can be found under `app/api/`.

   Logging, testing, and troubleshooting
   -------------------------------------
   - Processing and posting actions are recorded in the local database; use
     `GET /logs` to review activity.
   - Common troubleshooting steps:
     - OAuth errors: confirm redirect URI and client credentials in LinkedIn
       developer settings.
     - Processing errors: verify image formats (JPEG/PNG) and available disk space.
   - Tests are available under `tests/`. Run them with:

   ```powershell
   pytest -q
   ```

   Contributing
   ------------
   To contribute:
   - Open an issue to discuss major changes.
   - Submit focused pull requests with unit tests where applicable.
   - Keep changes small and documented.

   License and maintainer
   ---------------------
   This project is provided for personal and internal use. For questions or
   commercial inquiries, contact the maintainer: Mourish Antony.

   Primary files and locations
   - `main.py` — application entrypoint
   - `app/` — API and application logic
   - `backend/` — supplementary backend modules
   - `requirements.txt` — dependency list

   If you would like additional documentation sections (CI/CD, detailed API
   contracts, architecture diagrams), indicate which areas to expand.
