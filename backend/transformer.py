import numpy as np
import pandas as pd
from plotter import create_plot, plot_data_with_q_conversion
import os
from flask import url_for
import uuid
from utils import save_image 
import logging
from cv2 import GaussianBlur, filter2D


def flip_ud(df, change_sign=True):
    logging.debug("Executing flip_ud function.")
    flipped_df = df.iloc[::-1]
    if change_sign and pd.api.types.is_numeric_dtype(flipped_df.index):
        flipped_df.index = -flipped_df.index
    logging.debug(f"flip_ud result:\n{flipped_df.head()}")
    return flipped_df

def flip_lr(df, change_sign=True):
    logging.debug("Executing flip_lr function.")
    flipped_df = df.iloc[:, ::-1]
    if change_sign and pd.api.types.is_numeric_dtype(flipped_df.columns):
        flipped_df.columns = -flipped_df.columns
    logging.debug(f"flip_lr result:\n{flipped_df.head()}")
    return flipped_df

def rotate_90(df, direction='ccw', change_sign=True):
    logging.debug(f"Executing rotate_90 function. Direction: {direction}")
    if direction == 'ccw':
        rotated_df = df.T.iloc[::-1]
    else:  # clockwise
        rotated_df = df.T.iloc[:, ::-1]
    if change_sign:
        if pd.api.types.is_numeric_dtype(rotated_df.index):
            rotated_df.index = -rotated_df.index
        if pd.api.types.is_numeric_dtype(rotated_df.columns):
            rotated_df.columns = -rotated_df.columns
    logging.debug(f"rotate_90 result:\n{rotated_df.head()}")
    return rotated_df


def blur(df, blur_strength=3.5):
    logging.debug(f"Executing blur function. Blur strength: {blur_strength}.")
    sigma = blur_strength
    kernel_size = int(6 * sigma + 1)
    if (kernel_size % 2 == 0):
        kernel_size += 1  # kernel_size must be odd.

    image = df.values.astype(np.float32)
    blurred = GaussianBlur(image, (kernel_size, kernel_size), sigma)
    logging.debug("Gaussian blur applied.")
    blurred_df = pd.DataFrame(blurred, index=df.index, columns=df.columns)
    return blurred_df

def sharpen(df, sharpen_strength=1.5):
    logging.debug(f"Executing sharpen function. Sharpen strength: {sharpen_strength}.")
    kernel = np.array([[-1, -1, -1], 
                       [-1,  9, -1], 
                       [-1, -1, -1]])
    kernel = kernel * sharpen_strength

    image = df.values.astype(np.float32)
    sharpened = filter2D(image, -1, kernel)
    logging.debug("Sharpening filter applied.")
    sharpened_df = pd.DataFrame(sharpened, index=df.index, columns=df.columns)
    return sharpened_df


def transform_data(explist, action):
    logging.debug(f"Transforming data with action: {action}")
    transformed_explist = []

    for df in explist:
        logging.debug(f"Original DataFrame:\n{df.head()}")

        if action == 'flip_ud':
            transformed_df = flip_ud(df)
        elif action == 'flip_lr':
            transformed_df = flip_lr(df)
        elif action == 'rotate_ccw90':
            transformed_df = rotate_90(df, 'ccw')
        elif action == 'rotate_cw90':
            transformed_df = rotate_90(df, 'cw')
        elif action == 'blur':
            transformed_df = blur(df)
        elif action == 'sharpen':
            transformed_df = sharpen(df)
        else:
            logging.error(f"Unknown transformation action: {action}")
            raise ValueError(f"Unknown transformation action: {action}")

        transformed_explist.append(transformed_df)
        logging.debug(f"Transformed DataFrame:\n{transformed_df.head()}")

    logging.debug(f"All transformations completed for action: {action}")
    return transformed_explist