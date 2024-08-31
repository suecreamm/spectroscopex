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

    file_info = []

    for path in file_paths:
        if not os.path.exists(path):
            logging.error(f"File does not exist: {path}")
            continue

        if path.endswith('.csv'):
            try:
                df = pd.read_csv(path, index_col=0)
                logging.debug(f"Successfully read {path}, size: {df.shape}")
                
                df = ensure_numeric_index_and_columns(df)
                logging.debug(f"Converted {path} to numeric index and columns successfully")
            except Exception as e:
                logging.error(f"Error reading {path}: {e}")
                continue

            file_info.append((path, df))

        elif path.endswith('.pkl'):
            try:
                with open(path, 'rb') as file:
                    df = pickle.load(file)
                logging.debug(f"Successfully read {path}, size: {df.shape}")
                
                if isinstance(df, pd.DataFrame):
                    df = ensure_numeric_index_and_columns(df)
                    logging.debug(f"Converted {path} to numeric index and columns successfully")
                else:
                    logging.error(f"{path} is not a DataFrame format")
                    continue
            except Exception as e:
                logging.error(f"Error reading {path}: {e}")
                continue

            file_info.append((path, df))

        else:
            logging.warning(f"Unsupported file extension: {path}")

    file_info.sort(key=lambda x: x[0])

    for idx, (path, df) in enumerate(file_info):
        filename = f"{idx:04d}"
        variable_name = add_str + filename + add_str2
        explist.append(df)
        exptitles.append(variable_name)
        logging.debug(f"Added file: {path}, variable name: {variable_name}")

    if not explist or not exptitles:
        logging.error("Explist or exptitles is empty")
    else:
        logging.info(f"Loaded a total of {len(explist)} DataFrames.")
    
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
        
        _, file_extension = os.path.splitext(file_path)
        logging.debug(f"File extension detected: {file_extension}")

        if file_extension == '.pkl':
            logging.debug(f"Loading pkl file: {file_path}")

            with open(file_path, 'rb') as file:
                data = pickle.load(file)
                logging.debug(f"Successfully loaded pkl file: {file_path}")
                
                if isinstance(data, dict):
                    logging.debug(f"pkl file contains a dictionary with keys: {list(data.keys())}")
                elif isinstance(data, list):
                    logging.debug(f"pkl file contains a list with length: {len(data)}")
                else:
                    logging.debug(f"pkl file contains an object of type: {type(data)}")
                
                return data

        elif file_extension == '.csv':
            logging.debug(f"Loading csv file: {file_path}")
            
            data = pd.read_csv(file_path, index_col=0)
            logging.debug(f"Successfully loaded csv file: {file_path}, shape: {data.shape}")
            return data

        else:
            logging.error(f"Unsupported file type: {file_extension}")
            return None

    except Exception as e:
        logging.error(f"Error occurred while loading file: {file_path}, Error: {str(e)}")
        return None
