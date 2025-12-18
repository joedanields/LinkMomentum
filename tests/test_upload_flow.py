import os
import io
import tempfile
from fastapi.testclient import TestClient


def test_upload_endpoint(monkeypatch, tmp_path):
    # set test DB and upload dir
    db_file = tmp_path / 'test_db2.sqlite'
    os.environ['DATABASE_URL'] = f"sqlite:///{db_file}"
    os.environ['UPLOAD_DIR'] = str(tmp_path / 'uploads')

    # import app after env set
    from main import app
    from app.db import init_db

    init_db()
    client = TestClient(app)

    # create fake image
    data = {
        'files': (io.BytesIO(b'fakejpeg'), 'photo.jpg')
    }

    # monkeypatch batch_process to avoid heavy CPU
    monkeypatch.setattr('app.image_processor.ImageProcessor.batch_process', lambda self, paths: {'all_results': [], 'selected_images': [], 'summary': {'total': 0, 'high_quality': 0, 'blurry': 0, 'duplicates': 0, 'selected': 0}})

    response = client.post('/api/upload', files={'files': ('photo.jpg', io.BytesIO(b'fakejpeg'), 'image/jpeg')})
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
