from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename 
import os
import logging
import traceback
import base64
from file_processor import get_sorted_files, load_and_store_data
from plotter import shift_and_preview
from profile_analyzer import generate_profile_data
from transformer import transform_data, get_transformed_plot

main_bp = Blueprint('main', __name__)

data_store = {
    'explist_shifted_gauss': None,
    'exptitles': None,
    'explist_transformed': None
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
        data_store['explist_shifted_gauss'] = explist_shifted_gauss
        data_store['exptitles'] = exptitles
        data_store['explist_transformed'] = None  # 초기화
        
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


@main_bp.route('/transform', methods=['POST'])
def transform():
    try:
        action = request.json['action']
        
        if action == 'reset':
            # 초기 상태로 되돌리기
            explist = data_store['explist_shifted_gauss']
            exptitles = data_store['exptitles']
        else:
            explist = data_store['explist_transformed'] or data_store['explist_shifted_gauss']
            exptitles = data_store['exptitles']
        
        if not explist or not exptitles:
            return jsonify({'error': 'No data available for transformation'}), 400
        
        if action != 'reset':
            transformed_explist = transform_data(explist, action)
        else:
            transformed_explist = explist  # reset의 경우 변환하지 않음
        
        transformed_plot = get_transformed_plot(transformed_explist, exptitles)
        
        # Update the transformed data in the store
        data_store['explist_transformed'] = transformed_explist
        
        return jsonify({
            'success': True,
            'image': transformed_plot
        })
    except Exception as e:
        logging.error(f"Error in transform: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'error': f'Server error: {str(e)}', 'traceback': traceback.format_exc()}), 500
    

@main_bp.route('/download-shifted-data', methods=['POST'])
def download_shifted_data():
    try:
        data = request.json
        save_dir = data['save_dir']
        file_paths = data['filePaths']
        print(f"Received file paths: {file_paths}")  # 디버깅 메시지

        explist = data_store['explist_transformed'] or data_store['explist_shifted_gauss']
        exptitles = data_store['exptitles']

        if not explist or not exptitles:
            return jsonify({'error': 'No shifted or transformed data available'}), 400
        
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            print(f"Created directory: {save_dir}")  # 디버깅 메시지

        file_urls = []
        for i, df in enumerate(explist):
            sanitized_title = exptitles[i].replace(" ", "")
            save_path = os.path.join(save_dir, f"processed_{sanitized_title}.csv")
            df.to_csv(save_path)
            file_urls.append(f"/downloads/{os.path.basename(save_path)}")
            print(f"Saved processed data to: {save_path}")  # 디버깅 메시지

        return jsonify({'file_urls': file_urls})

    except Exception as e:
        logging.error(f"Error in download_shifted_data: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'error': f'Server error: {str(e)}', 'traceback': traceback.format_exc()}), 500