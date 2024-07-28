import os
import re
import pandas as pd

def get_sorted_files(file_paths):
    sorted_files = sorted(file_paths, key=extract_number_from_filename)
    return sorted_files

def extract_number_from_filename(filename):
    matches = re.findall(r'\d+', filename)
    return int(matches[0]) if matches else float('inf')

def load_and_store_data(file_paths, add_str='', add_str2=' K'):
    explist = []  # 로컬 변수로 선언
    exptitles = []  # 로컬 변수로 선언

    for path in file_paths:
        if path.endswith('.csv'):
            df = pd.read_csv(path, index_col=0)
            
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
