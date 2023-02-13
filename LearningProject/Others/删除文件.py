import os


def del_files(path):
    for root, _, file_name in os.walk(path):
        for file in file_name:
            if 'old' in file:
                os.remove(os.path.join(root, file))


path = input('文件目录：')
del_files(path)
