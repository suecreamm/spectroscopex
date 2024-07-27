from flask import Blueprint, request, jsonify
import pandas as pd

main = Blueprint('main', __name__)

@main.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and allowed_file(file.filename):
        df = pd.read_csv(file)
        # 데이터 처리 로직 추가
        result = process_data(df)
        return jsonify(result), 200

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['csv']

def process_data(df):
    # CSV 데이터 처리 로직 추가
    return {"message": "Data processed"}

