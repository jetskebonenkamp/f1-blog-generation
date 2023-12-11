import re
import spacy
import random
import json
import numpy as np


class RaceControl:
    def __init__(self, race, lap):
        self.rc_objs = self.__rcData(race, lap)
        self.lap_i, self.nlp = lap, spacy.load('en_core_web_sm')

    def __rcData(self, race, lap):
        file = '../DataExtraction/RaceData/LiveTiming_Data/' + race
        # + '.json'
        with open(file, 'r') as f: return json.load(f)[str(lap)]

    def messages(self):
        msgs = []
        # ce, sc = self.carEvents(), self.safetyCar()
        ps, ot = self.penalty(), self.offTrack()
        # if ce: [msgs.append(c) for c in ce]
        # if sc: [msgs.append(s) for s in sc]
        if ps: [msgs.append(p) for p in ps]
        if ot: [msgs.append(o) for o in ot]
        if len(msgs) > 0: return msgs
        fs, ic = self.flagsWaved(), self.incident()
        if fs: [msgs.append(f) for f in fs]
        if ic: [msgs.append(i) for i in ic]
        if len(msgs) > 0: return msgs
        om = self.otherMessage()
        if om: [msgs.append(o) for o in om]
        if len(msgs) > 0: return msgs
        rs = random.choice([True, None, None])
        if not rs: return None
        bf, tl = self.blueFlagsWaved(), self.trackLimits()
        if bf: [msgs.append(b) for b in bf]
        elif tl: [msgs.append(t) for t in tl]
        if len(msgs) > 0: return msgs

    def driverNumbers(self):
        d_info = self.dl[self.lap_i]['driver_info']
        return {d_info[d]['number']: d for d in d_info.keys()}

    def __driverInMsg(self, msg):
        ds = [d[1:-1] for d in re.findall('\([A-Z]{3}\)', msg)]
        if len(ds) > 0: return ds[0]

    def __locationInMsg(self, msg):
        loc = [l.lower() for l in re.findall('TURN \d+|SECTOR \d+', msg)]
        if len(loc) > 0: return loc[0]

    def __lapTimeInMsg(self, msg):
        lt = [t.lower() for t in re.findall('\d\:\d{2}\.\d{3}', msg)]
        if len(lt) > 0: return lt[0]

    def __actionInMsg(self, msg):
        doc = self.nlp(msg)
        act = [t for t in doc if t.pos_ == 'VERB']
        if len(act) > 0: act = act[0]
        else: return None
        dobj = [c for c in act.children if c.dep_ == 'dobj']
        if len(dobj) > 0: dobj = dobj[0]
        else: return None
        return act.lemma_.lower(), dobj.text.lower()

    def __timingInMsg(self, msg):
        tmg = [t for t in re.findall('\d{2}\:\d{2}:\d{2}', msg)]
        if len(tmg) > 0: return tmg[0]

    def __timeDelInMsg(self, msg):
        td = [t for t in re.findall('TIME \d{1}\:\d{2}\.\d{3} DELETED', msg)]
        if len(td) > 0: return True

    def __lapInMsg(self, msg):
        lap = [v.lower() for v in re.findall('LAP \d{1, 2}', msg)]
        if len(lap) > 0: return lap[0]

    def __incidentInMsg(self, msg):
        if 'incident' in msg.lower(): return True

    def otherMessage(self):
        o_msgs = [m for m in self.rc_objs if m['category'] == 'Other']
        o_msgs = [m for m in o_msgs if not self.__incidentInMsg(m['message'])]
        o_msgs = [m for m in o_msgs if not self.__timeDelInMsg(m['message'])]
        msg_objs, p_subjs, p_acts = [], [], []
        for m in o_msgs:
            msg, cause = m['message'], None
            if ' - ' in msg: msg, cause = msg.split(' - ')
            doc, act, subj, obj = self.nlp(msg), None, None, []
            acts = [t for t in doc if t.pos_ == 'VERB']
            if len(acts) == 0: continue
            elif len(acts) == 1: act = acts[0]
            elif len(acts) > 1:
                try: act = [a for a in acts if a.dep_ == 'ROOT'][0]
                except IndexError: continue
            for c in act.children:
                if 'subj' in c.dep_: subj = c
                if 'prep' in c.dep_: obj += [c]
                if 'obj' in c.dep_ or 'mod' in c.dep_: obj += [c]
            if not subj or not act or len(obj) == 0:
                act = random.choice(['mention', 'state', 'say'])
                mo = {'subject': [{'other': 'FIA'}], 'action': act,
                      'object': {'main': [msg.lower()]}}
                if mo not in msg_objs: msg_objs.append(mo)
            elif subj and act:
                msg_objs, p_subjs, p_acts = self.__otherEventObject(
                    [subj, act, obj, msg_objs, p_subjs, p_acts, msg, cause])
        if len(msg_objs) > 0: return msg_objs

    def __otherEventObject(self, data):
        subj, act, obj, msg_objs, p_subjs, p_acts, msg, cause = data
        fs, fa = [subj], [act]
        for c in subj.children:
            if c.dep_ == 'compound': fs.insert(-1, c)
        fs = ' '.join([s.text.lower() for s in fs])
        fa = [act]
        for c in act.children:
            if 'aux' in c.dep_: fa.insert(-1, c)
        fa = ' '.join([a.text.lower() for a in fa])
        sub_cat, loc = 'other', self.__locationInMsg(msg)
        if self.__driverInMsg(msg) == subj: sub_cat = 'driver'
        act = act.text.lower()
        mo = {'subject': [{sub_cat: fs}], 'action': act, 'object': {}}
        if len(obj) > 0:
            cs = [(o, o.i) for o in obj]
            for o in obj: cs += [(c, c.i) for c in o.children]
            for o in cs: cs += [(c, c.i) for c in o[0].children]
            cs = [c for c in cs if 'obj' in c[0].dep_ or 'mod' in c[0].dep_]
            cs = sorted(cs, key=lambda x: x[1])
            n_obj = list(np.unique([o[0] for o in cs]))
            fo = ' '.join([o.text.lower() for o in n_obj])
            mo['object']['main'] = [fo]
        if loc and loc not in obj: mo['object']['location'] = loc
        if cause: mo['object']['info'] = [cause.lower()]
        if fs in p_subjs and act in p_acts:
            del msg_objs[p_subjs.index(fs)]
        msg_objs.append(mo), p_subjs.append(fs), p_acts.append(act)
        return msg_objs, p_subjs, p_acts

    def otherMessageOld(self):
        o_msgs = [m for m in self.rc_objs if m['category'] == 'Other']
        o_msgs = [m for m in o_msgs if not self.__incidentInMsg(m['message'])]
        o_msgs = [m for m in o_msgs if not self.__timeDelInMsg(m['message'])]
        o_objs = []
        for o in o_msgs:
            o_obj = None
            if 'penalty' in o['message'].lower(): o_obj = self.penalty()
            if o_obj:
                o_objs += o_obj
                continue
            msg = o['message']
            loc = self.__locationInMsg(msg)
            o_obj = self.__otherMessageObject(msg.split(' in')[0], loc)
            o_objs.append(o_obj)
        if len(o_objs) > 0: return o_objs

    def __otherMessageObject(self, main, loc=None):
        obj = {'main': [main.lower()]}
        act = random.choice(['mention', 'note',
                             'indicate', 'communicate'])
        if loc: obj['location'] = [loc]
        subj = random.choice(['race control', 'stewards', 'fia'])
        return {'subject': [{'other': subj}],
                'action': act, 'object': obj}

    def flagsWaved(self):
        flag_msgs = [m for m in self.rc_objs if m['category'] == 'Flag']
        if len(flag_msgs) == 0: return None
        flag_objs = []
        for fm in flag_msgs:
            if fm['flag'] == 'BLUE' or fm['flag'] == 'GREEN': continue
            if fm['flag'] == 'CHEQUERED': continue  # return self.raceEnded()
            main_obj = fm['flag'].lower() + ' flag'
            loc = self.__locationInMsg(fm['message'])
            if fm['flag'] == 'CLEAR': 
                # flag_objs.append(self.__trackClearObject(loc))
                continue
            subj = random.choice(['race control', 'stewards', 'fia'])
            flag_obj = {'subject': [{'other': subj}],
                        'action': 'wave',
                        'object': {'main': [main_obj]}}
            if loc: flag_obj['object']['location'] = [loc]
            flag_objs.append(flag_obj)
        if len(flag_objs) > 0: return flag_objs
        for fm in flag_msgs:
            if fm['flag'] == 'CLEAR':
                flag_objs.append(self.__trackClearObject(loc))
                return flag_objs

    def __trackClearObject(self, loc=None):
        obj = {'main': ['clear']}
        if loc: obj['location'] = [loc]
        return {'subject': [{'other': 'track'}],
                'action': 'be',
                'object': obj}

    def blueFlagsWaved(self):
        flag_msgs = [m for m in self.rc_objs if m['category'] == 'Flag']
        if len(flag_msgs) == 0: return None
        flag_objs = []
        for fm in flag_msgs:
            if fm['flag'] != 'BLUE': continue
            msg = fm['message']
            d, tmg = self.__driverInMsg(msg), self.__timingInMsg(msg)
            if not d: continue
            flag_obj = {'subject': [{'driver': d}],
                        'action': 'get', 'object': {'main': ['blue flag']}}
            flag_obj['subject'] = [{'driver': d}]
            if tmg: flag_obj['object']['timing'].append(tmg)
            flag_objs.append(flag_obj)
        if len(flag_objs) > 0: return flag_objs

    def carEvents(self):
        ce_objs = [m for m in self.rc_objs if m['category'] == 'carevent']
        if len(ce_objs) == 0: return None
        data_objs = []
        for cm in ce_objs:
            msg, msg_obj = cm['message'], {}
            act, loc = self.__actionInMsg(msg), self.__locationInMsg(msg)
            d = self.__driverInMsg(msg)
            if d: msg_obj['subject'] = [{'driver': d}]
            if act: msg_obj['action'], msg_obj['object'] = act[0], {'main': [act[1]]}
            else: msg_obj['action'], msg_obj['object'] = 'unknown', {'main': ['unknown']}
            if loc: msg_obj['object']['location'] = [loc]
            if msg_obj != {}: data_objs.append(msg_obj)
        if len(data_objs) > 0: return data_objs
        
    def offTrack(self):
        ot_objs = [m for m in self.rc_objs if 'off track' in m['message'].lower()]
        if len(ot_objs) == 0: return None
        data_objs = []
        for om in ot_objs:
            d = self.__driverInMsg(om['message'])
            loc = self.__locationInMsg(om['message'])
            if not d: continue
            d_obj = {'subject': [{'driver': d}],
                     'action': 'go', 'object':
                     {'main': ['off track']}}
            if loc: d_obj['object']['location'] = [loc]
            data_objs.append(d_obj)
            if 'continue' in om['message'].lower():
                data_objs += [{'subject': [{'driver': d}],
                               'action': 'continue', 'object': {}}]
        if len(data_objs) > 0: return data_objs
        

    def penalty(self):
        p_objs = [m for m in self.rc_objs if 'penalty' in m['message'].lower()]
        if len(p_objs) == 0: return None
        # print(p_objs)
        data_objs = []
        for pm in p_objs:
            msg, msg_obj = pm['message'], {}
            d = self.__driverInMsg(msg)
            if d: msg_obj['subject'] = [{'driver': d}]
            msg_obj['action'], doc = 'get', self.nlp(msg)
            for token in doc:
                msg_obj['object'] = {'main': ['penalty']}
                if token.dep_ != 'nummod': continue
                if token.head.text != 'SECOND': continue
                msg_obj['object']['main'].append(token.text + ' seconds')
            cause = msg.split('-')[-1][1:].lower()
            if cause != '' and 'object' in msg_obj.keys():
                msg_obj['object']['main'].append(cause)
            elif cause != '': msg_obj['object'] = {'main': [cause]}
            if msg_obj != {}: data_objs.append(msg_obj)
        if len(data_objs) > 0: return data_objs

    def trackLimits(self):
        ld_objs = [m for m in self.rc_objs if self.__timeDelInMsg(m['message'])]
        if len(ld_objs) == 0: return None
        data_objs = []
        for lm in ld_objs:
            msg, msg_obj = lm['message'], {}
            d = self.__driverInMsg(msg)
            if not d: continue
            msg_obj['subject'] = [{'driver': d}]
            msg_obj['action'] = 'exceed'
            msg_obj['object'] = {'main': ['track limits']}
            lap, loc = self.__lapInMsg(msg), self.__locationInMsg(msg)
            if lap: msg_obj['object']['timing'] = [lap]
            if loc: msg_obj['object']['location'] = [loc]
            if msg_obj != {}: data_objs.append(msg_obj)
        if len(data_objs) > 0: return data_objs

    def incident(self):
        ic_objs = [m for m in self.rc_objs if self.__incidentInMsg(m['message'])]
        if len(ic_objs) == 0: return None
        data_objs = []
        for im in ic_objs:
            msg, act = im['message'], 'note'
            if 'investigate' in msg.lower(): act = 'investigate'
            d1 = self.__driverInMsg(msg)
            if not d1: continue
            driver, subj = [d1], random.choice(['stewards', 'fia'])
            msg_sub = msg.split(d1)[-1]
            d2 = self.__driverInMsg(msg_sub)
            if d2: driver.append(d2)
            msg_obj = {'subject': [{'other': subj}], 'action': act,
                       'object': {'main': ['incident'], 'driver': driver}}
            cause = None
            if ' - ' in msg: cause = msg.split('- ')[-1].lower()
            if cause: msg_obj['object']['info'] = [cause]
            loc = self.__locationInMsg(msg)
            if loc: msg_obj['object']['location'] = [loc]
            if 'after the race' in msg.lower():
                msg_obj['object']['timing'] = ['after race']
            data_objs.append(msg_obj)
        if len(data_objs) > 0: return data_objs
    
    def safetyCar(self):
        sc_objs = []
        sc_msgs = [m for m in self.rc_objs
                   if m['category'].lower() == 'safetycar']
        for sm in sc_msgs:
            sc_obj = self.__safetyCarObject(sm)
            if sc_obj: sc_objs += sc_obj
        if len(sc_objs) > 0: return sc_objs
        
    def __safetyCarObject(self, sc_msg):
        subj = 'safety car'
        if 'virtual' in sc_msg['message'].lower():
            subj = 'virtual ' + subj
        if sc_msg['status'].lower() == 'deployed':
            return [{'subject': [{'other': subj}],
                    'action': 'deploy',
                    'object': {'timing': ['lap ' + str(self.lap_i)]}}]
        elif sc_msg['status'].lower() == 'in this lap':
            return [{'subject': [{'car': subj}],
                     'action': 'will come',
                     'object': {'main': ['in pits'],
                            'timing': ['end of lap']}},
                    {'subject': [{'other': 'race'}],
                     'action': 'restart',
                     'object': {'main': ['soon']}}]
        elif sc_msg['status'].lower() == 'ending':
            return [{'subject': [{'other': subj}],
                    'action': 'end',
                    'object': {'timing': ['this lap']}}]

    def __incidentAction(self, msg):
        p_acts = {'noted': 'note', 'reviewed': 'review',
                  'under investigation': 'investigate'}
        for pa in p_acts.keys():
            if pa in msg.lower(): return p_acts[pa]