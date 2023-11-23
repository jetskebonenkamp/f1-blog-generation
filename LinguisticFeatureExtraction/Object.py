from AltNames import driverAltNames, labelPairs


class Object:
    def __init__(self, full_action, nouns, coref):
        self.full_action = full_action
        self.spec_labels = ['DRIVER', 'TEAM', 'POSITION', 'LOCATION', 'TYRE',
                            'MEASURE', 'TIMING', 'TOOL']
        self.label_pairs = labelPairs()
        self.coref, self.nouns = coref, nouns

    def getMainObject(self, fa):
        m_objs = []
        for action in fa:
            for child in action.children:
                obj = self.getDeeperObject(child)
                if not obj:
                    continue
                et = obj.ent_type_
                if not et:
                    fo = self.getFullObject(obj)
                    m_objs.append(fo)
                elif et and et not in self.spec_labels:
                    fo = self.getFullObject(obj)
                    m_objs.append(fo)
            if len(m_objs) == 0:
                for child in action.children:
                    if child.dep_ == 'advmod':
                        fo = self.getFullObject(child)
                        m_objs.append(fo)
        if len(m_objs) == 0:
            return None
        return m_objs

    def getDeeperObject(self, child):
        obj_deps = ['pobj', 'dobj', 'attr']
        add_deps = ['advmod', 'prep']
        obj = None
        if child.dep_ in obj_deps:
            obj = child
        elif child.dep_ in add_deps:
            for cchild in child.children:
                if cchild.dep_ in obj_deps:
                    obj = cchild
                elif cchild.dep_ in add_deps:
                    for ccchild in cchild.children:
                        if ccchild.dep_ in obj_deps:
                            obj = ccchild
        return obj

    def getSpecificObject(self, fa, label):
        s_objs = []
        for action in fa:
            for child in action.children:
                obj = self.getDeeperObject(child)
                if not obj:
                    continue
                et = obj.ent_type_
                if et and et == label:
                    fo = self.getFullObject(obj)
                    s_objs.append(fo)
                elif obj.text in self.label_pairs[label]:
                    fo = self.getFullObject(obj)
                    s_objs.append(fo)
        if len(s_objs) == 0:
            return None
        return s_objs

    def getObjects(self):
        full_action = self.full_action
        objects = {}
        objects['main'] = self.getMainObject(full_action)
        for label in self.spec_labels:
            objects[label.lower()] = self.getSpecificObject(full_action, label)
        return objects

    def getDisplayObjects(self):
        objects = self.getObjects()
        dis_objs = {}
        for key in objects.keys():
            if objects[key]:
                if key not in dis_objs.keys():
                    dis_objs[key] = []
                new_label = None
                for obj_list in objects[key]:
                    dis_objs = self.updateDisplayObjects(
                        key, obj_list, dis_objs, new_label)
                if len(dis_objs[key]) == 0:
                    del dis_objs[key]
        return dis_objs

    def updateDisplayObjects(self, key, obj_list, dis_objs, new_label):
        str_objs = [str(obj) for obj in obj_list]
        obj_str = ' '.join(str_objs)
        new_label = self.changeLabel(obj_list)
        obj_str_nw = self.getAltName(obj_list, obj_str)
        if obj_str != obj_str_nw:
            obj_str = obj_str_nw
            new_label = 'driver'
        if new_label and new_label in dis_objs.keys():
            if obj_str not in dis_objs[new_label]:
                dis_objs[new_label].append(obj_str)
        elif new_label:
            dis_objs[new_label] = []
            dis_objs[new_label].append(obj_str)
        elif obj_str not in dis_objs[key]:
            dis_objs[key].append(obj_str)
        return dis_objs

    def changeLabel(self, obj_list):
        label_pairs, new_label = labelPairs(), None
        for lp_key in label_pairs.keys():
            if lp_key not in self.spec_labels:
                continue
            for obj in obj_list:
                if obj.text.lower() in label_pairs[lp_key]:
                    new_label = lp_key.lower()
        return new_label

    def getAltName(self, obj_list, obj_str):
        alt_names = driverAltNames()
        for driver_key in alt_names.keys():
            for obj in obj_list:
                if obj.text.lower() in alt_names[driver_key]:
                    # if the object is a driver, we consider their modifiers
                    # as irrelevant and therefore exclude them in the string
                    for child in obj.children:
                        if 'mod' in child.dep_:
                            obj_str = obj_str.replace(' ' + child.text, '')
                    obj_str = obj_str.replace(obj.text, driver_key)
        return obj_str

    def getFullObject(self, obj):
        linked_obj = self.linkObject(obj)
        if linked_obj and linked_obj != obj:
            # print(obj, linked_obj)
            obj = linked_obj
        full_obj = [obj]
        if obj.head and obj.head.pos_ == 'ADP':
            full_obj.insert(0, obj.head)
        return self.combineObject(obj, full_obj)

    def linkObject(self, obj):
        return self.coref.connectEnt(obj)

    def combineObject(self, obj, full_obj):
        child_objs = []
        for child in obj.children:
            if 'mod' in child.dep_ or child.dep_ == 'compound':
                obj_i = 0
                for token in full_obj:
                    if child.i > token.i:
                        obj_i = full_obj.index(token) + 1
                child_objs.append(child)
                full_obj.insert(obj_i, child)
            elif child.dep_ == 'relcl':
                full_obj, child_objs = self.getRelcl(
                    child, full_obj, child_objs)
            elif child.dep_ == 'poss':
                full_obj, child_objs = self.getPoss(
                    child, full_obj, child_objs, obj)
        for child in child_objs:
            full_obj = self.combineObject(child, full_obj)
        return full_obj

    def getRelcl(self, child, full_obj, child_objs):
        obj_i = 0
        auxs = [tok for tok in child.children if tok.dep_ == 'aux']
        for token in full_obj:
            if child.i > token.i:
                obj_i = full_obj.index(token) + 1
        child_objs.append(child)
        full_obj.insert(obj_i, child)
        if len(auxs) > 0:
            aux = auxs[0]
            for token in full_obj:
                if aux.i > token.i:
                    aux_i = full_obj.index(token) + 1
            child_objs.append(aux)
            full_obj.insert(aux_i, aux)
        return full_obj, child_objs

    def getPoss(self, child, full_obj, child_objs, obj):
        for cchild in child.children:
            if cchild.dep_ == 'case':
                child_objs.append(child)
                obj_i = full_obj.index(obj)
                full_obj.insert(obj_i, cchild)
                full_obj.insert(obj_i, child)
        return full_obj, child_objs

    def sortObjects(self, objects):
        obj_dict = {}
        for obj_pair in objects:
            obj_i = obj_pair[0].i
            obj_dict[obj_i] = obj_pair
        keys = list(obj_dict.keys())
        keys.sort()
        sorted_obj_dict = {i: obj_dict[i] for i in keys}
        return list(sorted_obj_dict.values())