from flask import Flask, request, jsonify, send_file
import os
from werkzeug.utils import secure_filename
from file_processor import get_sorted_files, load_and_store_data
from plotter import plot

app = Flask(__name__)

@app.route('/upload-directory', methods=['POST'])
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
            file.save(filename)  # Save temporarily to process
            file_paths.append(filename)

        sorted_file_paths = get_sorted_files(file_paths)
        explist, exptitles = load_and_store_data(sorted_file_paths)

        img_bytes = plot(explist, exptitles)
        return send_file(img_bytes, mimetype='image/png')

    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return jsonify({'error': str(e)}), 500

    finally:
        for filepath in file_paths:
            if os.path.exists(filepath):
                os.remove(filepath)

if __name__ == '__main__':
    app.run(port=7654, debug=True)
