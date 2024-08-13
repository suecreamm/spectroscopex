import os
import logging
import traceback
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from file_processor import get_sorted_files, load_and_store_data
from plotter import shift_and_preview, plot_data_with_q_conversion
from profile_analyzer import generate_profile_data
from transformer import transform_data, get_transformed_plot
import uuid
from utils import save_image

main_bp = Blueprint('main', __name__)

data_store = {
    'explist_shifted_gauss': None,
    'exptitles': None,
    'explist_transformed': None,
    'explist_q_converted': None,  
    'explist_transformed_q': None
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
            save_path = save_file_to_directory(file, os.getcwd(), filename)
            file_paths.append(save_path)

        sorted_file_paths = get_sorted_files(file_paths)
        explist, exptitles = load_and_store_data(sorted_file_paths)

        gauss_peak_x_mean, gauss_peak_y_mean, explist_shifted_gauss, img_bytes = shift_and_preview(explist, exptitles, plot=True)

        # 전역 상태에 저장
        data_store['explist_shifted_gauss'] = explist_shifted_gauss
        data_store['exptitles'] = exptitles
        data_store['explist_transformed'] = None
        
        img_url = save_image(img_bytes.getvalue(), 'output_plot.png')

        # q-Energy Loss 체크박스가 활성화된 경우
        if request.form.get('q_energyloss') == 'true':
            q_plot_bytes, explist_q_converted = plot_data_with_q_conversion(explist_shifted_gauss, exptitles, gauss_peak_y_mean)
            q_plot_url = save_image(q_plot_bytes.getvalue(), 'q_output_plot.png')
            data_store['explist_q_converted'] = explist_q_converted
        else:
            q_plot_url = None

        x_profile_data = generate_profile_data(explist_shifted_gauss, exptitles, profile_axis='x')
        y_profile_data = generate_profile_data(explist_shifted_gauss, exptitles, profile_axis='y')
        
        x_profile_url = save_image(x_profile_data['image'].getvalue(), 'x_profile_plot.png')
        y_profile_url = save_image(y_profile_data['image'].getvalue(), 'y_profile_plot.png')

        response_data = {
            'image': img_url,
            'q_plot': q_plot_url,
            'profiles': {
                'x_profile': {'image': x_profile_url},
                'y_profile': {'image': y_profile_url}
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
        is_q_energy_loss_enabled = request.json.get('q_energy_loss_enabled', False)

        if action == 'reset':
            # 초기 상태로 되돌리기
            if is_q_energy_loss_enabled:
                explist = data_store.get('explist_q_converted', data_store['explist_shifted_gauss'])
            else:
                explist = data_store['explist_shifted_gauss']
            exptitles = data_store['exptitles']
        else:
            if is_q_energy_loss_enabled:
                explist = data_store.get('explist_transformed_q', data_store.get('explist_q_converted'))
            else:
                explist = data_store['explist_transformed'] or data_store['explist_shifted_gauss']
            exptitles = data_store['exptitles']
        
        if not explist or not exptitles:
            return jsonify({'error': 'No data available for transformation'}), 400
        
        if action != 'reset':
            transformed_explist = transform_data(explist, action)
        else:
            transformed_explist = explist  # reset의 경우 변환하지 않음
        
        transformed_plot_url = get_transformed_plot(transformed_explist, exptitles, apply_log=True)

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
