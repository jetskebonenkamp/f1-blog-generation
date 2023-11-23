import re
import spacy
import random


class RaceControl:
    def __init__(self, data_list, lap_i):
        self.lap_i, self.dl = lap_i, data_list
        self.rc_objs = self.__rcObjects()
        self.dns = self.driverNumbers()
        self.nlp = spacy.load('en_core_web_sm')

    def __rcObjects(self):
        rc_objs, ro_nw = self.dl[self.lap_i]['rc_messages'], []
        for ro in rc_objs: ro_nw.append({k.lower(): v for k, v in ro.items()})
        return ro_nw

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

    def flagsWaved(self):
        flag_msgs = [m for m in self.rc_objs if m['category'] == 'Flag']
        if len(flag_msgs) == 0: return None
        flag_objs = []
        for fm in flag_msgs:
            if fm['flag'] == 'BLUE' or fm['flag'] == 'GREEN': continue
            if fm['flag'] == 'CHEQUERED': return self.raceEnded()
            main_obj = fm['flag'].lower() + ' flag'
            loc = self.__locationInMsg(fm['message'])
            flag_obj = {'subject': [{'organization': 'fia'}],
                        'action': 'wave',
                        'object': {
                            'main': [main_obj],
                        }}
            if loc: flag_obj['object']['location'] = [loc]
        if len(flag_objs) > 0: return flag_objs

    def blueFlagsWaved(self):
        flag_msgs = [m for m in self.msgs if m['category'] == 'Flag']
        if len(flag_msgs) == 0: return None
        flag_objs = []
        for fm in flag_msgs:
            if fm['flag'] != 'BLUE': continue
            msg = fm['message']
            d, tmg = self.__driverInMsg(msg), self.__timingInMsg(msg)
            if not d: continue
            flag_obj = {'subject': [{'driver': d}],
                        'action': 'get',
                        'object': {'main': ['blue flag'],
                                   'timing': ['lap ' + str(self.lap_i)]}}
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

    def penalty(self):
        p_objs = [m for m in self.rc_objs if 'penalty' in m['message'].lower()]
        if len(p_objs) == 0: return None
        data_objs = []
        for pm in p_objs:
            msg, msg_obj = pm['message'], {}
            d = self.__driverInMsg(msg)
            if d: msg_obj['subject'] = [{'driver': d}]
            msg_obj['action'], doc = 'gets', self.nlp(msg)
            for token in doc:
                if token.dep_ != 'nummod': continue
                if token.head.text != 'SECOND': continue
                msg_obj['object'] = {'main': [token.text + ' second time penalty']}
            cause = msg.split('-')[-1][1:].lower()
            if cause != '': msg_obj['object']['main'].append(cause)
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
        print(data_objs)
        if len(data_objs) > 0: return data_objs

    def incident(self):
        ic_objs = [m for m in self.rc_objs if self.__incidentInMsg(m['message'])]
        if len(ic_objs) == 0: return None
        data_objs = []
        for im in ic_objs:
            msg = im['message']
            d1 = self.__driverInMsg(msg)
            if not d1: continue
            msg_sub = msg.split(d1)[-1]
            d2 = self.__driverInMsg(msg_sub)
            if d2:
                msg_objs = self.__duoIncObject(msg, d1, d2)
                for mo in msg_objs: data_objs.append(mo)
            else:
                cause = msg.split('-')[-1][1:].lower()
                if cause != '':
                    msg_objs = self.__monoIncObject(d1, cause)
                    for mo in msg_objs: data_objs.append(mo)
        if len(data_objs) > 0: return data_objs

    def __eventFromMsg(self, msg):
        doc = self.nlp(msg)
        acts = [tok for tok in doc if tok.pos_ == 'VERB']
        if len(acts) == 0: return []
        obj, f_obj, events = None, None, []
        for act in acts:
            for c in act.children:
                if c.pos_ == 'prep':
                    for cc in c.children:
                        obj = cc
                elif 'obj' in c.pos_: obj = c
            if obj:
                for c in obj.children:
                    if c.dep_ == 'compound': f_obj = [c, obj]
                if not f_obj: f_obj = [obj]
                f_obj = ' '.join([o.text for o in f_obj])
                events.append({'action': act.lemma_.text, 'object': f_obj})
        if len(events) > 0: return events

    def __monoIncObject(self, d, cause):
        events, a_objs = self.__eventFromMsg(cause), []
        for e in events:
            act, obj = e['action'], e['object']
            a_objs.append({'subject': [{'driver': d}],
                           'action': act, 'object': {'main': [obj]}})
        if len(a_objs) > 0: return a_objs

    def __duoIncObject(self, msg, d1, d2):
        msg, cause, a_objs = msg.split(' - '), []
        events = self.__eventFromMsg(cause)
        for e in events:
            act, obj = e['action'], e['object']
            a_objs.append({'subject': [{'driver': d1}, {'driver': d2}],
                           'action': act, 'object': {'main': [obj]}})
        ia = self.__incidentAction(msg)
        if ia: a_objs.append({'subject': [{'organization': 'fia'}],
                              'action': ia,
                              'object': {'main': ['incident'],
                                         'driver': [d1, d2]}})
        if len(a_objs) > 0: return a_objs

    def __incidentAction(self, msg):
        p_acts = {'noted': 'note', 'reviewed': 'review',
                  'under investigation': 'investigate'}
        for pa in p_acts.keys():
            if pa in msg.lower(): return p_acts[pa]

    def raceEnded(self, m):
        lap_obj = self.dl[self.lap_i]
        stats, r_info = lap_obj['stats'], lap_obj['race_info']
        winner = [d for d in stats.keys() if stats[d]['position'] == 1]
        if len(winner) > 0: winner = winner[0]
        loc = random.choice('country', 'city')
        return {'subject': [{'driver': winner}],
                'action': 'win',
                'object': {
                    'main': [r_info['race_name']],
                    'location': [r_info[loc]]
                }}