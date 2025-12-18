import pytest

from app import core


def test_core_settings_present():
    assert hasattr(core, 'UPLOAD_DIR')
    assert hasattr(core, 'STATIC_DIR')
    assert hasattr(core, 'TEMPLATE_DIR')


def test_image_processor_factory():
    proc = core.get_image_processor()
    assert proc is not None
    # has expected method
    assert hasattr(proc, 'assess_quality')
