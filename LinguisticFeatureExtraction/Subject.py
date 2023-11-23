from AltNames import driverAltNames, allAltNames, labelPairs


class Subject:
    def __init__(self, verb, nouns, doc, coref):
        self.nouns, self.doc = nouns, doc
        self.coref = coref
        self.alt_names, self.all_alts = driverAltNames(), allAltNames()
        self.subj = self.getSubject(verb)
        # only run below lines if a subject has been found
        if self.subj:
            self.full_subj = self.getFullSubject(self.subj)
            self.full_subj2 = self.additionalSubject()
        else:
            self.full_subj = None
            self.full_subj2 = None

    def getSubject(self, verb):
        # first, we check if there is a direct subject, i.e. a dependent
        # labelled as nominal subject (active or passive)
        for child in verb.children:
            if 'nsubj' in child.dep_:
                return child
        # if there is no direct subject, we check if their is a link to
        # a named entity with label driver that is not the object
        for child in verb.children:
            if child.ent_type_ == 'DRIVER' and 'obj' not in child.dep_:
                return child
        # if there is still no subject found, we take the head of the verb
        # as the subject if this is a named entity with label driver
        if verb.head.dep_ == 'conj':
            for child in verb.head.children:
                if 'nsubj' in child.dep_:
                    return child
        if verb.head.ent_type_ == 'DRIVER':
            return verb.head
        return None

    def getFullSubject(self, subj):
        return [self.linkSubject(subj)]

    def linkSubject(self, subj):
        return self.coref.connectEnt(subj)

    def additionalSubject(self):
        # check if there is a second subject present in the form of
        # a conjunct
        subj = self.subj
        for child in subj.children:
            if child.dep_ == 'conj':
                return self.getFullSubject(child)
        return None

    def subjectList(self):
        # return a list of the subjects present in the blog
        if self.full_subj2:
            return [self.full_subj, self.full_subj2]
        else:
            return [self.full_subj]

    def getDisplaySubject(self):
        new_pairs = []
        # create structured objects from the subjects, where the types
        # are defined using the named entities or, if these are not
        # present, using label rules
        for subj_pair in self.subjectList():
            ent_type = 'unknown'
            sp_strings = [str(subj) for subj in subj_pair]
            subj_name = ' '.join(sp_strings)
            for subj in subj_pair:
                subj_et = subj.ent_type_
                # get the name code if the entity label is driver
                if subj_et and subj_et == 'DRIVER':
                    ent_type = subj_et
                    for dc in list(self.alt_names.keys()):
                        if subj.text.lower() in self.alt_names[dc]:
                            subj_name = subj_name.replace(subj.text, dc)
                elif subj_et:
                    ent_type = subj_et
                for label, texts in labelPairs().items():
                    cp = self.checkPresence(subj, label, texts)
                    if cp:
                        ent_type = cp
            dis_subj = {ent_type.lower(): subj_name}
            if dis_subj not in new_pairs:
                new_pairs.append(dis_subj)
        return new_pairs

    def checkPresence(self, subj, label, texts):
        for text in texts:
            if text in subj.text:
                return label
        return None