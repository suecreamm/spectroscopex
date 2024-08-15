import yaml
import os
import uuid
from flask import url_for
import logging


def load_config():
    with open('config.yaml', 'r') as config_file:
        return yaml.safe_load(config_file)
    

def save_image(image_data, filename):
    save_dir = os.path.join(os.getcwd(), 'static', 'images')
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        logging.debug(f"Created directory: {save_dir}")

    file_path = os.path.join(save_dir, filename)
    
    with open(file_path, 'wb') as f:
        f.write(image_data)
        logging.debug(f"Image saved to {file_path}")

    return f'/static/images/{filename}'

