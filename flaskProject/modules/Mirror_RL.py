class FeatureVectorModifier:
    def __init__(self):
        # 使用指定的路径作为类的属性
        # self.file_path = './Contrastive_Clustering/test/extracted_nodes.txt'
        # self.output_path = './Contrastive_Clustering/testR/extracted_nodes_mirror.txt'
        self.file_path = './modules/Contrastive_Clustering/test/extracted_nodes.txt'
        self.output_path = './modules/Contrastive_Clustering/testR/extracted_nodes_mirror.txt'

    def modify_features(self):
        modified_vectors = []

        with open(self.file_path, 'r') as file:
            for line in file:
                original_line = line.strip()  # 保留原始行
                features = original_line.split(' ')
                tag = features[0]  # 提取标签
                values = features[1:]  # 特征值

                float_values = list(map(float, values))

                # 对特征向量进行复制，并对调left和right的值
                copied_values = float_values.copy()
                copied_values[14], copied_values[15] = copied_values[15], copied_values[14]

                # 更新标签，给复制的向量的标签结尾加上'R'
                modified_tag = tag + 'R'

                modified_vector = [modified_tag] + list(map(str, copied_values))

                # 首先添加原始向量到结果列表
                modified_vectors.append(original_line + '\n')
                # 然后添加修改后的向量
                modified_vectors.append(' '.join(modified_vector) + '\n')

        # 将包含原始和修改后的向量的列表写入到指定的输出文件中
        with open(self.output_path, 'w') as file:
            file.writelines(modified_vectors)


# 使用示例
# modifier = FeatureVectorModifier()
# modifier.modify_features()
