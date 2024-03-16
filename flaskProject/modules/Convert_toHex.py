import json
from PIL import ImageColor

class ColorFormatConverter:
    def __init__(self, file_path):
        self.file_path = file_path

    def read_json_file(self):
        with open(self.file_path, 'r', encoding='utf-8') as file:
            self.data = json.load(file)

    def convert_color_to_hex(self, color):
        try:
            if color is None or not isinstance(color, str):
                return color
            if color.startswith("#"):
                return color
            hex_color = ImageColor.getcolor(color, "RGB")
            return f'#{hex_color[0]:02x}{hex_color[1]:02x}{hex_color[2]:02x}'
        except Exception as e:
            return color

    def update_color_format(self):
        for node_key, node_value in self.data["DiGraph"]["Nodes"].items():
            attributes = node_value.get("Attributes", {})
            for attr_key, attr_value in attributes.get("attributes", {}).items():
                if attr_key in ["fill", "stroke"]:
                    # print(self.convert_color_to_hex(attr_value))
                    attributes["attributes"][attr_key] = self.convert_color_to_hex(attr_value)

    def save_json_file(self):
        with open(self.file_path, 'w', encoding='utf-8') as file:
            json.dump(self.data, file, ensure_ascii=False, indent=4)

    def process_file(self):
        self.read_json_file()
        self.update_color_format()
        self.save_json_file()


