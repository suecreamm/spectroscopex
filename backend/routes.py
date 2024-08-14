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

@main_bp.route('/upload-directory', methods=['POST'])
def upload_directory():
    if 'filePaths' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    files = request.files.getlist('filePaths')
    if len(files) == 0:
        return jsonify({'error': 'No files selected'}), 400

    try:
        file_paths = []
        for file in files:
            filename = secure_filename(file.filename)
            save_path = save_file_to_directory(file, os.getcwd(), filename)
            file_paths.append(save_path)

        sorted_file_paths = get_sorted_files(file_paths)
        explist, exptitles = load_and_store_data(sorted_file_paths)

        gauss_peak_x_mean, gauss_peak_y_mean, explist_shifted_gauss, img_bytes = shift_and_preview(explist, exptitles, plot=True)
        img_url = save_image(img_bytes.getvalue(), 'output_plot.png')

        response_data = {
            'image': img_url,
            'gauss_peak_x_mean': gauss_peak_x_mean,
            'gauss_peak_y_mean': gauss_peak_y_mean,
            'filePaths': file_paths,
            'explist_shifted_gauss': [df.to_dict(orient='list') for df in explist_shifted_gauss],
            'exptitles': exptitles
        }

        if request.form.get('q_energyloss') == 'true':
            q_plot_bytes, explist_q_converted = plot_data_with_q_conversion(explist_shifted_gauss, exptitles, gauss_peak_y_mean)
            q_plot_url = save_image(q_plot_bytes.getvalue(), 'q_output_plot.png')
            response_data['q_plot'] = q_plot_url
            response_data['explist_q_converted'] = [df.to_dict(orient='list') for df in explist_q_converted]
        else:
            response_data['q_plot'] = None

        x_profile_data = generate_profile_data(explist_shifted_gauss, exptitles, profile_axis='x')
        y_profile_data = generate_profile_data(explist_shifted_gauss, exptitles, profile_axis='y')
        
        x_profile_url = save_image(x_profile_data['image'].getvalue(), 'x_profile_plot.png')
        y_profile_url = save_image(y_profile_data['image'].getvalue(), 'y_profile_plot.png')

        response_data['profiles'] = {
            'x_profile': {'image': x_profile_url},
            'y_profile': {'image': y_profile_url}
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
        explist = [pd.DataFrame(df) for df in request.json['explist']]  # JSON으로부터 DataFrame을 재생성
        exptitles = request.json['exptitles']
        gauss_y = request.json['gauss_peak_y_mean']

        if action == 'reset':
            transformed_explist = explist
            plot_image_bytes = get_transformed_plot(transformed_explist, exptitles)
        elif action == 'q_conversion':
            plot_image_bytes, transformed_explist = plot_data_with_q_conversion(explist, exptitles, gauss_y)
        else:
            transformed_explist = transform_data(explist, action)
            plot_image_bytes = get_transformed_plot(transformed_explist, exptitles)

        plot_image_url = save_image(plot_image_bytes.getvalue(), 'transformed_plot.png')

        return jsonify({'success': True, 'image': plot_image_url})

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
        print(f"Received file paths: {file_paths}")

        explist = [pd.DataFrame(df) for df in data['explist']]
        exptitles = data['exptitles']

        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            print(f"Created directory: {save_dir}")

        file_urls = []
        for i, df in enumerate(explist):
            sanitized_title = exptitles[i].replace(" ", "")
            save_path = os.path.join(save_dir, f"processed_{sanitized_title}.csv")
            df.to_csv(save_path)
            file_urls.append(f"/downloads/{os.path.basename(save_path)}")
            print(f"Saved processed data to: {save_path}")

        return jsonify({'file_urls': file_urls})

    except Exception as e:
        logging.error(f"Error in download_shifted_data: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'error': f'Server error: {str(e)}', 'traceback': traceback.format_exc()}), 500
