from PIL import Image, ImageEnhance, ExifTags
import os


def auto_enhance(path_in, path_out, resize_to=(1200, 627)):
    """Perform mild auto-enhancements and save to out path."""
    img = Image.open(path_in)
    # Auto-orient using EXIF
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = img._getexif()
        if exif is not None:
            orient = exif.get(orientation)
            if orient == 3:
                img = img.rotate(180, expand=True)
            elif orient == 6:
                img = img.rotate(270, expand=True)
            elif orient == 8:
                img = img.rotate(90, expand=True)
    except Exception:
        pass


    # Mild auto-contrast/brightness
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.08)
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(1.05)


    # Resize while keeping aspect ratio, then pad/crop center to exact size
    img.thumbnail((resize_to[0], int(resize_to[1]*2)), Image.LANCZOS)
    # center crop
    w, h = img.size
    left = max(0, (w - resize_to[0]) // 2)
    top = max(0, (h - resize_to[1]) // 2)
    img = img.crop((left, top, left + resize_to[0], top + resize_to[1]))


    img.save(path_out, quality=90)
    return path_out