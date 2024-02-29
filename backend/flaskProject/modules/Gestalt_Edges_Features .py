import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_diff import delta_e_cie2000
from colormath.color_conversions import convert_color

# 假定的文件路径，这里作为示例，实际路径可能需要调整
input_nodes_file = '../GMoutput/GMinfo.json'
output_nodes_file = '../GMoutput/extracted_nodes.json'
input_SimGraph_file = '../GMoutput/extracted_nodes.json'
output_SimGraph_file = '../GMoutput/similarity_graph.json'


class NodeExtractor:
    @staticmethod
    def parse_points_from_string(points_str):
        points_list = []
        points_pairs = points_str.split()
        for pair in points_pairs:
            x_str, y_str = pair.split(',')
            points_list.append([float(x_str), float(y_str)])
        return points_list

    @staticmethod
    def calculate_bboxs_for_line_polygon_polyline(points):
        bboxs = []
        for i in range(len(points) - 1):
            start = points[i]
            end = points[i + 1]
            mid = [(start[0] + end[0]) / 2, (start[1] + end[1]) / 2]
            bbox = [start, end, mid]
            bboxs.append(bbox)
        return bboxs

    @staticmethod
    def extract_nodes_info(input_file, output_file):
        with open(input_file, 'r', encoding='utf-8') as file:
            data = json.load(file)

        nodes = data['DiGraph']['Nodes']
        extracted_nodes = {}

        for node, attributes in nodes.items():
            tag = attributes['Attributes']['tag']
            attrs = attributes['Attributes']['attributes']
            visible = attributes['Attributes']['visible']
            level = attributes['Attributes']['level']
            layer = attributes['Attributes']['layer'].split('_')
            text_content = attributes['Attributes']['text_content']
            bbox = attributes['Attributes']['attributes']['bbox']

            extracted_attrs = {
                'tag': tag,
                'stroke': attrs.get('stroke', None),
                'stroke-width': attrs.get('stroke-width', 1),
                'stroke-opacity': attrs.get('stroke-opacity', 1),
                'fill': attrs.get('fill', None),
                'opacity': attrs.get('opacity', 1),
                'level': level,
                'layer': layer,
                'text_content': text_content
            }

            if tag.split('_')[0] == "path":
                pcode = attrs.get('Pcode', [])
                pnums = attrs.get('Pnums', [])
                path_to_lines = PathToLines(pcode, pnums)
                bboxs = path_to_lines.get_bboxs()
                extracted_attrs['bbox'] = bboxs
                extracted_nodes[node] = extracted_attrs

            elif tag.split('_')[0] in ["polygon", "polyline"]:
                points_str = attrs.get('points', "")
                points = NodeExtractor.parse_points_from_string(points_str)
                bboxs = NodeExtractor.calculate_bboxs_for_line_polygon_polyline(points)
                extracted_attrs['bbox'] = bboxs
                extracted_nodes[node] = extracted_attrs

            elif visible:
                extracted_attrs['bbox'] = bbox
                extracted_nodes[node] = extracted_attrs

        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(extracted_nodes, file, indent=4)


class PathToLines:
    def __init__(self, pcode, pnums):
        self.last_control = None
        self.pcode = pcode
        self.pnums = pnums
        self.lines = []  # 保存线段
        self.bboxs = []  # 保存线段的bbox
        self.current_position = (0, 0)  # 初始化当前位置
        self.start_position = None  # 保存路径的起始位置
        self.last_control_point = None  # 保存最后一个控制点
        self.last_command = None  # 保存最后执行的命令

    def process_commands(self):
        for code, nums in zip(self.pcode, self.pnums):
            if code == 'M':
                self.move_to(nums)
            elif code == 'L':
                self.line_to(nums)
            elif code == 'H':
                self.horizontal_line_to(nums)
            elif code == 'V':
                self.vertical_line_to(nums)
            elif code == 'C':
                self.cubic_bezier_to(nums)
            elif code == 'S':
                self.smooth_cubic_bezier_to(nums)
            elif code == 'Q':
                self.quadratic_bezier_to(nums)
            elif code == 'T':
                self.smooth_quadratic_bezier_to(nums)
            elif code == 'Z':
                self.close_path()

    def move_to(self, nums):
        x, y = float(nums[0]), float(nums[1])
        self.current_position = (x, y)
        # 当执行M命令时，更新起始位置
        self.start_position = (x, y)
        self.last_command = 'M'

    def line_to(self, nums):
        x, y = float(nums[0]), float(nums[1])
        self.lines.append([self.current_position, (x, y)])
        self.calculate_line_bbox(self.current_position, (x, y))
        self.current_position = (x, y)

    def quadratic_bezier_to(self, nums):
        cx, cy, x, y = map(float, nums)
        start = self.current_position
        control = (cx, cy)
        end = (x, y)
        points = [start]
        for t in range(1, 11):
            t /= 10  # 将t从0变化到1
            bx = round((1 - t) ** 2 * start[0] + 2 * (1 - t) * t * control[0] + t ** 2 * end[0], 2)
            by = round((1 - t) ** 2 * start[1] + 2 * (1 - t) * t * control[1] + t ** 2 * end[1], 2)
            points.append((bx, by))
        points.append(end)

        # 对每个连续的点对绘制直线
        for i in range(len(points) - 1):
            self.lines.append([points[i], points[i + 1]])
            self.calculate_line_bbox(points[i], points[i + 1])

    def smooth_quadratic_bezier_to(self, nums):
        # 假设前一个贝塞尔曲线的控制点存储在 last_control 变量中
        # 如果没有前一个贝塞尔曲线（即这是第一个T命令），可以简化处理为直线
        if not hasattr(self, 'last_control') or self.last_control is None:
            self.line_to(nums)
        else:
            # 计算当前控制点为上一个控制点的反射点
            reflect_x = 2 * self.current_position[0] - self.last_control[0]
            reflect_y = 2 * self.current_position[1] - self.last_control[1]
            self.last_control = (reflect_x, reflect_y)  # 更新控制点
            x, y = float(nums[0]), float(nums[1])
            # 使用反射的控制点绘制二次贝塞尔曲线
            self.quadratic_bezier_to([reflect_x, reflect_y, x, y])

    def calculate_line_bbox(self, start, end):
        # 应用四舍五入，这里假设保留两位小数
        min_x, max_x = round(min(start[0], end[0]), 2), round(max(start[0], end[0]), 2)
        min_y, max_y = round(min(start[1], end[1]), 2), round(max(start[1], end[1]), 2)
        mid_x = round((start[0] + end[0]) / 2, 2)
        mid_y = round((start[1] + end[1]) / 2, 2)
        self.bboxs.append([[min_x, min_y], [max_x, max_y], [mid_x, mid_y]])

    def horizontal_line_to(self, nums):
        x = float(nums[0])
        self.lines.append([self.current_position, (x, self.current_position[1])])
        self.calculate_line_bbox(self.current_position, (x, self.current_position[1]))
        self.current_position = (x, self.current_position[1])

    def vertical_line_to(self, nums):
        y = float(nums[0])
        self.lines.append([self.current_position, (self.current_position[0], y)])
        self.calculate_line_bbox(self.current_position, (self.current_position[0], y))
        self.current_position = (self.current_position[0], y)

    def cubic_bezier_to(self, nums):
        c1x, c1y, c2x, c2y, x, y = map(float, nums)
        start = self.current_position
        control1 = (c1x, c1y)
        control2 = (c2x, c2y)
        end = (x, y)
        points = [start]
        steps = 10  # 曲线分割成多少段，可以根据需要调整

        for step in range(1, steps + 1):
            t = step / steps
            # 三次贝塞尔曲线方程
            bx = (1 - t)**3 * start[0] + 3 * (1 - t)**2 * t * control1[0] + 3 * (1 - t) * t**2 * control2[0] + t**3 * end[0]
            by = (1 - t)**3 * start[1] + 3 * (1 - t)**2 * t * control1[1] + 3 * (1 - t) * t**2 * control2[1] + t**3 * end[1]
            points.append((round(bx, 2), round(by, 2)))

        # 使用计算出的点更新线段和边界框列表
        for i in range(len(points) - 1):
            self.lines.append([points[i], points[i + 1]])
            self.calculate_line_bbox(points[i], points[i + 1])

        # 更新当前位置为曲线的结束点
        self.current_position = end

    def smooth_cubic_bezier_to(self, nums):
        # 新控制点和结束点
        c2x, c2y, x, y = map(float, nums)

        if self.last_command in ['C', 'S']:
            # 前一个命令是C或S，计算反射的控制点
            last_cx, last_cy = self.last_control_point
            # 计算反射点，即当前点关于最后一个控制点的对称点
            c1x = 2 * self.current_position[0] - last_cx
            c1y = 2 * self.current_position[1] - last_cy
        else:
            # 前一个命令不是C或S，第一个控制点与当前点相同
            c1x, c1y = self.current_position

        # 使用计算出的控制点和结束点绘制三次贝塞尔曲线
        self.cubic_bezier_to([c1x, c1y, c2x, c2y, x, y])

        # 更新最后一个控制点和命令
        self.last_control_point = (c2x, c2y)
        self.last_command = 'S'

    def close_path(self):
        # 如果存在起始位置，则将当前位置连接回起始位置
        if self.start_position:
            self.lines.append([self.current_position, self.start_position])
            self.calculate_line_bbox(self.current_position, self.start_position)
            # 更新当前位置为起始位置，闭合路径
            self.current_position = self.start_position
        self.last_command = 'Z'

    def get_bboxs(self):
        self.process_commands()
        return self.bboxs


class GestaltSimilarityCalculator:
    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file
        self.nodes = self.load_nodes()
        self.edges = []

    def load_nodes(self):
        with open(self.input_file, 'r') as file:
            data = json.load(file)
        return data

    @staticmethod
    def hex_to_rgb(hex_color):
        if hex_color in ['none', 'transparent', None]:
            return None  # 返回None表示颜色为透明或无效
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join([c * 2 for c in hex_color])
        try:
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        except ValueError:
            return None

    @staticmethod
    def calculate_ciede2000(hex_color1, hex_color2):
        rgb_color1 = GestaltSimilarityCalculator.hex_to_rgb(hex_color1)
        rgb_color2 = GestaltSimilarityCalculator.hex_to_rgb(hex_color2)
        # 检查rgb_color1或rgb_color2是否为None
        if rgb_color1 is None or rgb_color2 is None:
            return 100  # 返回最大色差，以表示完全不相似

        color1_rgb = sRGBColor(*rgb_color1, is_upscaled=True)
        color2_rgb = sRGBColor(*rgb_color2, is_upscaled=True)
        color1_lab = convert_color(color1_rgb, LabColor)
        color2_lab = convert_color(color2_rgb, LabColor)
        delta_e = delta_e_cie2000(color1_lab, color2_lab)
        return delta_e

    def calculate_similarity(self):
        node_ids = list(self.nodes.keys())  # 获取所有节点的ID列表
        n = len(node_ids)  # 节点总数
        for i in range(n):  # 对于每个节点
            node_id = node_ids[i]
            for j in range(i+1, n):  # 仅与其后的节点比较
                other_node_id = node_ids[j]
                # 无需检查 node_id != other_node_id，因为 j 始终大于 i
                gestalt_matrix = self.calculate_gestalt_matrix(self.nodes[node_id], self.nodes[other_node_id])
                self.edges.append([node_id, other_node_id, gestalt_matrix])

    def calculate_layer_similarity(self, layer1, layer2):
        # 计算两个layer数组的最长公共前缀的长度
        min_length = min(len(layer1), len(layer2))
        lcp_length = 0  # 最长公共前缀的长度
        for i in range(min_length):
            if layer1[i] == layer2[i]:
                lcp_length += 1
            else:
                break

        # 计算相似度：最长公共前缀长度 / 较长数组的长度
        max_length = max(len(layer1), len(layer2))
        if max_length == 0:  # 防止除以0的情况
            return 1.000  # 如果两个layer数组都为空，则认为它们完全相似
        layer_similarity = lcp_length / max_length
        # 使用round函数保留三位小数
        return round(layer_similarity, 3)

    @staticmethod
    def rolling_hash(s, length):
        """计算字符串s中所有长度为length的子串的哈希值。"""
        if length == 0:
            return []
        base, mod = 256, 10 ** 9 + 7
        hash_values = []
        current_hash = 0
        for i in range(len(s)):
            current_hash = (current_hash * base + ord(s[i])) % mod
            if i >= length - 1:
                if i >= length:
                    # 减去最左边字符的影响
                    left_exp = pow(base, length, mod)
                    current_hash = (current_hash - ord(s[i - length]) * left_exp) % mod
                hash_values.append(current_hash)
        return hash_values

    def find_lcs_with_binary_search(self, s1, s2):
        """使用二分搜索和哈希来寻找最长公共子串的长度。"""
        left, right = 0, min(len(s1), len(s2))
        result = 0
        while left <= right:
            mid = (left + right) // 2
            hash_set1 = set(GestaltSimilarityCalculator.rolling_hash(s1, mid))
            if any(GestaltSimilarityCalculator.rolling_hash(s2, mid)[i] in hash_set1 for i in range(len(s2) - mid + 1)):
                result = mid
                left = mid + 1
            else:
                right = mid - 1
        return result

    # 使用二分搜索优化后的文本内容相似度计算方法
    def calculate_text_content_similarity(self, text1, text2):
        # 如果text1或text2为None，直接返回0.000
        if text1 is None or text2 is None:
            return 0.000

        # 如果文本内容完全相同
        if text1 == text2:
            return 1.000

        lcs_length = self.find_lcs_with_binary_search(text1, text2)
        max_text_length = max(len(text1), len(text2))

        if max_text_length == 0:  # 如果两个字符串都是空的
            return 1.000  # 理论上，两个空字符串是完全相同的，但根据实际情况可能需要调整

        text_content_similarity = round(lcs_length / max_text_length, 3)
        return text_content_similarity

    # def calculate_gestalt_matrix(self, node_attrs, other_node_attrs):
    #     gestalt_matrix = {
    #         "color_similarity": self.calculate_color_similarity(node_attrs, other_node_attrs),
    #         "tag_similarity": self.calculate_tag_similarity(node_attrs, other_node_attrs),  # 确保此处无误
    #         "position_similarity": self.calculate_position_similarity(node_attrs, other_node_attrs)
    #     }
    #     return gestalt_matrix
    def calculate_gestalt_matrix(self, node_attrs, other_node_attrs):
        color_similarity = self.calculate_color_similarity(node_attrs, other_node_attrs)
        tag_similarity = self.calculate_tag_similarity(node_attrs, other_node_attrs)
        position_similarity = self.calculate_position_similarity(node_attrs, other_node_attrs)
        gestalt_features_values = []

        if isinstance(color_similarity, dict):
            gestalt_features_values.extend(color_similarity.values())
        else:
            gestalt_features_values.append(color_similarity)

        gestalt_features_values.extend(tag_similarity.values())
        gestalt_features_values.extend(position_similarity.values())

        return gestalt_features_values

    def calculate_tag_similarity(self, node_attrs, other_node_attrs):
        tag_match = 0.0
        # 检查节点类型，判断是面型还是线型

        def check_node_type(node):
            bbox = node.get('bbox', [])
            if isinstance(bbox[0][0], list):  # 检查bbox第一个元素的第一个元素是否为列表，判断为线型
                return 'line'
            else:
                return 'face'
        node_type1 = check_node_type(node_attrs)
        node_type2 = check_node_type(other_node_attrs)

        # 完全相同的tag
        if node_attrs.get('tag') == other_node_attrs.get('tag'):
            tag_match = 1.0
        elif node_type1 == node_type2:
            tag_match = 0.5  # 同类型（面型与面型，或线型与线型）

        # 计算layer_similarity
        layer1 = node_attrs.get('layer', [])
        layer2 = other_node_attrs.get('layer', [])
        layer_similarity = self.calculate_layer_similarity(layer1, layer2)

        # 计算text_content_similarity
        text1 = node_attrs.get('text_content', '')
        text2 = other_node_attrs.get('text_content', '')
        text_content_similarity = self.calculate_text_content_similarity(text1, text2)

        return {
            "tag_match": tag_match,
            "layer_similarity": layer_similarity,
            "text_content_similarity": text_content_similarity
        }

    def calculate_position_similarity(self, node_attrs, other_node_attrs):
        def get_unified_bbox(node_attrs):
            bbox_data = node_attrs.get('bbox', [])
            # 检查是否为线型元素的bboxs
            if bbox_data and isinstance(bbox_data[0], list) and isinstance(bbox_data[0][0], list):
                # 线型元素，合并bboxs的边界
                x_min = min(bbox[0][0] for bbox in bbox_data if bbox)
                y_min = min(bbox[0][1] for bbox in bbox_data if bbox)
                x_max = max(bbox[1][0] for bbox in bbox_data if bbox)
                y_max = max(bbox[1][1] for bbox in bbox_data if bbox)
                unified_bbox = [(x_min, y_min, x_max, y_max)]
            elif bbox_data and isinstance(bbox_data[0], list) and len(bbox_data[0]) == 2:
                # 面型元素或单个线型元素的bbox，直接使用
                unified_bbox = [(bbox_data[0][0], bbox_data[0][1], bbox_data[1][0], bbox_data[1][1])]
            else:
                # 未知或缺失的bbox数据，返回默认的空bbox
                unified_bbox = [(0, 0, 0, 0)]

            return unified_bbox

        def calculate_similarity(value1, value2, max_difference):
            diff = abs(value1 - value2)
            similarity = max(0, min(1, 1 - diff / max_difference))
            return round(similarity, 3)

        def calculate_area_similarity(area1, area2):
            # 面积相似度可以基于最小和最大面积的比例来计算
            min_area, max_area = min(area1, area2), max(area1, area2)
            area = min_area / max_area if max_area > 0 else 1
            return round(area, 3)

        bbox1 = get_unified_bbox(node_attrs)[0]
        bbox2 = get_unified_bbox(other_node_attrs)[0]
        max_difference = 100  # 可以调整，以适应不同的场景
        top_edge_similarity = calculate_similarity(bbox1[1], bbox2[1], max_difference)
        left_edge_similarity = calculate_similarity(bbox1[0], bbox2[0], max_difference)
        bottom_edge_similarity = calculate_similarity(bbox1[3], bbox2[3], max_difference)
        right_edge_similarity = calculate_similarity(bbox1[2], bbox2[2], max_difference)
        area1 = (bbox1[2] - bbox1[0]) * (bbox1[3] - bbox1[1])
        area2 = (bbox2[2] - bbox2[0]) * (bbox2[3] - bbox2[1])
        area_similarity = calculate_area_similarity(area1, area2)

        def calculate_bbox_intersection(bbox1, bbox2):
            x_min1, y_min1, x_max1, y_max1 = bbox1
            x_min2, y_min2, x_max2, y_max2 = bbox2

            # 计算交集的边界
            x_min_intersection = max(x_min1, x_min2)
            y_min_intersection = max(y_min1, y_min2)
            x_max_intersection = min(x_max1, x_max2)
            y_max_intersection = min(y_max1, y_max2)

            # 检查是否存在交集
            if x_min_intersection < x_max_intersection and y_min_intersection < y_max_intersection:
                return (x_min_intersection, y_min_intersection, x_max_intersection, y_max_intersection)
            else:
                return None

        def calculate_overlap_ratio(bbox1, bbox2):
            intersection_bbox = calculate_bbox_intersection(bbox1, bbox2)

            if intersection_bbox is None:
                # 如果没有交集，则overlap_ratio为0
                return 0.0

            # 计算交集面积
            intersection_area = (intersection_bbox[2] - intersection_bbox[0]) * (
                        intersection_bbox[3] - intersection_bbox[1])

            # 计算并集面积
            area1 = (bbox1[2] - bbox1[0]) * (bbox1[3] - bbox1[1])
            area2 = (bbox2[2] - bbox2[0]) * (bbox2[3] - bbox2[1])
            union_area = area1 + area2 - intersection_area

            # 计算比例
            overlap_ratio = intersection_area / union_area if union_area > 0 else 0.0

            return round(overlap_ratio, 3)

        overlap_ratio = calculate_overlap_ratio(bbox1, bbox2)
        # 实现位置相似度计算
        return {
            "top_edge_similarity": top_edge_similarity,
            "bottom_edge_similarity": bottom_edge_similarity,
            "left_edge_similarity": left_edge_similarity,
            "right_edge_similarity": right_edge_similarity,
            "area_similarity": area_similarity,
            "overlap_ratio": overlap_ratio
        }

    def calculate_color_similarity(self, node_attrs, other_node_attrs):
        # 实现颜色相似度计算
        fill1 = node_attrs["fill"]
        fill2 = other_node_attrs["fill"]

        def hex_to_rgb(hex_color):
            if hex_color in ['none', 'transparent', None]:
                return None  # 返回None表示颜色为透明或无效
            hex_color = hex_color.lstrip('#')
            if len(hex_color) == 3:
                hex_color = ''.join([c * 2 for c in hex_color])
            try:
                return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
            except ValueError:
                return None

        def rgb_color_difference(rgb1, rgb2):
            """计算两个RGB颜色之间的欧几里得距离。"""
            return sum((c1 - c2) ** 2 for c1, c2 in zip(rgb1, rgb2)) ** 0.5

        def calculate_fill_color_difference(fill1, fill2):
            if fill1 in [None, 'none', ''] or fill2 in [None, 'none', '']:
                return 0.0 if fill1 != fill2 else 1.0

            rgb1 = hex_to_rgb(fill1)
            rgb2 = hex_to_rgb(fill2)


            # 如果转换后的RGB值为None，则直接返回最低相似度0.0
            if rgb1 is None or rgb2 is None:
                return 0.0

            color_diff = rgb_color_difference(rgb1, rgb2)

            # 将颜色差异转换为相似度，这里使用的是简化的线性转换
            # 注意：这个转换公式可能需要根据实际情况调整
            color_similarity = max(0, 1 - (color_diff / (255 * 3 ** 0.5)))
            return round(color_similarity, 3)


        fill_color_difference = calculate_fill_color_difference(fill1, fill2)

        def calculate_opacity_difference(opacity1, opacity2):
            # 确保opacity值是有效的小数
            opacity1 = float(opacity1) if opacity1 is not None else 1.0  # 默认不透明
            opacity2 = float(opacity2) if opacity2 is not None else 1.0  # 默认不透明

            # 计算两个opacity值之间的差异，并转换为相似度
            opacity_diff = abs(opacity1 - opacity2)
            opacity_similarity = 1 - opacity_diff

            # 保证相似度在0到1之间
            opacity_similarity = max(0, min(opacity_similarity, 1))

            # 返回保留3位小数的相似度值
            return round(opacity_similarity, 3)

        opacity1 = node_attrs.get('opacity', '1.0')  # 如果没有指定，默认为不透明
        opacity2 = other_node_attrs.get('opacity', '1.0')  # 如果没有指定，默认为不透明

        # 计算opacity的相似度
        opacity_difference = calculate_opacity_difference(opacity1, opacity2)

        def rgb_to_hsl(r, g, b):
            r /= 255.0
            g /= 255.0
            b /= 255.0
            max_color = max(r, g, b)
            min_color = min(r, g, b)
            l = (max_color + min_color) / 2.0

            if max_color == min_color:
                h = s = 0
            else:
                d = max_color - min_color
                s = d / (2.0 - max_color - min_color) if l > 0.5 else d / (max_color + min_color)
                if max_color == r:
                    h = (g - b) / d + (6 if g < b else 0)
                elif max_color == g:
                    h = (b - r) / d + 2
                else:
                    h = (r - g) / d + 4
                h /= 6.0
            return h * 360, s, l

        def calculate_brightness_difference(fill1, fill2):
            rgb1 = hex_to_rgb(fill1)
            rgb2 = hex_to_rgb(fill2)
            if rgb1 is None or rgb2 is None:
                return 0.0  # 如果颜色无效，亮度差异设为0

            hsl1 = rgb_to_hsl(*rgb1)
            hsl2 = rgb_to_hsl(*rgb2)

            # 计算亮度(L)值的差异，并转换为相似度
            l_diff = abs(hsl1[2] - hsl2[2])
            brightness_similarity = 1 - l_diff

            return round(brightness_similarity, 3)

        # 提取fill颜色并计算brightness_difference
        fill1 = node_attrs.get("fill", "#000000")  # 默认白色
        fill2 = other_node_attrs.get("fill", "#000000")  # 默认白色

        brightness_difference = calculate_brightness_difference(fill1, fill2)

        def calculate_saturation_difference(fill1, fill2):
            rgb1 = self.hex_to_rgb(fill1)
            rgb2 = self.hex_to_rgb(fill2)
            if rgb1 is None or rgb2 is None:
                # 如果颜色无效，饱和度差异设为0
                return 0.0

            hsl1 = rgb_to_hsl(*rgb1)
            hsl2 = rgb_to_hsl(*rgb2)

            # 计算饱和度(S)值的差异，并转换为相似度
            s_diff = abs(hsl1[1] - hsl2[1])
            saturation_similarity = 1 - s_diff

            # 保留3位小数并返回
            return round(saturation_similarity, 3)

        saturation_difference = calculate_saturation_difference(fill1, fill2)


        stroke1 = node_attrs.get('stroke', '#000000')  # 默认值
        stroke2 = other_node_attrs.get('stroke', '#000000')  # 默认值
        stroke_color_similarity = self.calculate_fill_or_stroke_similarity(stroke1, stroke2)
        # 获取stroke-width值
        stroke_width1 = node_attrs.get('stroke-width', '1')  # 如果没有指定，默认为1
        stroke_width2 = other_node_attrs.get('stroke-width', '1')  # 如果没有指定，默认为1

        def calculate_stroke_width_similarity(stroke_width1, stroke_width2, max_difference=10):
            # 转换stroke-width值为浮点数
            stroke_width1 = float(stroke_width1) if stroke_width1 is not None else 1.0  # 默认值为1
            stroke_width2 = float(stroke_width2) if stroke_width2 is not None else 1.0  # 默认值为1

            # 计算绝对差异
            diff = abs(stroke_width1 - stroke_width2)

            # 规范化差异并转换为相似度
            # 注意：这里使用的max_difference是一个预定义的最大差异值，可根据实际需要调整
            similarity = max(0, 1 - (diff / max_difference))

            # 保留3位小数并返回
            return round(similarity, 3)
        # 计算stroke-width的相似度
        stroke_width_similarity = calculate_stroke_width_similarity(stroke_width1, stroke_width2)

        return {
            "fill_color_difference": fill_color_difference,
            "opacity_difference": opacity_difference,
            "brightness_difference": brightness_difference,
            "saturation_difference": saturation_difference,
            "stroke_color_similarity": stroke_color_similarity,
            "stroke_width_similarity": stroke_width_similarity
        }

    def calculate_fill_or_stroke_similarity(self, color1, color2):
        # 如果两个颜色值都是None或'transparent'，则视为完全相似
        if (color1 in [None, 'transparent', '']) and (color2 in [None, 'transparent', '']):
            return 1.0
        # 如果任一颜色为None或'transparent'，则视为完全不相似
        elif (color1 in [None, 'transparent', '']) or (color2 in [None, 'transparent', '']):
            return 0.0

        rgb1 = self.hex_to_rgb(color1)
        rgb2 = self.hex_to_rgb(color2)

        # 如果颜色转换失败（例如，无效的十六进制颜色代码），则直接返回最低相似度0.0
        if rgb1 is None or rgb2 is None:
            return 0.0
        def rgb_color_difference(rgb1, rgb2):
            """计算两个RGB颜色之间的欧几里得距离。"""
            return sum((c1 - c2) ** 2 for c1, c2 in zip(rgb1, rgb2)) ** 0.5
        # 计算RGB颜色差异，并转换为相似度
        color_diff = rgb_color_difference(rgb1, rgb2)
        color_similarity = max(0, 1 - (color_diff / (255 * 3 ** 0.5)))

        return round(color_similarity, 3)

    def save_to_file(self):
        output_data = {"Gestalt_Edges": self.edges}
        with open(self.output_file, 'w') as file:
            json.dump(output_data, file, indent=4)

    def run(self):
        self.calculate_similarity()
        self.save_to_file()


def draw_lines_from_json(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)

    fig, ax = plt.subplots()

    for node, attrs in data.items():
        # 只处理path类型的节点
        if attrs['tag'].split('_')[0] == 'path':
            bboxs = attrs.get('bbox', [])
    #         for bbox in bboxs:
    #             if bbox:
    #                 start_point = bbox[0]  # 起点
    #                 end_point = bbox[1]    # 终点
    #                 # 绘制直线段，使用起点和终点坐标
    #                 ax.plot([start_point[0], end_point[0]], [start_point[1], end_point[1]], marker = 'o')
    #
    # ax.set_aspect('equal', adjustable='datalim')
    # plt.show()


def update_graph_with_similarity_edges():
    extractor = NodeExtractor()
    extractor.extract_nodes_info(input_nodes_file, output_nodes_file)
    print(f"Extracted nodes information saved to {output_nodes_file}")
    calculator = GestaltSimilarityCalculator(input_SimGraph_file, output_SimGraph_file)
    calculator.run()


update_graph_with_similarity_edges()
# draw_lines_from_json(output_nodes_file)
