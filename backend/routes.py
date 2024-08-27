import os
import logging
import traceback
from flask import Blueprint, request, jsonify, session, send_file, make_response
from werkzeug.utils import secure_filename
from file_processor import get_sorted_files, load_and_store_data
from plotter import shift_and_preview, plot_data_with_q_conversion, create_plot
from profile_analyzer import generate_profile_data
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
        print(f"Created directory: {save_dir}")

    save_path = os.path.join(save_dir, filename)
    file.save(save_path)
    print(f"File saved to: {save_path}")
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

        explist_shifted_gauss = transform_data(explist_shifted_gauss,'flip_lr')
        explist_shifted_gauss = transform_data(explist_shifted_gauss,'flip_ud')

        img_bytes, _ = plot_data_with_q_conversion(explist_shifted_gauss,exptitles, gauss_peak_y_mean, q_conversion=False, apply_log=True)
        img_url = save_image(img_bytes.getvalue(), 'output_plot.png')

        explist_path = save_dataframe_to_file(explist_shifted_gauss, 'explist_shifted_gauss.pkl')
        session['explist_path'] = explist_path
        session['exptitles'] = exptitles
        session['gauss_peak_y_mean'] = gauss_peak_y_mean
        session['latest_explist'] = explist_path  # Store the latest explist path

        x_profile_data = generate_profile_data(explist_shifted_gauss, exptitles, profile_axis='x')
        y_profile_data = generate_profile_data(explist_shifted_gauss, exptitles, profile_axis='y')

        x_profile_url = save_image(x_profile_data['image'].getvalue(), 'x_profile_plot.png')
        y_profile_url = save_image(y_profile_data['image'].getvalue(), 'y_profile_plot.png')

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
            logging.error("Missing data for Q-Energy Loss transformation")
            return jsonify({'error': 'Missing data for Q-Energy Loss transformation'}), 400

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

    except Exception as e:
        logging.error(f"Error in transform: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'error': f'Server error: {str(e)}', 'traceback': traceback.format_exc()}), 500


@main_bp.route('/export-csv-zip', methods=['POST'])
def export_csv_zip():
    try:
        data = request.json
        explist_path = data.get('explist')
        exptitles = data.get('exptitles', [])

        if not explist_path or not exptitles:
            return jsonify({'error': 'Missing explist or exptitles'}), 400

        # Load the explist data from a pickle file
        try:
            with open(explist_path, 'rb') as f:
                explist = pickle.load(f)
        except Exception as e:
            logging.error(f"Failed to load explist data from {explist_path}: {str(e)}")
            return jsonify({'error': f'Failed to load explist data from {explist_path}'}), 500

        if explist is None:
            return jsonify({'error': f'Explist data is empty or corrupted in {explist_path}'}), 500

        # Create a ZIP file in memory
        memory_file = BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as zf:
            for i, title in enumerate(exptitles):
                # Assuming 'explist' is a DataFrame or similar structure
                csv_data = explist.to_csv(index=True)
                file_name = f'exported_{title}.csv'
                zf.writestr(file_name, csv_data)
        
        memory_file.seek(0)
        return send_file(memory_file, attachment_filename='exported_data.zip', as_attachment=True)

    except Exception as e:
        logging.error(f"Error in export_csv_zip: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'error': f'Server error: {str(e)}', 'traceback': traceback.format_exc()}), 500