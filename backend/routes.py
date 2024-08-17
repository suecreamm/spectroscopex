import os
import logging
import traceback
import logging
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

main_bp = Blueprint('main', __name__)


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
            logging.error("파일이 요청에 포함되지 않음")
            return jsonify({"error": "파일이 요청에 포함되지 않음"}), 400
        
        # 파일을 읽고 처리
        files = request.files.getlist('filePaths')
        file_paths = []
        for file in files:
            filename = secure_filename(file.filename)
            save_path = save_file_to_directory(file, SAVED_DATA_DIR, filename)
            file_paths.append(save_path)

        sorted_file_paths = get_sorted_files(file_paths)
        explist, exptitles = load_and_store_data(sorted_file_paths)

        # Shift and preview processing
        gauss_peak_x_mean, gauss_peak_y_mean, explist_shifted_gauss, img_bytes = shift_and_preview(explist, exptitles, plot=True)
        img_url = save_image(img_bytes.getvalue(), 'output_plot.png')

        # Save explist_shifted_gauss as a file and store path in session
        explist_path = save_dataframe_to_file(explist_shifted_gauss, 'explist_shifted_gauss.pkl')
        session['explist_path'] = explist_path
        session['exptitles'] = exptitles
        session['gauss_peak_y_mean'] = gauss_peak_y_mean

        # 프로파일 생성
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
            logging.error("data.json 파일이 요청에 포함되지 않음")
            return jsonify({'error': 'data.json 파일이 요청에 포함되지 않음'}), 400

        data_file = request.files['data.json']
        logging.debug(f"Received data.json file: {data_file.filename}, size: {data_file.content_length} bytes")
        
        data_file.seek(0)  # 파일 포인터 초기화
        data = json.load(data_file)
        logging.debug(f"Loaded data from data.json: {data}")

        # explist_shifted_gauss.pkl 파일 경로를 data.json에서 가져옴
        explist_path = data.get('explist_shifted_gauss')
        exptitles = data.get('exptitles', [])
        gauss_peak_y_mean = data.get('gauss_peak_y_mean', None)

        logging.debug(f"로드된 데이터: explist_path={explist_path}, exptitles={exptitles}, gauss_peak_y_mean={gauss_peak_y_mean}")

        if not explist_path or not exptitles or gauss_peak_y_mean is None:
            logging.error("Q-Energy Loss 변환을 위한 데이터가 누락됨")
            return jsonify({'error': 'Missing data for Q-Energy Loss transformation'}), 400

        explist_data = load_dataframe_from_file(explist_path)

        if explist_data is None:
            logging.error(f"파일 {explist_path}을 로드하지 못함")
            return jsonify({'error': f'Failed to load explist data from {explist_path}'}), 500

        q_plot_bytes, transformed_explist = plot_data_with_q_conversion(explist_data, exptitles, gauss_peak_y_mean)
        q_plot_url = save_image(q_plot_bytes.getvalue(), 'q_output_plot.png')

        transformed_explist_path = save_dataframe_to_file(transformed_explist, 'explist_q_converted.pkl')
        session['explist_path'] = transformed_explist_path

        response_data = {
            'success': True,
            'q_plot': q_plot_url,
            'explist_q_converted': transformed_explist_path,
            'exptitles': exptitles
        }

        return jsonify(response_data)

    except Exception as e:
        logging.error(f"q_energy_loss에서 오류 발생: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'error': f'Server error: {str(e)}', 'traceback': traceback.format_exc()}), 500


@main_bp.route('/transform', methods=['POST'])
def transform():
    try:
        if 'data.json' not in request.files:
            logging.error("data.json 파일이 요청에 포함되지 않음")
            return jsonify({'error': 'data.json 파일이 요청에 포함되지 않음'}), 400

        data_file = request.files['data.json']
        logging.debug(f"Received data.json file: {data_file.filename}, size: {data_file.content_length} bytes")
        
        data_file.seek(0)  # 파일 포인터 초기화
        data = json.load(data_file)
        logging.debug(f"Loaded data from data.json: {data}")

        explist_path = data.get('explist')
        action = data.get('action')

        if not explist_path or not action:
            logging.error("Transformation을 위한 필수 데이터가 누락됨")
            return jsonify({'error': 'Missing data for transformation'}), 400

        logging.debug(f"로드된 데이터: explist_path={explist_path}, action={action}")

        # explist를 파일에서 로드
        explist_data = load_dataframe_from_file(explist_path)
        if explist_data is None:
            logging.error(f"파일 {explist_path}을 로드하지 못함")
            return jsonify({'error': f'Failed to load explist data from {explist_path}'}), 500

        logging.debug(f"로드된 Explist 데이터: {explist_data}")

        transformed_explist = transform_data(explist_data, action)
        
        img_bytes, _ = plot_data_with_q_conversion(transformed_explist, data.get('exptitles', []), apply_log=False, q_conversion=False)
        plot_image_url = save_image(img_bytes.getvalue(), 'transformed_plot.png')

        transformed_explist_path = save_dataframe_to_file(transformed_explist, 'transformed_explist.pkl')
        session['explist_path'] = transformed_explist_path

        return jsonify({'success': True, 'image': plot_image_url, 'explist_path': transformed_explist_path})

    except Exception as e:
        logging.error(f"Error in transform: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'error': f'Server error: {str(e)}', 'traceback': traceback.format_exc()}), 500


@main_bp.route('/export-csv', methods=['POST'])
def export_csv():
    try:
        data = request.json
        explist_path = data.get('explist')
        exptitles = data.get('exptitles', [])

        if not explist_path or not exptitles:
            return jsonify({'error': 'Missing explist or exptitles'}), 400

        # Load the explist data
        explist = load_dataframe_from_file(explist_path)
        if explist is None:
            return jsonify({'error': f'Failed to load explist data from {explist_path}'}), 500

        # Prepare CSV data from the explist
        csv_data = explist.to_csv(index=False)

        # Send the CSV file as a response
        response = make_response(csv_data)
        response.headers['Content-Disposition'] = 'attachment; filename=exported_data.csv'
        response.headers['Content-Type'] = 'text/csv'
        
        return response

    except Exception as e:
        logging.error(f"Error in export_csv: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'error': f'Server error: {str(e)}', 'traceback': traceback.format_exc()}), 500

