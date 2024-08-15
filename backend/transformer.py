import numpy as np
import pandas as pd
from plotter import create_plot, plot_data_with_q_conversion
import os
from flask import url_for
import uuid
from utils import save_image 
import logging


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
