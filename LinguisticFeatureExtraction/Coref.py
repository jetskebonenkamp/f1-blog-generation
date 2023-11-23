from AltNames import allAltNames

class Coref:
    def __init__(self, fe):
        self.fe = fe
        self.blog = fe.blog

    def getClusters(self):
        clusters = self.fe.doc._.coref_clusters
        text = self.blog
        all_ents = []
        for cluster in clusters:
            ents = []
            try:
                for start_i, end_i in cluster:
                    ents.append(text[start_i:end_i])
                all_ents.append(ents)
            except TypeError:
                print(cluster)
                continue
        return all_ents

    def connectEnt(self, token):
        clusters = self.getClusters()
        tok_cluster, c_tok = None, None
        if token.ent_type_ or token.text in allAltNames():
            return token
        for cluster in clusters:
            for ct in cluster:
                if token.text in ct:
                    tok_cluster, c_tok = cluster, ct
                    break
            if tok_cluster:
                break
        if not tok_cluster:
            return token
        nouns, conn_ent = self.fe.nouns, None
        for ct in tok_cluster:
            for noun in nouns:
                if noun.text in ct and ct != c_tok:
                    et = noun.ent_type_
                    if et and et == 'DRIVER':
                        return noun
                    elif noun.text in allAltNames():
                        return noun
                    elif et:
                        conn_ent = noun
                    elif not conn_ent and noun.pos_ == 'PROPN':
                        conn_ent = noun
        if conn_ent:
            return conn_ent
        return token

    def getConnectedEnt(self, token, nouns):
        clusters = self.getClusters()
        alts = allAltNames()
        for cluster in clusters:
            # if token.text in cluster:
            for ent in cluster:
                if token.text not in ent:
                    continue
                    conn_noun = nouns[-1]
                    et_found = False
                    
                    print(token, cluster)
                    conn_noun = nouns[-1]
                    et_found = False
                    for noun in nouns:
                        if noun.text not in ent:
                            continue
                        et = noun.ent_type_
                        if et and et == 'DRIVER' or noun.text in alts:
                            # print(token, noun)
                            conn_noun = noun
                            break
                        if et:
                            conn_noun = noun
                            et_found = True
                        if noun.pos_ == 'PROPN' and not et_found:
                            conn_noun = noun
                    for tok in self.fe.doc:
                        if tok.text == conn_noun:
                            return tok
                    # return conn_noun
        return token