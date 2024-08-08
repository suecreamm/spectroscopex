from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import logging
import traceback
import base64
from file_processor import get_sorted_files, load_and_store_data
from plotter import shift_and_preview, create_plot
from profile_analyzer import generate_profile_data
from transformer import *

main_bp = Blueprint('main', __name__)

@main_bp.route('/upload-directory', methods=['POST'])
def upload_directory():
    if 'filePaths' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    files = request.files.getlist('filePaths')
    if len(files) == 0:
        return jsonify({'error': 'No files selected'}), 400

    file_paths = []
    try:
        for file in files:
            filename = secure_filename(file.filename)
            file.save(filename)
            file_paths.append(filename)

        sorted_file_paths = get_sorted_files(file_paths)
        explist, exptitles = load_and_store_data(sorted_file_paths)

        gauss_peak_x_mean, gauss_peak_y_mean, explist_shifted_gauss, img_bytes = shift_and_preview(explist, exptitles, plot=True)
        
        img_base64 = base64.b64encode(img_bytes.getvalue()).decode('utf-8')
        
        x_profile_data = generate_profile_data(explist_shifted_gauss, exptitles, profile_axis='x')
        y_profile_data = generate_profile_data(explist_shifted_gauss, exptitles, profile_axis='y')
        
        # Base64 encode profile images
        x_profile_data['image'] = base64.b64encode(x_profile_data['image'].getvalue()).decode('utf-8')
        y_profile_data['image'] = base64.b64encode(y_profile_data['image'].getvalue()).decode('utf-8')
        
        response_data = {
            'image': f'data:image/png;base64,{img_base64}',
            'profiles': {
                'x_profile': x_profile_data,
                'y_profile': y_profile_data
            },
            'gauss_peak_x_mean': gauss_peak_x_mean,
            'gauss_peak_y_mean': gauss_peak_y_mean
        }
        
        return jsonify(response_data)

    except Exception as e:
        logging.error(f"Error in upload_directory: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'error': f'Server error: {str(e)}', 'traceback': traceback.format_exc()}), 500

    finally:
        for filepath in file_paths:
            if os.path.exists(filepath):
                os.remove(filepath)

@main_bp.route('/get-profile', methods=['POST'])
def get_profile():
    data = request.json
    profile_axis = data['profile_axis']
    method = data.get('method', 'mean')
    
    files = request.files.getlist('filePaths')
    file_paths = [secure_filename(file.filename) for file in files if file and allowed_file(file.filename)]
    sorted_file_paths = get_sorted_files(file_paths)
    explist, exptitles = load_and_store_data(sorted_file_paths)
    
    profile_data = generate_profile_data(explist, exptitles, 
                                         profile_axis=profile_axis, 
                                         method=method)
    
    return jsonify(profile_data)

@main_bp.route('/apply-transformation', methods=['POST'])
def apply_transformation():
    data = request.json
    transformation = data['transformation']

    files = request.files.getlist('filePaths')
    file_paths = [secure_filename(file.filename) for file in files if file and allowed_file(file.filename)]
    sorted_file_paths = get_sorted_files(file_paths)
    explist, exptitles = load_and_store_data(sorted_file_paths)

    if transformation == 'flip_ud':
        transformed_df = flip_ud(explist)
    elif transformation == 'flip_lr':
        transformed_df = flip_lr(explist)
    elif transformation == 'rotate_90':
        transformed_df = rotate_90(explist)
    else:
        return jsonify({'error': 'Invalid transformation'}), 400

    img_bytes = create_plot([transformed_df], exptitles)
    img_base64 = base64.b64encode(img_bytes.getvalue()).decode('utf-8')

    response_data = {
        'image': f'data:image/png;base64,{img_base64}'
    }

    return jsonify(response_data)