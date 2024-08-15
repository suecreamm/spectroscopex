import os
import re
import pandas as pd
import numpy as np
import uuid

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
            print(f"File does not exist: {path}")
            continue

        if path.endswith('.csv'):
            try:
                df = pd.read_csv(path, index_col=0)
                df = ensure_numeric_index_and_columns(df)
            except Exception as e:
                print(f"Error reading {path}: {e}")
                continue

            filename = os.path.basename(path)[:-4]  # Remove '.csv' extension
            number_part = re.findall(r'\d+', filename)
            if number_part:
                # Use the first number found in the filename
                filename = number_part[-1]
            else:
                # Provide a default number if no numbers are found
                filename = '0000'

            # Create the variable name without extra 'K'
            variable_name = add_str + filename + add_str2
            explist.append(df)
            exptitles.append(variable_name)
    
    return explist, exptitles

def save_dataframe_to_file(df, file_path=None):
    if not file_path:
        file_path = os.path.join('data', f'{uuid.uuid4().hex}.csv')

    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    df.to_csv(file_path)
    return file_path

def load_dataframe_from_file(file_path):
    return pd.read_csv(file_path, index_col=0)
