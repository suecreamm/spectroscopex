import os
import pandas as pd
import pickle
import uuid
import logging
import json
from io import BytesIO


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
    # 저장할 디렉토리 경로 설정
    save_dir = os.path.join(os.getcwd(), 'static', 'images')
    logging.debug(f"Save directory set to: {save_dir}")
    
    # 디렉토리가 존재하지 않으면 생성
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        logging.debug(f"Created directory: {save_dir}")

    # 저장할 파일의 전체 경로 설정
    file_path = os.path.join(save_dir, filename)
    logging.debug(f"File path set to: {file_path}")

    try:
        with open(file_path, 'wb') as f:
            # 데이터 타입 확인 및 저장
            if isinstance(image_data, BytesIO):
                logging.debug("Image data is of type BytesIO.")
                data_to_write = image_data.getvalue()
            else:
                logging.debug("Image data is of type bytes.")
                data_to_write = image_data
            
            # 실제 파일에 데이터 쓰기
            f.write(data_to_write)
            logging.info(f"Image saved to {file_path}")
            logging.debug(f"Image size: {len(data_to_write)} bytes")

    except Exception as e:
        logging.error(f"Failed to save image: {str(e)}")
        logging.debug(f"Exception details: {traceback.format_exc()}")
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
