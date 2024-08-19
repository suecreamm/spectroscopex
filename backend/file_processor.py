import os
import re
import pandas as pd
import numpy as np
import uuid
import logging
import pickle


def get_sorted_files(file_paths):
    sorted_files = sorted(file_paths, key=extract_number_from_filename)
    return sorted_files

def extract_number_from_filename(filename):
    matches = re.findall(r'\d+', filename)
    return int(matches[0]) if matches else float('inf')

def ensure_numeric_index_and_columns(df):
    def convert_to_numeric(value):
        try:
            return float(value)
        except ValueError:
            return np.nan

    df.index = pd.to_numeric([convert_to_numeric(val) for val in df.index], errors='coerce')
    df.columns = pd.to_numeric([convert_to_numeric(val) for val in df.columns], errors='coerce')
    df = df.dropna(axis=0, how='any').dropna(axis=1, how='any')
    
    return df

def load_and_store_data(file_paths, add_str='', add_str2=' K'):
    explist = []
    exptitles = []

    for path in file_paths:
        if not os.path.exists(path):
            logging.error(f"파일이 존재하지 않음: {path}")
            continue

        if path.endswith('.csv'):
            try:
                df = pd.read_csv(path, index_col=0)
                logging.debug(f"{path} 파일 읽기 성공, 크기: {df.shape}")
                
                df = ensure_numeric_index_and_columns(df)
                logging.debug(f"{path} 파일 숫자형 인덱스와 컬럼으로 변환 성공")
            except Exception as e:
                logging.error(f"{path} 파일 읽기 오류: {e}")
                continue

            filename = os.path.basename(path)[:-4]  # '.csv' 확장자 제거
            number_part = re.findall(r'\d+', filename)
            if number_part:
                filename = number_part[-1]  # 파일명에서 숫자 부분 추출
            else:
                filename = '0000'  # 숫자가 없을 경우 기본값 설정

            variable_name = add_str + filename + add_str2
            explist.append(df)
            exptitles.append(variable_name)
            logging.debug(f"추가된 파일: {path}, 변수명: {variable_name}")

        elif path.endswith('.pkl'):
            try:
                with open(path, 'rb') as file:
                    df = pickle.load(file)
                logging.debug(f"{path} 파일 읽기 성공, 크기: {df.shape}")
                
                # Ensure the data is in DataFrame format and process it similarly
                if isinstance(df, pd.DataFrame):
                    df = ensure_numeric_index_and_columns(df)
                    logging.debug(f"{path} 파일 숫자형 인덱스와 컬럼으로 변환 성공")
                else:
                    logging.error(f"{path} 파일은 데이터프레임 형식이 아님")
                    continue
            except Exception as e:
                logging.error(f"{path} 파일 읽기 오류: {e}")
                continue

            filename = os.path.basename(path)[:-4]  # '.pkl' 확장자 제거
            number_part = re.findall(r'\d+', filename)
            if number_part:
                filename = number_part[-1]
            else:
                filename = '0000'

            variable_name = add_str + filename + add_str2
            explist.append(df)
            exptitles.append(variable_name)
            logging.debug(f"추가된 파일: {path}, 변수명: {variable_name}")
        
        else:
            logging.warning(f"지원되지 않는 파일 확장자: {path}")

    if not explist or not exptitles:
        logging.error("Explist 또는 exptitles이 비어 있음")
    else:
        logging.info(f"총 {len(explist)}개의 데이터프레임이 로드됨.")
    
    return explist, exptitles


def save_dataframe_to_file(df, file_path=None):
    if not file_path:
        file_path = os.path.join('data', f'{uuid.uuid4().hex}.csv')

    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    df.to_csv(file_path)
    return file_path

def load_dataframe_from_file(file_path):
    try:
        logging.debug(f"Attempting to load file from path: {file_path}")
        
        # 파일 확장자 확인
        _, file_extension = os.path.splitext(file_path)
        logging.debug(f"File extension detected: {file_extension}")

        if file_extension == '.pkl':
            logging.debug(f"Loading pkl file: {file_path}")
            # pkl 파일을 로드하여 딕셔너리 형태로 반환
            with open(file_path, 'rb') as file:
                data = pickle.load(file)
                logging.debug(f"Successfully loaded pkl file: {file_path}")
                
                # pkl 파일의 데이터 구조에 대한 추가 디버깅 정보
                if isinstance(data, dict):
                    logging.debug(f"pkl file contains a dictionary with keys: {list(data.keys())}")
                elif isinstance(data, list):
                    logging.debug(f"pkl file contains a list with length: {len(data)}")
                else:
                    logging.debug(f"pkl file contains an object of type: {type(data)}")
                
                return data

        elif file_extension == '.csv':
            logging.debug(f"Loading csv file: {file_path}")
            # csv 파일을 로드하여 데이터프레임으로 반환
            data = pd.read_csv(file_path, index_col=0)
            logging.debug(f"Successfully loaded csv file: {file_path}, shape: {data.shape}")
            return data

        else:
            logging.error(f"Unsupported file type: {file_extension}")
            return None

    except Exception as e:
        logging.error(f"Error occurred while loading file: {file_path}, Error: {str(e)}")
        return None
