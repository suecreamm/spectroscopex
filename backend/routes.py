from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename 
import os
import logging
import traceback
import base64
from file_processor import get_sorted_files, load_and_store_data
from plotter import shift_and_preview
from profile_analyzer import generate_profile_data
from transformer import *

main_bp = Blueprint('main', __name__)

shifted_data_store = {
    'explist_shifted_gauss': None,
    'exptitles': None
}

def save_file_to_directory(file, directory, filename):
    save_dir = os.path.abspath(directory)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        print(f"Created directory: {save_dir}")  # 디버깅 메시지

    save_path = os.path.join(save_dir, filename)
    file.save(save_path)
    print(f"File saved to: {save_path}")  # 디버깅 메시지
    return save_path


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
            save_path = save_file_to_directory(file, os.getcwd(), filename)  # 절대 경로 사용
            file_paths.append(save_path)

        sorted_file_paths = get_sorted_files(file_paths)
        explist, exptitles = load_and_store_data(sorted_file_paths)

        gauss_peak_x_mean, gauss_peak_y_mean, explist_shifted_gauss, img_bytes = shift_and_preview(explist, exptitles, plot=True)

        # 전역 상태에 저장
        shifted_data_store['explist_shifted_gauss'] = explist_shifted_gauss
        shifted_data_store['exptitles'] = exptitles
        
        img_base64 = base64.b64encode(img_bytes.getvalue()).decode('utf-8')
        
        x_profile_data = generate_profile_data(explist_shifted_gauss, exptitles, profile_axis='x')
        y_profile_data = generate_profile_data(explist_shifted_gauss, exptitles, profile_axis='y')
        
        x_profile_data['image'] = base64.b64encode(x_profile_data['image'].getvalue()).decode('utf-8')
        y_profile_data['image'] = base64.b64encode(y_profile_data['image'].getvalue()).decode('utf-8')

        response_data = {
            'image': f'data:image/png;base64,{img_base64}',
            'profiles': {
                'x_profile': x_profile_data,
                'y_profile': y_profile_data
            },
            'gauss_peak_x_mean': gauss_peak_x_mean,
            'gauss_peak_y_mean': gauss_peak_y_mean,
            'filePaths': file_paths
        }
        
        return jsonify(response_data)

    except Exception as e:
        logging.error(f"Error in upload_directory: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'error': f'Server error: {str(e)}', 'traceback': traceback.format_exc()}), 500

@main_bp.route('/download-shifted-data', methods=['POST'])
def download_shifted_data():
    try:
        data = request.json
        save_dir = data['save_dir']  # 클라이언트에서 전달받은 저장 디렉토리
        file_paths = data['filePaths']
        print(f"Received file paths: {file_paths}")  # 디버깅 메시지

        # 전역 상태에서 explist_shifted_gauss와 exptitles 가져오기
        explist_shifted_gauss = shifted_data_store.get('explist_shifted_gauss')
        exptitles = shifted_data_store.get('exptitles')

        if not explist_shifted_gauss or not exptitles:
            return jsonify({'error': 'No shifted data available'}), 400
        
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            print(f"Created directory: {save_dir}")  # 디버깅 메시지

        file_urls = []
        for i, df in enumerate(explist_shifted_gauss):
            sanitized_title = exptitles[i].replace(" ", "")
            save_path = os.path.join(save_dir, f"shifted_{sanitized_title}.csv")
            df.to_csv(save_path)
            file_urls.append(f"/downloads/{os.path.basename(save_path)}")
            print(f"Saved shifted data to: {save_path}")  # 디버깅 메시지

        return jsonify({'file_urls': file_urls})

    except Exception as e:
        logging.error(f"Error in download_shifted_data: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'error': f'Server error: {str(e)}', 'traceback': traceback.format_exc()}), 500
    
