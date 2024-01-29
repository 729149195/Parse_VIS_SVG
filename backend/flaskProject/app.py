import time
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO
import os
import json
from modules.CreateGM import SVGParser
from modules.TestGM_bbox import SVGDrawer
from flask import send_file, make_response
from modules.Community_Detection import CommunityDetector


app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")  # 允许跨域
UPLOAD_FOLDER = './uploads'
OUTPUT_FOLDER = './GMoutput'
OUTPUT_FILE = 'GMinfo.json'

@app.route('/upload', methods=['POST'])
def upload_svg():
    svg_file = request.files.get('file')
    if svg_file:
        filename = svg_file.filename
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        svg_file.save(save_path)
        return jsonify({'result': f'File {filename} uploaded successfully'})
    else:
        return jsonify({'error': 'No SVG file received'}), 400


@app.route('/remove', methods=['POST'])
def remove_file():
    data = request.json
    filename = data.get('filename')
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify({'result': 'File removed successfully'})
    else:
        return jsonify({'error': 'File not found'}), 404


@app.route('/evaluate', methods=['POST'])
def evaluate_svg():
    data = request.json
    filename = data.get('filename')
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        # 使用 SVGParser 处理文件
        svg_parser = SVGParser(file_path)
        svg_parser.run()
        SVGDrawer("./GMoutput/GMinfo.json").run()
        detector = CommunityDetector("./GMoutput/GMinfo.json")
        detector.execute()
        # 读取输出文件
        output_path = os.path.join(OUTPUT_FOLDER, OUTPUT_FILE)
        if os.path.exists(output_path):
            with open(output_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                return jsonify(data)
        else:
            return jsonify({'error': 'Result file not found'}), 404
    else:
        return jsonify({'error': 'File not found'}), 404


@app.route('/community_data')
def data():
    directory = os.path.join(app.root_path, 'data')  # 文件夹路径
    return send_from_directory(directory, 'community_data.json')


if __name__ == '__main__':
    app.run(debug=True, port=8000)
