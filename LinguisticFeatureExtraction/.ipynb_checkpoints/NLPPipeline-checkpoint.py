from fastcoref import spacy_component
import spacy
import random
from spacy.util import minibatch, compounding
from spacy.training import Example


class NLPPipeline:
    def __init__(self, model_name):
        self.nlp = self.loadModel(model_name)
        self.ner = self.nlp.get_pipe('ner')

    def trainNerModel(self, train_data):
        for _, annotations in train_data:
            for ent in annotations.get('entities'):
                self.ner.add_label(ent[2])
        pipe_exceptions = ["ner", "trf_wordpiecer", "trf_tok2vec"]
        unaffected_pipes = [pipe for pipe in self.nlp.pipe_names
                            if pipe not in pipe_exceptions]
        with self.nlp.disable_pipes(*unaffected_pipes):
            for iteration in range(30):
                random.shuffle(train_data)
                losses = {}
                batches = minibatch(train_data,
                                    size=compounding(4.0, 32.0, 1.001))
                for batch in batches:
                    self.updateByBatch(batch, losses)

    def updateByBatch(self, batch, losses):
        batch_examples = []
        for text, annotations in batch:
            doc = self.nlp.make_doc(text)
            batch_examples.append(Example.from_dict(doc, annotations))
        self.nlp.update(batch_examples, drop=0.5, losses=losses)

    def loadModel(self, model_name):
        nlp = spacy.load(model_name)
        nlp.add_pipe('fastcoref')
        return nlp