from AltTerms import alternativeVerbs, randomizeAction


class ObjectEditor:
    def __init__(self, data_obj):
        self.data_obj = data_obj
        self.subject = data_obj['subject']
        self.action = data_obj['action']
        self.object = data_obj['object']

    def mainAction(self):
        alt_acts, main_act = alternativeVerbs(), self.action
        for key in alt_acts:
            if self.action in alt_acts[key]: main_act = key
            tups = [a for a in alt_acts[key] if type(a) == tuple]
            for tup in tups:
                for act in tup[0]:
                    try: main = self.object['main']
                    except KeyError: continue
                    if act in self.action and tup[1] in main:
                        main_act = key
                        self.data_obj = self.__removeFromObj(tup[1])
        # if main_act != self.action: print(main_act, self.action)
        return main_act

    def newObject(self):
        main_act = self.mainAction()
        new_obj = randomizeAction(main_act, self.data_obj)
        return new_obj

    def __removeFromObj(self, elem):
        try:
            new_do = self.data_obj
            new_do['object']['main'].remove(elem)
            if len(new_do['object']['main']) == 0: del new_do['object']['main']
            return new_do
        except KeyError:
            return self.data_obj