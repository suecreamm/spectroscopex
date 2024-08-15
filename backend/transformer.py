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


def transform_data(explist, action, exptitles=None, gauss_y=None, q_energy_loss_enabled=False, use_q_converted=False):
    logging.debug("Entering transform_data function")
    logging.debug(f"Received explist: {explist}")
    logging.debug(f"Received action: {action}")
    logging.debug(f"Received exptitles: {exptitles}")
    logging.debug(f"Q-Energy Loss Enabled: {q_energy_loss_enabled}")
    logging.debug(f"Use Q-Converted: {use_q_converted}")

    if explist is None or exptitles is None:
        raise ValueError("explist and exptitles must not be None in transform_data")

    transformed_explist = explist
    img_bytes = None

    if q_energy_loss_enabled and use_q_converted:
        logging.debug("Performing q_conversion")
        # q_conversion을 한 번만 수행
        transformed_explist, img_bytes = plot_data_with_q_conversion(explist, exptitles, gauss_y)
    else:
        logging.debug("Skipping q_conversion and directly creating plot")
        # 변환된 데이터 사용
        transformed_explist = explist

    # q-converted 데이터에 대해 추가 액션 수행
    if action in ['flip_ud', 'flip_lr', 'rotate_ccw90', 'rotate_cw90']:
        new_transformed_explist = []
        for df in transformed_explist:
            if action == 'flip_ud':
                transformed_df = flip_ud(df)
            elif action == 'flip_lr':
                transformed_df = flip_lr(df)
            elif action == 'rotate_ccw90':
                transformed_df = rotate_90(df, direction='ccw')
            elif action == 'rotate_cw90':
                transformed_df = rotate_90(df, direction='cw')
            new_transformed_explist.append(transformed_df)
        transformed_explist = new_transformed_explist
    elif action == 'reset':
        transformed_explist = explist
    else:
        raise ValueError(f"Unknown action: {action}")

    logging.debug(f"Final transformed explist: {transformed_explist}")

    if not img_bytes:
        # q_conversion을 한 번 수행했거나 q_energy_loss_enabled가 False인 경우, create_plot으로 그림
        logging.debug("Generating plot with create_plot")
        img_bytes = create_plot(transformed_explist, exptitles, apply_log=True)

    # 디버깅 메시지 추가
    if img_bytes:
        logging.debug(f"Generated image bytes: {len(img_bytes.getvalue())} bytes")
    else:
        logging.error("Failed to generate image bytes, img_bytes is None or empty")

    return transformed_explist, img_bytes


def get_transformed_plot(explist, exptitles, apply_log=True):
    if explist is None or exptitles is None:
        raise ValueError("explist or exptitles is None in get_transformed_plot")
    
    img_bytes = create_plot(explist, exptitles, apply_log=apply_log)
    
    with open('transformed_plot.png', 'wb') as f:
        f.write(img_bytes.getvalue())
    
    img_url = 'transformed_plot.png'
    return img_bytes
