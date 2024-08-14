import numpy as np
import pandas as pd
from plotter import create_plot, plot_data_with_q_conversion
import os
from flask import url_for
import uuid
from utils import save_image 

def flip_ud(df, change_sign=True):
    flipped_df = df.iloc[::-1]
    if change_sign and pd.api.types.is_numeric_dtype(flipped_df.index):
        flipped_df.index = -flipped_df.index
    return flipped_df

def flip_lr(df, change_sign=True):
    flipped_df = df.iloc[:, ::-1]
    if change_sign and pd.api.types.is_numeric_dtype(flipped_df.columns):
        flipped_df.columns = -flipped_df.columns
    return flipped_df

def rotate_90(df, direction='ccw', change_sign=True):
    if direction == 'ccw':
        rotated_df = df.T.iloc[::-1]
    else:  # clockwise
        rotated_df = df.T.iloc[:, ::-1]
    if change_sign:
        if pd.api.types.is_numeric_dtype(rotated_df.index):
            rotated_df.index = -rotated_df.index
        if pd.api.types.is_numeric_dtype(rotated_df.columns):
            rotated_df.columns = -rotated_df.columns
    return rotated_df


def transform_data(explist, action, exptitles=None, gauss_y=None):
    transformed_explist = []
    if action == 'q_conversion':
        if exptitles is None or gauss_y is None:
            raise ValueError("exptitles and gauss_y must be provided for q_conversion")
        # q_conversion을 위한 처리
        transformed_explist, img_bytes = plot_data_with_q_conversion(explist, exptitles, gauss_y)
        return transformed_explist, img_bytes
    
    for df in explist:
        if action == 'flip_ud':
            transformed_df = flip_ud(df)
        elif action == 'flip_lr':
            transformed_df = flip_lr(df)
        elif action == 'rotate_ccw90':
            transformed_df = rotate_90(df, direction='ccw')
        elif action == 'rotate_cw90':
            transformed_df = rotate_90(df, direction='cw')
        elif action == 'reset':
            transformed_df = df  # No transformation, just return the original
        else:
            raise ValueError(f"Unknown action: {action}")
        transformed_explist.append(transformed_df)
    
    return transformed_explist


def get_transformed_plot(explist, exptitles, apply_log=True):
    img_bytes = create_plot(explist, exptitles, apply_log=apply_log)
    img_url = save_image(img_bytes.getvalue(), 'transformed_plot.png')
    return img_url
