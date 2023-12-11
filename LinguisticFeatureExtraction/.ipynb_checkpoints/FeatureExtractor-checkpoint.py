from Subject import Subject
from Action import Action
from Object import Object
from Coref import Coref
from ObjectEditor import ObjectEditor


class FeatureExtractor:
    def __init__(self, blog, nlp):
        self.blog, self.doc = blog, nlp(blog)
        self.nouns, self.verbs = self.getFeatures()
        self.coref = Coref(self)

    def getFeatures(self):
        nouns = [token for token in self.doc if token.pos_ == 'PROPN'
                 or token.pos_ == 'NOUN']
        verbs = [token for token in self.doc if token.pos_ == 'VERB'
                 or token.pos_ == 'AUX' or token.text == 'pits']
        return nouns, verbs

    def getDataObjects(self):
        data_objects = []
        # looping through the verbs to get the full actions and the
        # corresponding subjects and objects
        for verb in self.verbs:
            subj = Subject(verb, self.nouns, self.doc, self.coref)
            # skip the verb if there is no subject identified
            if not subj.subj:
                continue
            dis_subj = subj.getDisplaySubject()
            action = Action(verb)
            fa = action.full_action
            if not fa:
                return None
            data_obj = self.createDataObject(action, fa, dis_subj)
            if data_obj and data_obj not in data_objects:
                data_objects.append(data_obj)
            add_verb = verb
            res = self.getAdditionalDataObject(add_verb, subj)
            if res:
                add_obj, add_verb = res
                for obj in add_obj:
                    if obj not in data_objects:
                        data_objects.append(obj)
        if len(data_objects) > 0:
            return data_objects
        return None

    def getAdditionalDataObject(self, verb, subj):
        # checking if there is another verb linked that does not have a
        # subject dependency - this can be seen as an additional action
        # of the same subject
        add_verb = None
        for child in verb.children:
            if child.dep_ == 'conj' or child.dep_ == 'advcl':
                # print(verb, child)
                n_subj = Subject(child, self.nouns, self.doc, self.coref)
                if not n_subj.subj:
                    add_verb = child
        if not add_verb:
            for child in verb.children:
                if child.dep_ == 'prep':
                    for cchild in child.children:
                        if 'comp' in cchild.dep_ and cchild.pos_ == 'VERB':
                            n_subj = Subject(cchild, self.nouns,
                                             self.doc, self.coref)
                            if not n_subj.subj:
                                add_verb = cchild
        if add_verb:
            return self.getObjectsFromVerb(add_verb, subj)
        return None

    def createDataObject(self, action, fa, dis_subj):
        data_obj = {}
        data_obj['subject'] = dis_subj
        data_obj['action'] = action.getDisplayAction(fa)
        obj = Object(fa, self.nouns, self.coref)
        data_obj['object'] = obj.getDisplayObjects()
        if self.isNamedEntityPresent(dis_subj):
            new_obj = ObjectEditor(data_obj).newObject()
            return new_obj

    def isNamedEntityPresent(self, dis_obj):
        for obj in dis_obj:
            for label in obj.keys():
                if label != 'unknown':
                    return True
        return False

    def getObjectsFromVerb(self, verb, subj):
        data_objects = []
        dis_subj = subj.getDisplaySubject()
        action = Action(verb)
        fa = action.full_action
        if not fa:
            return None
        data_obj = self.createDataObject(action, fa, dis_subj)
        if data_obj:
            data_objects.append(data_obj)
        if len(data_objects) > 0:
            return data_objects, verb
        return None