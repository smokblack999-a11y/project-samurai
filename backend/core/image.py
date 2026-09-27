import base64, io
from PIL import Image, ImageOps

def image_to_data_url(raw: bytes) -> str:
    image = ImageOps.exif_transpose(Image.open(io.BytesIO(raw))).convert("RGB")
    image.thumbnail((2400, 2400))
    out = io.BytesIO()
    image.save(out, format="JPEG", quality=88, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(out.getvalue()).decode()
