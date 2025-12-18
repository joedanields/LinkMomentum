````markdown
Celery integration
==================

This project includes optional Celery support to run image processing in a worker.

Quick start (local Redis):

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Start Redis (on Windows you can use Docker):

```bash
docker run -p 6379:6379 -d redis:7
```

3. Export broker URL and start worker:

Windows (PowerShell):
```powershell
$env:CELERY_BROKER_URL = 'redis://localhost:6379/0'
celery -A app.celery_app.celery worker --loglevel=info
```

Linux/macOS:
```bash
export CELERY_BROKER_URL=redis://localhost:6379/0
celery -A app.celery_app.celery worker --loglevel=info
```

4. Start the FastAPI app (in a separate terminal).

When `CELERY_BROKER_URL` is set, uploads will enqueue `process_event_images_task` in Celery. If not set, the app falls back to FastAPI BackgroundTasks.

````
