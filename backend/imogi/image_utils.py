"""Optimasi gambar otomatis saat upload (resize + kompres)."""
import io
import os

from django.core.files.base import ContentFile
from PIL import Image, ImageOps

MAX_SIZE = 1600       # sisi terpanjang maksimum (px)
QUALITY = 82          # kualitas JPEG
THRESHOLD = 400_000   # bytes; di bawah ini & sudah kecil -> lewati


def optimize_imagefield(fieldfile, max_size=MAX_SIZE, quality=QUALITY, threshold=THRESHOLD):
    """Ringankan file gambar pada sebuah ImageField (in-place, sebelum model.save()).

    - Resize bila lebih besar dari max_size.
    - Simpan JPEG teroptimasi; PNG dipertahankan hanya bila ada transparansi (logo).
    - Idempoten: file yang sudah kecil & pas dilewati.
    """
    if not fieldfile:
        return
    try:
        fieldfile.open()
        img = Image.open(fieldfile)
        img.load()
    except Exception:
        return

    try:
        size_bytes = fieldfile.size
    except Exception:
        size_bytes = threshold + 1

    too_big = img.width > max_size or img.height > max_size
    if not too_big and size_bytes <= threshold:
        return  # sudah ringan

    img = ImageOps.exif_transpose(img)  # hormati orientasi
    has_alpha = img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info)
    # PNG mode RGBA belum tentu benar-benar transparan (mis. render ChatGPT).
    # Bila alpha opaque penuh, perlakukan sebagai foto -> JPEG (jauh lebih ringan).
    if has_alpha:
        try:
            if img.convert("RGBA").getchannel("A").getextrema()[0] == 255:
                has_alpha = False
        except Exception:
            pass

    if img.width > max_size or img.height > max_size:
        ratio = max_size / float(max(img.width, img.height))
        img = img.resize((round(img.width * ratio), round(img.height * ratio)), Image.LANCZOS)

    buf = io.BytesIO()
    stem = os.path.splitext(os.path.basename(fieldfile.name))[0]
    if has_alpha:
        img.save(buf, "PNG", optimize=True)
        newname = stem + ".png"
    else:
        img.convert("RGB").save(buf, "JPEG", quality=quality, optimize=True, progressive=True)
        newname = stem + ".jpg"

    fieldfile.save(newname, ContentFile(buf.getvalue()), save=False)
