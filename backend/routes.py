from flask import Blueprint, request, jsonify, send_file, session
from utils import save_image
import os
import logging
from plotter import shift_and_preview, plot_data_with_q_conversion, plot_x_profiles, plot_y_profiles
from werkzeug.utils import secure_filename
from file_processor import get_sorted_files, load_and_store_data, save_dataframe_to_file, load_dataframe_from_file
import uuid
import traceback
import matplotlib.pyplot as plt
from io import BytesIO

main_bp = Blueprint('main', __name__)

def save_file_to_directory(file, directory, filename):
    """
    파일을 지정된 디렉토리에 저장합니다.
    
    :param file: 저장할 파일 객체
    :param directory: 파일을 저장할 디렉토리 경로
    :param filename: 저장할 파일의 이름
    :return: 파일의 전체 경로
    """
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
    try:
        if 'filePaths' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        files = request.files.getlist('filePaths')
        if len(files) == 0:
            return jsonify({'error': 'No files selected'}), 400

        file_paths = []
        for file in files:
            filename = secure_filename(file.filename)
            save_path = os.path.join(os.getcwd(), filename)
            file.save(save_path)
            file_paths.append(save_path)

        sorted_file_paths = get_sorted_files(file_paths)
        explist, exptitles = load_and_store_data(sorted_file_paths)

        gauss_peak_x_mean, gauss_peak_y_mean, explist_shifted_gauss, img_bytes = shift_and_preview(explist, exptitles, plot=True)
        img_url = save_image(img_bytes.getvalue(), 'output_plot.png')

        # Generate X-profile
        x_profile_img = BytesIO()
        plot_x_profiles(explist_shifted_gauss, exptitles, plot=True)
        plt.savefig(x_profile_img, format='png')
        x_profile_img.seek(0)
        x_profile_url = save_image(x_profile_img.getvalue(), 'x_profile_plot.png')
        plt.close()

        # Generate Y-profile
        y_profile_img = BytesIO()
        plot_y_profiles(explist_shifted_gauss, exptitles, plot=True)
        plt.savefig(y_profile_img, format='png')
        y_profile_img.seek(0)
        y_profile_url = save_image(y_profile_img.getvalue(), 'y_profile_plot.png')
        plt.close()

        response_data = {
            'image': img_url,
            'x_profile': {'image': x_profile_url},
            'y_profile': {'image': y_profile_url},
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

        return jsonify(response_data)

    except Exception as e:
        logging.error(f"Error in upload_directory: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'error': f'Server error: {str(e)}', 'traceback': traceback.format_exc()}), 500

    if 'filePaths' not in request.files:
        logging.error('No file part in the request')
        return jsonify({'error': 'No file part'}), 400
    
    files = request.files.getlist('filePaths')
    if len(files) == 0:
        logging.error('No files selected for upload')
        return jsonify({'error': 'No files selected'}), 400

    try:
        file_paths = []
        for file in files:
            filename = secure_filename(file.filename)
            save_path = save_file_to_directory(file, os.getcwd(), filename)
            file_paths.append(save_path)

        sorted_file_paths = get_sorted_files(file_paths)
        explist, exptitles = load_and_store_data(sorted_file_paths)

        explist_filenames = []
        for df in explist:
            filename = f"{uuid.uuid4()}.csv"
            filepath = save_dataframe_to_file(df, filename)
            explist_filenames.append(filepath)

        session['explist_filenames'] = explist_filenames
        session['exptitles'] = exptitles

        logging.debug(f"Session explist_filenames: {session.get('explist_filenames')}")
        logging.debug(f"Session exptitles: {session.get('exptitles')}")

        gauss_peak_x_mean, gauss_peak_y_mean, explist_shifted_gauss, img_bytes = shift_and_preview(explist, exptitles, plot=True)
        img_url = save_image(img_bytes.getvalue(), 'output_plot.png')

        x_profile_data = generate_profile_data(explist_shifted_gauss, exptitles, profile_axis='x')
        y_profile_data = generate_profile_data(explist_shifted_gauss, exptitles, profile_axis='y')
        
        x_profile_url = save_image(x_profile_data['image'].getvalue(), 'x_profile_plot.png')
        y_profile_url = save_image(y_profile_data['image'].getvalue(), 'y_profile_plot.png')

        response_data = {
            'image': img_url,
            'gauss_peak_x_mean': gauss_peak_x_mean,
            'gauss_peak_y_mean': gauss_peak_y_mean,
            'filePaths': file_paths,
            'explist_shifted_gauss': [df.to_dict(orient='list') for df in explist_shifted_gauss],
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
        return jsonify({'error': 'Server error occurred. Please try again later.'}), 500

@main_bp.route('/q-energyloss', methods=['POST'])
def q_energy_loss():
    try:
        explist_filenames = session.get('explist_filenames', [])
        exptitles = session.get('exptitles', [])
        gauss_peak_y_mean = request.json.get('gauss_peak_y_mean', [])

        if not explist_filenames or not exptitles:
            logging.error("No valid explist or exptitles provided.")
            raise ValueError("No valid explist or exptitles provided.")

        explist = [load_dataframe_from_file(filepath) for filepath in explist_filenames]

        plot_image_bytes, explist_q_converted = plot_data_with_q_conversion(explist, exptitles, gauss_peak_y_mean)
        plot_image_url = save_image(plot_image_bytes.getvalue(), 'q_output_plot.png')

        response_data = {
            'image': plot_image_url,
            'explist_q_converted': [df.to_dict(orient='list') for df in explist_q_converted]
        }

        return jsonify(response_data)

    except Exception as e:
        logging.error(f"Error in q-energy-loss: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'error': 'Server error occurred. Please try again later.'}), 500

@main_bp.route('/x-profile', methods=['POST'])
def x_profile():
    try:
        explist_filenames = session.get('explist_filenames', [])
        exptitles = session.get('exptitles', [])

        if not explist_filenames or not exptitles:
            logging.error("No valid explist or exptitles provided.")
            raise ValueError("No valid explist or exptitles provided.")

        explist = [load_dataframe_from_file(filepath) for filepath in explist_filenames]

        x_profile_img = BytesIO()
        plot_x_profiles(explist, exptitles, plot=True)
        plt.savefig(x_profile_img, format='png')
        x_profile_img.seek(0)
        x_profile_url = save_image(x_profile_img.getvalue(), 'x_profile_plot.png')
        plt.close()

        return jsonify({'success': True, 'image': x_profile_url})

    except Exception as e:
        logging.error(f"Error in x-profile: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'error': 'Server error occurred. Please try again later.'}), 500


@main_bp.route('/y-profile', methods=['POST'])
def y_profile():
    try:
        explist_filenames = session.get('explist_filenames', [])
        exptitles = session.get('exptitles', [])

        if not explist_filenames or not exptitles:
            logging.error("No valid explist or exptitles provided.")
            raise ValueError("No valid explist or exptitles provided.")

        explist = [load_dataframe_from_file(filepath) for filepath in explist_filenames]

        y_profile_img = BytesIO()
        plot_y_profiles(explist, exptitles, plot=True)
        plt.savefig(y_profile_img, format='png')
        y_profile_img.seek(0)
        y_profile_url = save_image(y_profile_img.getvalue(), 'y_profile_plot.png')
        plt.close()

        return jsonify({'success': True, 'image': y_profile_url})

    except Exception as e:
        logging.error(f"Error in y-profile: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'error': 'Server error occurred. Please try again later.'}), 500
    try:
        explist_filenames = session.get('explist_filenames', [])
        exptitles = session.get('exptitles', [])

        if not explist_filenames or not exptitles:
            logging.error("No valid explist or exptitles provided.")
            raise ValueError("No valid explist or exptitles provided.")

        # Load the DataFrames from the stored filenames
        explist = [load_dataframe_from_file(filepath) for filepath in explist_filenames]

        # Generate the Y profiles
        _, gauss_peak_y = plot_y_profiles(explist, exptitles, plot=True)

        # Save the generated plot to a file and return the file path
        plot_image = BytesIO()
        plt.savefig(plot_image, format='png')
        plot_image.seek(0)

        plot_image_url = save_image(plot_image.getvalue(), 'y_profile_plot.png')

        return jsonify({'success': True, 'image': plot_image_url})

    except Exception as e:
        logging.error(f"Error in y-profile: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'error': 'Server error occurred. Please try again later.'}), 500
    try:
        explist_filenames = session.get('explist_filenames', [])
        exptitles = session.get('exptitles', [])

        if not explist_filenames or not exptitles:
            logging.error("No valid explist or exptitles provided.")
            raise ValueError("No valid explist or exptitles provided.")

        explist = [load_dataframe_from_file(filepath) for filepath in explist_filenames]

        _, gauss_peak_y = plot_y_profiles(explist, exptitles, plot=True)
        plot_image_url = save_image(gauss_peak_y.getvalue(), 'y_profile_plot.png')

        return jsonify({'success': True, 'image': plot_image_url})

    except Exception as e:
        logging.error(f"Error in y-profile: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'error': 'Server error occurred. Please try again later.'}), 500

@main_bp.route('/download-shifted-data', methods=['POST'])
def download_shifted_data():
    try:
        save_dir = request.json['save_dir']
        explist_filenames = session.get('explist_filenames', [])
        exptitles = session.get('exptitles', [])

        if not explist_filenames or not exptitles:
            logging.error("No valid explist or exptitles provided.")
            raise ValueError("No valid explist or exptitles provided.")

        explist = [load_dataframe_from_file(filepath) for filepath in explist_filenames]

        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            logging.info(f"Created directory: {save_dir}")

        file_urls = []
        for i, df in enumerate(explist):
            sanitized_title = exptitles[i].replace(" ", "")
            save_path = os.path.join(save_dir, f"processed_{sanitized_title}.csv")
            df.to_csv(save_path)
            file_urls.append(f"/downloads/{os.path.basename(save_path)}")
            logging.info(f"Saved processed data to: {save_path}")

        return jsonify({'file_urls': file_urls})

    except Exception as e:
        logging.error(f"Error in download_shifted_data: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'error': 'Server error occurred. Please try again later.'}), 500
