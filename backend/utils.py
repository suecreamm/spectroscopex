import os
import pandas as pd
import pickle
import uuid
import logging
import json


def save_session_data(session_data, session_filename):
    session_filepath = os.path.join(os.getcwd(), session_filename)
    with open(session_filepath, 'w') as f:
        json.dump(session_data, f)
    logging.info(f"Session data saved to: {session_filepath}")

def load_session_data(session_filename):
    session_filepath = os.path.join(os.getcwd(), session_filename)
    if not os.path.exists(session_filepath):
        logging.error(f"Session file not found: {session_filepath}")
        return None

    try:
        with open(session_filepath, 'r') as f:
            session_data = json.load(f)
            logging.info(f"Session data loaded from: {session_filepath}")
            return session_data
    except Exception as e:
        logging.error(f"Error loading session file: {str(e)}")
        return None


def save_image(image_data, filename):
    save_dir = os.path.join(os.getcwd(), 'static', 'images')
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        logging.debug(f"Created directory: {save_dir}")

    file_path = os.path.join(save_dir, filename)
    
    try:
        with open(file_path, 'wb') as f:
            f.write(image_data)
            logging.info(f"Image saved to {file_path}")
    except Exception as e:
        logging.error(f"Failed to save image: {str(e)}")
        return None

    return f'/static/images/{filename}'


def save_dataframe_to_file(df_list, filename):
    save_dir = os.path.join(os.getcwd(), 'saved_data')
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        logging.info(f"Created directory: {save_dir}")

    file_path = os.path.join(save_dir, filename)
    try:
        with open(file_path, 'wb') as f:
            pickle.dump(df_list, f)
            logging.info(f"DataFrame list saved to {file_path}")
    except Exception as e:
        logging.error(f"Failed to save DataFrame list: {str(e)}")
        return None

    return file_path

def load_dataframe_from_file(file_path):
    if not os.path.exists(file_path):
        logging.error(f"File {file_path} does not exist")
        return None

    try:
        with open(file_path, 'rb') as f:
            df_list = pickle.load(f)
            logging.info(f"DataFrame list loaded from {file_path}")
            return df_list
    except Exception as e:
        logging.error(f"Failed to load DataFrame list: {str(e)}")
        return None

def generate_unique_filename(extension='csv'):
    unique_id = str(uuid.uuid4())
    filename = f"{unique_id}.{extension}"
    logging.debug(f"Generated unique filename: {filename}")

    return filename

def delete_file(file_path):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logging.info(f"File {file_path} has been deleted.")
        else:
            logging.warning(f"File {file_path} does not exist.")
    except Exception as e:
        logging.error(f"Error deleting file {file_path}: {str(e)}")
