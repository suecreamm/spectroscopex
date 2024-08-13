import yaml
import os
import uuid
from flask import url_for


def load_config():
    with open('config.yaml', 'r') as config_file:
        return yaml.safe_load(config_file)
    

def save_image(image_bytes, filename):
    """이미지를 static/images 디렉토리에 저장하고 URL을 반환하는 함수"""
    unique_filename = f"{uuid.uuid4()}_{filename}"
    image_path = os.path.join('static', 'images', unique_filename)
    os.makedirs(os.path.dirname(image_path), exist_ok=True)
    with open(image_path, 'wb') as img_file:
        img_file.write(image_bytes)
    return url_for('static', filename=f'images/{unique_filename}', _external=True)
