import json
import colorsys
import os

init_json_file_path = 'extracted_json/1.svg.json'
output_json_file_path = 'feature_vectors.json'
features = []
# 定义桶的数量
NUM_BUCKETS = 15
# 假设的layer最小值和最大值
min_layer, max_layer = 0, 10
# 计算每个桶的大小
bucket_size = (max_layer - min_layer) / NUM_BUCKETS

with open(init_json_file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

for node_id, node_data in data.items():
    layer_values = node_data.get("layer", [])
    if layer_values:
        current_max_layer = max(map(int, layer_values))
        max_layer = max(max_layer, current_max_layer)

def tag_mapping(svg_tag):
    tag_map = {tag_name: key for key, tag_name in enumerate([
        "svg", "g", "path", "rect", "circle", "ellipse", "line", "polyline",
        "polygon", "text", "image", "use", "defs", "symbol", "marker", "pattern",
        "mask", "filter", "linearGradient", "radialGradient", "stop", "clipPath",
        "textPath", "tspan", "a", "foreignObject", "solidColor", "linearGradient", "radialGradient", "pattern", "hatch",
        "mesh","title"
    ])}
    return tag_map.get(svg_tag, -1)


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    lv = len(hex_color)
    if lv == 3:
        hex_color = ''.join([c * 2 for c in hex_color])
    elif lv != 6:
        return 0, 0, 0  # Return default for incorrect length

    if all(c in '0123456789abcdefABCDEF' for c in hex_color):
        return tuple(int(hex_color[i:i + 2], 16) for i in range(0, 6, 2))
    return 0.0, 0.0, 0.0  # Default for non-hex values


def rgb_to_hsl(rgb):
    """Convert RGB tuple to HSL tuple, rounding to 3 decimal places."""
    r_normalized, g_normalized, b_normalized = [x / 255.0 for x in rgb]
    h, l, s = colorsys.rgb_to_hls(r_normalized, g_normalized, b_normalized)
    return round(h * 360.0, 3), round(s * 100.0, 3), round(l * 100.0, 3)


def fill_mapping(fill_color):
    if fill_color and fill_color != "none":
        rgb = hex_to_rgb(fill_color)
        hsl = rgb_to_hsl(rgb)
        return hsl
    return 0.0, 0.0, 0.0


def fill_layer(layer):
    layer_vector = [0] * NUM_BUCKETS
    for layer_value in layer:
        layer_value = int(layer_value)  # 确保layer_value是整数
        if min_layer <= layer_value <= max_layer:
            index = int((layer_value - min_layer) / bucket_size)
            index = min(index, NUM_BUCKETS - 1)  # 防止索引超出范围
            layer_vector[index] = 1  # 在layer_vector中标记桶被占用
    return layer_vector


def extract_bbox_features(bbox_data):
    # 检查bbox_data是二维还是三维
    if all(isinstance(item, list) for item in bbox_data) and all(
            isinstance(subitem, (list, tuple)) for item in bbox_data for subitem in item):
        is_complex_shape = True
    else:
        is_complex_shape = False
    if is_complex_shape:
        valid_subitems = [subitem for item in bbox_data if isinstance(item, list) for subitem in item if
                          isinstance(subitem, (list, tuple)) and len(subitem) == 2]
        if valid_subitems:
            min_left = min(subitem[0] for item in bbox_data for subitem in item)
            min_top = min(subitem[1] for item in bbox_data for subitem in item)
            max_right = max(subitem[0] for item in bbox_data for subitem in item)
            max_bottom = max(subitem[1] for item in bbox_data for subitem in item)
        else:
            min_left = min_top = max_right = max_bottom  = 0.0
    else:
        min_left = min(item[0] for item in bbox_data)
        min_top = min(item[1] for item in bbox_data)
        max_right = max(item[0] for item in bbox_data)
        max_bottom = max(item[1] for item in bbox_data)

    center_x = round((min_left + max_right) / 2, 3)
    center_y = round((min_top + max_bottom) / 2, 3)
    width = round(max_right - min_left, 3)
    height = round(max_bottom - min_top, 3)
    area = round(width * height, 3)

    return round(min_top, 3), round(max_bottom, 3), round(min_left, 3), round(max_right, 3), center_x, center_y, width, height, area


def putout_features(feature_vector):
    output_dir = 'feature_txt'
    os.makedirs(output_dir, exist_ok=True)
    json_files = [file for file in os.listdir('extracted_json') if file.endswith('.json')]
    for json_file in json_files:
        output_txt_file = os.path.join(output_dir, json_file.replace('.json', '.txt'))
        output_content = ""
        output_line = f"{node_id:<30} {feature_vector}\n"
        output_content += output_line
        with open(output_txt_file, 'w', encoding='utf-8') as f:
            f.write(output_content)

        print(f"{json_file} 的特征已成功写入到文件 {output_txt_file}")


def extract_features():
    for node, datas in data.items():
        feature_vector = []
        # 处理标签并添加到特征向量
        tag = datas.get("tag").split('_')[0]
        tag_encoded = tag_mapping(tag)  # 使用One-Hot编码映射
        feature_vector.append(tag_encoded)

        # 处理并分别填充fill颜色的hsl并添加到特征向量
        fill = datas.get("fill")
        fill_encoded = fill_mapping(fill)
        for value in fill_encoded:
            feature_vector.append(value)

        # 处理并处理填充stroke颜色并添加到特征向量
        stroke = datas.get("stroke")
        stroke_encoded = fill_mapping(stroke)
        for value in stroke_encoded:
            feature_vector.append(value)

        # 使用分桶（bucketing）策略加上标准化处理处理并处理填充layer颜色并添加到特征向量
        layer = datas.get("layer", [])
        layer_encoded = fill_layer(layer)
        feature_vector.extend(layer_encoded)

        # 处理并处理填充text_content并添加到特征向量
        text_content = datas.get("text_content", "")
        feature_vector.append(1 if text_content else 0)

        # 处理并处理填充上下左右边界中点长宽高面积并添加到特征向量
        bbox = datas.get("bbox")
        bbox_encoded = extract_bbox_features(bbox)
        for value in bbox_encoded:
            feature_vector.append(value)

        # print(len(feature_vector))
        print(f"{node.split('/')[len(node.split('/')) - 1]:<15} {feature_vector}")


extract_features()
