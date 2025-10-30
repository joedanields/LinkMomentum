from PIL import Image
import imagehash


def compute_hash(pil_img):
    return imagehash.average_hash(pil_img)


def find_duplicates(image_paths, threshold=5):
    """Return a list of unique image paths, eliminating near-duplicates."""
    hashes = {}
    unique = []
    for p in image_paths:
        try:
            img = Image.open(p)
            h = compute_hash(img)
        except Exception:
            continue
        found_dup = False
        for prev_h, prev_path in list(hashes.items()):
            if h - prev_h <= threshold:
                found_dup = True
                break
        if not found_dup:
            hashes[h] = p
            unique.append(p)
    return unique