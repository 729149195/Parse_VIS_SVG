from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO
import os
import json
from modules.CreateGM import SVGParser
from modules.Community_Detection import CommunityDetector
from modules.Add_id import add_svg_id
from modules.Convert_toHex import ColorFormatConverter
from modules.Statisticians import TagCounter, AttributeCounter, GroupCounter, FillColorCounter, StrokeColorCounter
from modules.Gestalt_Edges_Features import update_graph_with_similarity_edges
from modules.Ex_Features import SVGFeatureExtractor
from modules.Contrastive_Clustering.cluster import ClusterPredictor
from modules.Mirror_RL import FeatureVectorModifier

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
        svg_parser.run()  #解析生成初始MGinfo.json文件

        converter = ColorFormatConverter("./GMoutput/GMinfo.json")
        converter.process_file()    # 统一色值为hex
        update_graph_with_similarity_edges()  #创建并添加格式塔边
        extractor = SVGFeatureExtractor()
        extractor.process_specific_json_file()  # 对该svg进行特征向量的提取
        tag_counter = TagCounter()  #统计不同种类元素数量
        tag_counter.process()
        counter = AttributeCounter()
        counter.process()  #统计不同属性数量
        fill_counter = FillColorCounter()
        fill_counter.process_data()
        stroke_counter = StrokeColorCounter()
        stroke_counter.process_data()
        detector = CommunityDetector("./GMoutput/GMinfo.json")
        detector.execute()  # 从GMinfo.json提取可见元素并进行社区检测

        modifier = FeatureVectorModifier()
        modifier.modify_features()

        predictor = ClusterPredictor()  #利用训练好的模型对特征向量文件进行分类并输出到community_dectction.json文件中
        predictor.run()

        countergroup = GroupCounter()  # 统计group节点数量信息
        countergroup.process()

        output_path = os.path.join(OUTPUT_FOLDER, OUTPUT_FILE)  # 读取输出文件
        add_svg_id(file_path,"./GMoutput/GMinfo.json")   #为原始svg元素添加对应id
        if os.path.exists(output_path):
            with open(output_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                return jsonify(data)
        else:
            return jsonify({'error': 'Result file not found'}), 404
    else:
        return jsonify({'error': 'File not found'}), 404


@app.route('/get-svg', methods=['GET'])
def get_svg():
    # 获取前端传递的 filename 参数
    filename = request.args.get('filename')
    if not filename:
        return jsonify({'error': 'Filename is required'}), 400
    # 构造文件路径
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    # 检查文件是否存在
    if not os.path.exists(filepath) or not os.path.isfile(filepath):
        return jsonify({'error': 'File not found'}), 404
    # 返回文件内容
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route('/ele_num_data', methods=['GET'])
def histogram_ele_data():
    data_file_path = os.path.join(app.root_path, 'data', 'ele_num.json')  # 数据文件路径
    if not os.path.exists(data_file_path):
        return jsonify({'error': 'Data file not found'}), 404
    with open(data_file_path, 'r', encoding='utf-8') as data_file:
        ele_num_data = json.load(data_file)
        return jsonify(ele_num_data)


@app.route('/attr_num_data', methods=['GET'])
def histogram_attr_data():
    data_file_path = os.path.join(app.root_path, 'data', 'attr_num.json')  # 数据文件路径
    if not os.path.exists(data_file_path):
        return jsonify({'error': 'Data file not found'}), 404
    with open(data_file_path, 'r', encoding='utf-8') as data_file:
        ele_num_data = json.load(data_file)
        return jsonify(ele_num_data)


@app.route('/bbox_num_data', methods=['GET'])
def histogram_bbox_data():
    data_file_path = os.path.join(app.root_path, 'data', 'bbox_points_count.json')  # 数据文件路径
    if not os.path.exists(data_file_path):
        return jsonify({'error': 'Data file not found'}), 404
    with open(data_file_path, 'r', encoding='utf-8') as data_file:
        ele_num_data = json.load(data_file)
        return jsonify(ele_num_data)


@app.route('/group_data', methods=['GET'])
def histogram_group_data():
    data_file_path = os.path.join(app.root_path, 'data', 'group_data.json')  # 数据文件路径
    if not os.path.exists(data_file_path):
        return jsonify({'error': 'Data file not found'}), 404
    with open(data_file_path, 'r', encoding='utf-8') as data_file:
        group_num_data = json.load(data_file)
        return jsonify(group_num_data)


@app.route('/fill_num', methods=['GET'])
def fill_data():
    data_file_path = os.path.join(app.root_path, 'data', 'fill_num.json')  # 数据文件路径
    if not os.path.exists(data_file_path):
        return jsonify({'error': 'Data file not found'}), 404
    with open(data_file_path, 'r', encoding='utf-8') as data_file:
        fill_num_data = json.load(data_file)
        return jsonify(fill_num_data)


@app.route('/stroke_num', methods=['GET'])
def stroke_data():
    data_file_path = os.path.join(app.root_path, 'data', 'stroke_num.json')  # 数据文件路径
    if not os.path.exists(data_file_path):
        return jsonify({'error': 'Data file not found'}), 404
    with open(data_file_path, 'r', encoding='utf-8') as data_file:
        stroke_num_data = json.load(data_file)
        return jsonify(stroke_num_data)


@app.route('/community_data')
def data():
    directory = os.path.join(app.root_path, 'data')  # 文件夹路径
    return send_from_directory(directory, 'community_data.json')


@app.route('/community_data_mult')
def data_mult():
    data_file_path = os.path.join(app.root_path, 'data', 'community_data_mult.json')  # 数据文件路径
    if not os.path.exists(data_file_path):
        return jsonify({'error': 'Data file not found'}), 404
    with open(data_file_path, 'r', encoding='utf-8') as data_file:
        stroke_num_data = json.load(data_file)
        return jsonify(stroke_num_data)


if __name__ == '__main__':
    app.run(debug=True, port=8000)
