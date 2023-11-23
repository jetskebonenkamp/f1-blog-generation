import os
import json


def loadBlogData(folder, all_files=False, file_index=10):
    filenames = [fn for fn in os.listdir(folder) if 'ipynb' not in fn]
    all_blogs = []
    if not all_files:
        example_fn = filenames[file_index]
        full_path = folder + '/' + example_fn
        blogs = loadFromFile(full_path)
        all_blogs = [blogs]
        return all_blogs
    all_blogs = {}
    for fn in filenames:
        full_path = folder + '/' + fn
        blogs = loadFromFile(full_path)
        all_blogs[fn.split('.')[0]] = blogs
    return all_blogs


def loadFromFile(full_path):
    blogs = []
    with open(full_path, 'r') as f:
        json_data = json.load(f)
        items = json_data# ['items']
        for timestamp in items:
            blogs.append(items[timestamp])
    return blogs