class Action:
    def __init__(self, verb):
        self.verb = verb
        self.full_action = self.getFullAction()

    def getFullAction(self):
        verb = self.verb
        verb = self.getReplacingVerb(verb)
        if verb.head and verb.head.dep_ == 'mark':
            return None
        actions = [verb]
        opt_deps = ['neg', 'prt', 'prep', 'agent', 'acomp']
        dobj = self.getDirectObject(verb)
        if dobj:
            for child in dobj.children:
                if child.dep_ in opt_deps:
                    actions.append(child)
        for child in verb.children:
            dep = child.dep_
            # check if there is a relevant support token present among
            # the children and insert it before or after, depending on
            # the order of the tokens in the blog
            if dep == 'advmod':
                for cchild in child.children:
                    if cchild.dep_ == 'prep':
                        actions.append(child)
                        actions.append(cchild)
            if dep in opt_deps:
                actions.append(child)
        return actions

    def getDirectObject(self, verb):
        for child in verb.children:
            if child.dep_ == 'dobj':
                return child
        return None

    def getDisplayAction(self, action):
        new_action = [act for act in action if act.dep_ != 'prep']
        new_action = [act for act in new_action if act.dep_ != 'advmod']
        new_action = [act for act in new_action if act.dep_ != 'prt']
        action_string = ' '.join([str(act.lemma_) for act in new_action])
        return action_string

    def getReplacingVerb(self, verb):
        # if there is an open clausal complement among the children of
        # the action, we see this dependent as the main action instead
        for child in verb.children:
            if 'comp' in child.dep_:
                if child.pos_ == 'VERB':
                    return child
                for cchild in child.children:
                    if 'comp' in cchild.dep_ and cchild.pos_ == 'VERB':
                        return cchild
        return verb