from NLPPipeline import NLPPipeline
from BlogData import loadBlogData
from FeatureExtractor import FeatureExtractor
import pickle
import json


def loadPipe(folder):
    with open(folder + './NamedEntityRecognition/ner_training_data2.ob', 'rb') as f:
        train_data = pickle.load(f)
    pipe = NLPPipeline('en_core_web_sm')
    pipe.trainNerModel(train_data)
    return pipe


def extractFeatures():
    folder = '../../Data Extraction/BlogData/'
    all_blogs = loadBlogData(folder + 'JSONData_Autosport3', all_files=True)
    pipe = loadPipe(folder)
    all_blog_objects = {}
    for key in list(all_blogs.keys()):
        blogs = all_blogs[key]
        # since the first and last sequence of blog posts
        # contain pre- and post-race content, the first
        # and last 15 items are excluded
        blogs = blogs[15:len(blogs)-15]
        blog_objects = {}
        for blog in blogs:
            fe = FeatureExtractor(blog, pipe.nlp)
            data_objs = fe.getDataObjects()
            if data_objs:
                blog_objects[blog] = []
                for obj in data_objs:
                    blog_objects[blog].append(obj)
        all_blog_objects[key] = blog_objects
    return all_blog_objects


def establishDataset():
    all_blog_objects = extractFeatures()
    for key in list(all_blog_objects.keys()):
        blog_objects = all_blog_objects[key]
        fn = 'IOPairs/IO_' + key + '.json'
        with open(fn, 'w') as f:
            json.dump(blog_objects, f)


establishDataset()