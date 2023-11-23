from NLPPipeline import NLPPipeline
from BlogData import loadBlogData
from FeatureExtractor import FeatureExtractor
import pickle
import json


def loadPipe(folder):
    # create nlp pipeline and further train a NER model for our scope
    model_path = folder + './NamedEntityRecognition/ner_training_data.ob'
    with open(model_path, 'rb') as f: train_data = pickle.load(f)
    pipe = NLPPipeline('en_core_web_sm')
    pipe.trainNerModel(train_data)
    return pipe


def extractFeatures(blogs, pipe):
    # boundaries set to exclude pre- and post-race posts
    blogs, blog_objects = blogs[15:len(blogs)-15], {}
    for blog in blogs:
        fe = FeatureExtractor(blog, pipe.nlp)
        data_objs = fe.getDataObjects()
        if data_objs:
            blog_objects[blog] = []
            for obj in data_objs: blog_objects[blog].append(obj)
    return blog_objects


def extractAllFeatures():
    # retrieve blog posts and extract data objects
    folder = '../../Data Extraction/BlogData/'
    all_blogs = loadBlogData(folder + 'DataSet', all_files=True)
    pipe, all_blog_objects = loadPipe(folder), {}
    for key in list(all_blogs.keys()):
        all_blog_objects[key] = extractFeatures(all_blogs[key], pipe)
    return all_blog_objects


def saveIoPairs():
    # save extracted data objects
    all_blog_objects = extractFeatures()
    for key in list(all_blog_objects.keys()):
        blog_objects = all_blog_objects[key]
        fn = 'IOPairs/IO_' + key + '.json'
        with open(fn, 'w') as f: json.dump(blog_objects, f)


saveIoPairs()