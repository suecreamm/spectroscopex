import os
import logging
import traceback
from flask import Blueprint, request, jsonify, session, send_file, make_response, abort
from werkzeug.utils import secure_filename
from file_processor import get_sorted_files, load_and_store_data
from plotter import shift_and_preview, plot_data_with_q_conversion
from profile_analyzer import generate_profile_data, plot_intensity_profiles_with_heatmap
from transformer import transform_data
import uuid
import json
import pickle
from utils import save_image, save_dataframe_to_file, load_dataframe_from_file
import pandas as pd
import base64
import matplotlib.pyplot as plt
from io import BytesIO
import zipfile

main_bp = Blueprint('main', __name__)

plt.switch_backend('Agg')

def save_file_to_directory(file, directory, filename):
    save_dir = os.path.abspath(directory)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        print(f"Created directory: {save_dir}")  # 디버깅 메시지

    save_path = os.path.join(save_dir, filename)
    file.save(save_path)
    print(f"File saved to: {save_path}")  # 디버깅 메시지
    return save_path


def save_uploaded_file(file, save_dir='uploads'):
    """Uploads the file to the server and returns the file path."""
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    file_path = os.path.join(save_dir, secure_filename(file.filename))
    file.save(file_path)
    return file_path


@main_bp.route('/upload-directory', methods=['POST'])
def upload_directory():
    SAVED_DATA_DIR = 'saved_data'
    try:
        if 'filePaths' not in request.files:
            logging.error("No files included in the request")
            return jsonify({"error": "No files included in the request"}), 400
        
        files = request.files.getlist('filePaths')

        if len(files) == 1:
            files = [files[0]]
        
        logging.debug(f"Files received: {[file.filename for file in files]}")

        file_paths = []
        for file in files:
            filename = secure_filename(file.filename)
            save_path = save_file_to_directory(file, SAVED_DATA_DIR, filename)
            file_paths.append(save_path)

        sorted_file_paths = get_sorted_files(file_paths)
        explist, exptitles = load_and_store_data(sorted_file_paths)

        # Shift and preview processing
        gauss_peak_x_mean, gauss_peak_y_mean, explist_shifted_gauss, _ = shift_and_preview(explist, exptitles, plot=False)

        # If the shifted data is invalid or empty, use the original explist
        if not explist_shifted_gauss or all(df.empty for df in explist_shifted_gauss):
            logging.warning("No valid shifted data available. Using original explist.")
            explist_shifted_gauss = explist  # Use the original data if the shifted data is not valid
            skip_transformations = True
        else:
            skip_transformations = False

        # Apply transformations to the data only if explist_shifted_gauss is valid
        if not skip_transformations:
            explist_shifted_gauss = transform_data(explist_shifted_gauss, 'flip_lr')
            explist_shifted_gauss = transform_data(explist_shifted_gauss, 'flip_ud')

        # Generate the plot
        img_bytes, _ = plot_data_with_q_conversion(explist_shifted_gauss, exptitles, gauss_peak_y_mean, q_conversion=False, apply_log=True)
        img_url = save_image(img_bytes.getvalue(), 'output_plot.png')

        # Save the transformed explist data
        explist_path = save_dataframe_to_file(explist_shifted_gauss, 'explist_shifted_gauss.pkl')
        session['explist_path'] = explist_path
        session['exptitles'] = exptitles
        session['gauss_peak_y_mean'] = gauss_peak_y_mean
        session['latest_explist'] = explist_path  # Store the latest explist path

        # Generate profile data
        x_profile_data = generate_profile_data(explist_shifted_gauss, exptitles, profile_axis='x')
        y_profile_data = generate_profile_data(explist_shifted_gauss, exptitles, profile_axis='y')

        # Save profile plots
        x_profile_url = save_image(x_profile_data['image'].getvalue(), 'x_profile_plot.png')
        y_profile_url = save_image(y_profile_data['image'].getvalue(), 'y_profile_plot.png')

        # Prepare the response data
        response_data = {
            'image': img_url,
            'gauss_peak_x_mean': gauss_peak_x_mean,
            'gauss_peak_y_mean': gauss_peak_y_mean,
            'filePaths': file_paths,
            'explist_shifted_gauss': explist_path,
            'exptitles': exptitles,
            'latest_explist': explist_path,  # Return the latest explist path
            'profiles': {
                'x_profile': {'image': x_profile_url},
                'y_profile': {'image': y_profile_url}
            }
        }
        return jsonify(response_data)

    except Exception as e:
        logging.error(f"Error in upload_directory: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'error': f'Server error: {str(e)}', 'traceback': traceback.format_exc()}), 500
    

@main_bp.route('/q-energyloss', methods=['POST'])
def q_energy_loss():
    try:
        if 'data.json' not in request.files:
            logging.error("data.json file is not included in the request")
            return jsonify({'error': 'data.json file is not included in the request'}), 400

        data_file = request.files['data.json']
        logging.debug(f"Received data.json file: {data_file.filename}, size: {data_file.content_length} bytes")
        
        data_file.seek(0)
        data = json.load(data_file)
        logging.debug(f"Loaded data from data.json: {data}")

        # Get the explist_shifted_gauss file path from data.json
        explist_path = data.get('latest_explist')
        exptitles = data.get('exptitles', [])
        gauss_peak_y_mean = data.get('gauss_peak_y_mean', None)

        logging.debug(f"Loaded data: explist_path={explist_path}, exptitles={exptitles}, gauss_peak_y_mean={gauss_peak_y_mean}")

        if not explist_path or not exptitles or gauss_peak_y_mean is None:
            logging.error("Missing data for Q-Loss Energy transformation")
            return jsonify({'error': 'Missing data for Q-Loss Energy transformation'}), 400

        explist_data = load_dataframe_from_file(explist_path)

        if explist_data is None:
            logging.error(f"Failed to load file from {explist_path}")
            return jsonify({'error': f'Failed to load explist data from {explist_path}'}), 500

        q_plot_bytes, transformed_explist = plot_data_with_q_conversion(explist_data, exptitles, gauss_peak_y_mean, q_conversion=True, apply_log=True)
        q_plot_url = save_image(q_plot_bytes.getvalue(), 'q_output_plot.png')

        transformed_explist_path = save_dataframe_to_file(transformed_explist, 'explist_q_converted.pkl')
        session['explist_path'] = transformed_explist_path
        session['latest_explist'] = transformed_explist_path  # Store the latest explist path

        response_data = {
            'success': True,
            'q_plot': q_plot_url,
            'explist_q_converted': transformed_explist_path,
            'latest_explist': transformed_explist_path,
            'exptitles': exptitles
        }

        return jsonify(response_data)

    except Exception as e:
        logging.error(f"Error in q_energy_loss: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'error': f'Server error: {str(e)}', 'traceback': traceback.format_exc()}), 500


@main_bp.route('/transform', methods=['POST'])
def transform():
    try:
        if 'data.json' not in request.files:
            logging.error("data.json file is not included in the request")
            return jsonify({'error': 'data.json file is not included in the request'}), 400
        
        logging.debug("Transform function called.")

        data_file = request.files['data.json']
        data_file.seek(0)
        data = json.load(data_file)

        explist_path = data.get('explist')  # Use latest_explist from the incoming request
        action = data.get('action')

        if not explist_path or not action:
            logging.error("Missing essential data for transformation")
            return jsonify({'error': 'Missing data for transformation'}), 400

        logging.debug(f"Loaded data: explist_path={explist_path}, action={action}")

        # Generate a unique filename using UUID
        unique_id = uuid.uuid4()
        transformed_filename = f'transformed_explist_{action}_{unique_id}.pkl'
        transformed_explist_path = os.path.join(os.path.dirname(explist_path), transformed_filename)

        # Load explist data from the original file
        explist_data = load_dataframe_from_file(explist_path)
        if explist_data is None:
            logging.error(f"Failed to load file from {explist_path}")
            return jsonify({'error': f'Failed to load explist data from {explist_path}'}), 500

        logging.debug(f"Loaded Explist data: {explist_data}")

        transformed_explist = transform_data(explist_data, action)
        
        save_dataframe_to_file(transformed_explist, transformed_explist_path)
        logging.info(f"Transformed data saved to: {transformed_explist_path}")

        img_bytes, _ = plot_data_with_q_conversion(transformed_explist, data.get('exptitles', []), apply_log=False, q_conversion=False)
        
        # Convert BytesIO image data to Base64
        img_bytes.seek(0)
        img_base64 = base64.b64encode(img_bytes.getvalue()).decode('utf-8')

        # Store the path of the transformed explist in the session
        session['explist_path'] = transformed_explist_path
        session['latest_explist'] = transformed_explist_path  # Store the latest explist path

        return jsonify({'success': True, 'image': img_base64, 'explist_path': transformed_explist_path, 'latest_explist': transformed_explist_path})

        # Update the transformed data in the store
        if is_q_energy_loss_enabled:
            data_store['explist_transformed_q'] = transformed_explist
        else:
            data_store['explist_transformed'] = transformed_explist
        
        return jsonify({
            'success': True,
            'image': transformed_plot_url
        })
    except Exception as e:
        logging.error(f"Error in transform: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'error': f'Server error: {str(e)}', 'traceback': traceback.format_exc()}), 500
    

@main_bp.route('/export-csv-files', methods=['POST'])
def export_csv_files():
    try:
        data = request.json
        explist_path = data.get('latest_explist')
        exptitles = data.get('exptitles', [])

        if not explist_path or not exptitles:
            return jsonify({'error': 'Missing explist path or exptitles in request'}), 400

        # Load the explist data from the file
        with open(explist_path, 'rb') as f:
            explist = pickle.load(f)

        if len(explist) != len(exptitles):
            return jsonify({'error': 'Explist data length does not match exptitles'}), 400

        output_dir = os.path.join('exports', 'csv_files')
        os.makedirs(output_dir, exist_ok=True)

        saved_files = []
        for i, df in enumerate(explist):
            file_name = f'{exptitles[i]}.csv'
            file_path = os.path.join(output_dir, file_name)
            df.to_csv(file_path, index=False)
            saved_files.append(file_path)

        return jsonify({'message': 'All CSV files were successfully saved.', 'files': saved_files})

    except Exception as e:
        logging.error(f"Error in export_csv_files: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'error': f'Server error: {str(e)}', 'traceback': traceback.format_exc()}), 500


@main_bp.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        directory = os.path.abspath('exports/csv_files')
        file_path = os.path.join(directory, filename)

        if not os.path.commonpath([file_path, directory]) == directory or not os.path.isfile(file_path):
            abort(404)

        return send_file(file_path, as_attachment=True)

    except Exception as e:
        logging.error(f"Error downloading file: {str(e)}")
        return jsonify({'error': f'Failed to download file: {str(e)}'}), 500


@main_bp.route('/plot_intensity_profiles', methods=['POST'])
def plot_intensity_profiles():
    data = request.json
    
    x_min = float(data.get('x_min', None))
    x_max = float(data.get('x_max', None))
    y_min = float(data.get('y_min', None))
    y_max = float(data.get('y_max', None))

    """
    img_bytes = plot_intensity_profiles_with_heatmap(
        explist, exptitles,
        value=75, window_size=5, plot='x',
        aggregation='mean',
        x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max,
        q_conversion=False, apply_log=True,
        figsize=(5, 5),
        width_ratio=(3.5, 1),
        hide_ticks=True,
    )

    return send_file(img_bytes, mimetype='image/png')
    """