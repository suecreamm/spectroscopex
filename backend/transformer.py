import numpy as np
import pandas as pd
from plotter import create_plot, plot_data_with_q_conversion
import os
from flask import url_for
import uuid
from utils import save_image 
import logging
from cv2 import GaussianBlur


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

def blur(df, blur_strength=3.5):
    logging.debug(f"blur 함수 실행 중. 블러 강도: {blur_strength}.")
    sigma = blur_strength
    kernel_size = int(6 * sigma + 1)
    if kernel_size % 2 == 0:
        kernel_size += 1  # kerner_size must be odd.

    image = df.values.astype(np.float32)
    blurred = GaussianBlur(image, (kernel_size, kernel_size), sigma)
    logging.debug("Gaussian blur applied.")
    blurred_df = pd.DataFrame(blurred, index=df.index, columns=df.columns)
    return blurred_df


def transform_data(explist, action):
    from transformer import flip_ud, flip_lr, rotate_90
    transformed_explist = []

    for df in explist:
        if action == 'flip_ud':
            transformed_explist.append(flip_ud(df))
        elif action == 'flip_lr':
            transformed_explist.append(flip_lr(df))
        elif action == 'rotate_ccw90':
            transformed_explist.append(rotate_90(df, 'ccw'))
        elif action == 'rotate_cw90':
            transformed_explist.append(rotate_90(df, 'cw'))
        elif action == 'blur':
            transformed_explist.append(blur(df))
        elif action == 'sharpen':
            pass
        else:
            logging.error(f"Unknown transformation action: {action}")
            raise ValueError(f"Unknown transformation action: {action}")

    return transformed_explist

