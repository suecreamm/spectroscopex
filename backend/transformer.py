import pandas as pd
import numpy as np

def flip_ud(df, change_sign=True):
    flipped_df = df.iloc[::-1]
    if change_sign:
        if pd.api.types.is_string_dtype(flipped_df.index):
            try:
                flipped_df.index = pd.to_numeric(flipped_df.index)
            except ValueError:
                pass  # If conversion fails, leave the index unchanged
        if pd.api.types.is_numeric_dtype(flipped_df.index):
            flipped_df.index = -flipped_df.index.to_series()
    return flipped_df

def flip_lr(df, change_sign=True):
    flipped_df = df.iloc[:, ::-1]
    if change_sign:
        if pd.api.types.is_string_dtype(flipped_df.columns):
            try:
                flipped_df.columns = pd.to_numeric(flipped_df.columns)
            except ValueError:
                pass  # If conversion fails, leave the columns unchanged
        if pd.api.types.is_numeric_dtype(flipped_df.columns):
            flipped_df.columns = -flipped_df.columns
    return flipped_df


def rotate_90(df, change_sign=True):
    rotated_df = df.T.iloc[::-1]
    if change_sign:
        if pd.api.types.is_string_dtype(rotated_df.index):
            try:
                rotated_df.index = pd.to_numeric(rotated_df.index)
            except ValueError:
                pass
        if pd.api.types.is_numeric_dtype(rotated_df.index):
            rotated_df.index = -rotated_df.index.to_series()

        if pd.api.types.is_string_dtype(rotated_df.columns):
            try:
                rotated_df.columns = pd.to_numeric(rotated_df.columns)
            except ValueError:
                pass
        if pd.api.types.is_numeric_dtype(rotated_df.columns):
            rotated_df.columns = -rotated_df.columns
    return rotated_df