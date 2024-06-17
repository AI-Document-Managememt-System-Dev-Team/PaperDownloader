import os

class TXTInfo:
    def __init__(self, folder='information'):
        self.folder = folder
        # 如果文件夹不存在，创建文件夹
        if not os.path.exists(folder):
            os.makedirs(folder)

    # 插入或更新文本文件的函数
    def update_entry(self, name, abstract, keywords, site):
        file_path = os.path.join(self.folder, f"{name}.txt")
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(f"{abstract}\n{keywords}\n{site}")
            print(f'条目 {name} 已创建/更新。')

