import os
import re
import pandas as pd
import numpy as np

def get_sorted_files(file_paths):
    sorted_files = sorted(file_paths, key=extract_number_from_filename)
    return sorted_files

def extract_number_from_filename(filename):
    matches = re.findall(r'\d+', filename)
    return int(matches[0]) if matches else float('inf')

def ensure_numeric_index_and_columns(df, multiply_small_means=True):
    def convert_to_numeric(value):
        try:
            return float(value)
        except ValueError:
            return np.nan
    
    df.index = pd.to_numeric([convert_to_numeric(val) for val in df.index], errors='coerce')
    df.columns = pd.to_numeric([convert_to_numeric(val) for val in df.columns], errors='coerce')
    df = df.dropna(axis=0, how='any').dropna(axis=1, how='any')
    
    """
    if multiply_small_means:
        for column in df.columns:
            column_mean = df[column].mean()
            if column_mean:
                df[column] *= 1e8
        #print(f"Column {column} multiplied by 1e10. New mean: {df[column].mean()}")
    """    
    return df

def load_and_store_data(file_paths, add_str='', add_str2=' K', multiply_small_means=True):
    explist = []
    exptitles = []

    for path in file_paths:
        print(f"Attempting to load file: {path}")  # 디버깅 메시지

        if not os.path.exists(path):
            print(f"Error: The file {path} does not exist.")  # 디버깅 메시지
            continue

        if path.endswith('.csv'):
            try:
                df = pd.read_csv(path, index_col=0)
                print(f"Successfully loaded file: {path}")  # 디버깅 메시지
                df = ensure_numeric_index_and_columns(df, multiply_small_means)
            except Exception as e:
                print(f"Error reading {path}: {e}")  # 디버깅 메시지
                continue
            
            filename = os.path.basename(path)[:-4]
            number_part = re.findall(r'\d+', filename)
            if number_part:
                filename = number_part[0]
            else:
                filename = 'K0000'
            
            variable_name = add_str + filename + add_str2
            explist.append(df)
            exptitles.append(variable_name)
    
    return explist, exptitles

def save_dataframe_to_file(df, filename, directory='dataframes'):
    """
    :param df: 저장할 데이터프레임
    :param filename: 저장할 파일 이름
    :param directory: 파일이 저장될 디렉토리, 기본값은 'dataframes'
    :return: 파일의 전체 경로
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    filepath = os.path.join(directory, filename)
    df.to_csv(filepath)
    return filepath

def load_dataframe_from_file(filepath):
    """
    :param filepath: 로드할 파일의 경로
    :return: 로드된 데이터프레임
    """
    return pd.read_csv(filepath, index_col=0)