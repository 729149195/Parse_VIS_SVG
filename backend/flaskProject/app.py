import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
import os
import json
from werkzeug.utils import secure_filename
from modules.CreateGM import SVGParser
import threading


app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")  # 允许跨域
UPLOAD_FOLDER = './uploads'
OUTPUT_FOLDER = './GMoutput'
OUTPUT_FILE = 'GMinfo.json'


def process_file(file_path):
    svg_parser = SVGParser(file_path)
    # 假设有一种方式来获取处理的进度
    for i in range(100):
        time.sleep(0.1)  # 模拟处理进度
        progress = i + 1
        socketio.emit('progress', {'progress': progress})  # 向客户端发送进度


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


if __name__ == '__main__':
    app.run(debug=True)
