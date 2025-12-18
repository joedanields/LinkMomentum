import os
import tempfile
from app.db import init_db, SessionLocal, Event, Image
from app.tasks import process_event_images_task


def setup_test_db(tmp_path, monkeypatch):
    db_file = tmp_path / "test_db.sqlite"
    os.environ["DATABASE_URL"] = f"sqlite:///{db_file}"
    # re-import init_db from app.db uses env var
    init_db()


def test_process_event_images_task(monkeypatch, tmp_path):
    # prepare DB
    setup_test_db(tmp_path, monkeypatch)
    db = SessionLocal()

    event = Event(name='Test Event', total_uploaded=1, processing_status='pending')
    db.add(event)
    db.commit()
    db.refresh(event)

    # create dummy image file
    img_path = tmp_path / 'img1.jpg'
    img_path.write_bytes(b'fakejpeg')

    img = Image(event_id=event.id, filename='img1.jpg', filepath=str(img_path))
    db.add(img)
    db.commit()
    db.refresh(img)

    # mock ImageProcessor.batch_process
    def fake_batch(paths):
        return {
            'all_results': [{
                'path': str(img_path),
                'filename': 'img1.jpg',
                'quality_score': 0.9,
                'sharpness_score': 0.8,
                'brightness_score': 0.7,
                'contrast_score': 0.6,
                'is_blur': False,
                'is_duplicate': False,
            }],
            'selected_images': [{'filename': 'img1.jpg'}],
        }

    monkeypatch.setattr('app.image_processor.ImageProcessor.batch_process', lambda self, paths: fake_batch(paths))

    # call task
    res = process_event_images_task(event.id, [{'path': str(img_path)}])

    db.refresh(img)
    db.refresh(event)

    assert event.processing_status == 'completed'
    assert img.quality_score == 0.9
    assert 'success' in res

    db.close()
