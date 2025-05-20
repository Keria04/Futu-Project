import base64
from io import BytesIO
from PIL import Image
from celery import Celery
from model_module.calculate_embeded import calaculate_embeded

celery_app = Celery(
    'tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1'
)

@celery_app.task
def generate_embeddings_task(img_data_b64):
    img_bytes = base64.b64decode(img_data_b64)
    img = Image.open(BytesIO(img_bytes))
    embedder = calaculate_embeded()
    feat = embedder.calculate(img)
    return feat.tolist()
