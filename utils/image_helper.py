import base64
import io

from PIL import Image

def encode_image(image_content):
    return base64.b64encode(image_content).decode('utf-8')

def resize_image_data(base64_data, max_width):
    img_data = base64.b64decode(base64_data)
    with Image.open(io.BytesIO(img_data)) as img:
        img.thumbnail((max_width, int((img.height / img.width) * max_width)), Image.LANCZOS)
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG")
        return base64.b64encode(buffer.getvalue()).decode('utf-8')