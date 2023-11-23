from RaceData import RaceData
from RaceControl import RaceControl
from Actions import Actions
from ExtraStats import Ranking, Intervals
from Pitstops import Pitstops
from LapTimes import LapTimes

import random
import numpy as np


class Identifier:
    def __init__(self, race_i, lap_i):
        self.data = RaceData(race_i).dataList()
        self.rank = Ranking(self.dl)
        self.ps, self.lts = Pitstops(self.dl), LapTimes(self.dl)
        self.drivers = self.dl[0]['stats'].keys()
        self.ivs, self.lap_i = Intervals(self.dl), lap_i

    def identifyActions(self):
        rc = RaceControl(self.dl, self.lap_i)
        acts_obj = Actions(self, rc)
        actions = self.__randomized(acts_obj)
        if actions: return actions
        actions = acts_obj.mainActs()
        if actions: return actions
        actions = acts_obj.subActs()
        if actions: return actions
        actions = acts_obj.subSubActs()
        if actions: return actions
        actions = acts_obj.subSubSubActs()
        if actions: return actions
        return actions
    
    def overtake(self):
        overtakes = []
        c_lap, p_lap = self.lap_i, self.lap_i - 1
        c_ranking, p_ranking = self.rank.rankArray(c_lap), self.rank.rankArray(p_lap)
        for pos in c_ranking.keys():
            c, p = c_ranking[pos], p_ranking[pos]
            if c < p:
                ov = self.__driversOvertakenByDriver(c, c_ranking, p_ranking)
                if ov: overtakes.append(self.__overtakeObject(c, ov, pos))
        if len(overtakes) > 0: return overtakes
        return None

    def __driversOvertakenByDriver(self, d, c_r, p_r):
        c_pos = [pos for pos in c_r.keys() if c_r[pos] == d][0]
        p_pos = [pos for pos in p_r.keys() if p_r[pos] == d][0]
        d_overtaken, rank_drivers = [], list(c_r.values())
        if c_pos < p_pos:
            for p in range(p_pos-1, c_pos+1):
                d_name = rank_drivers[p]
                if not self.ps.driverMadeStop(d_name, self.lap_i):
                    d_overtaken.append(d_name)
        if len(d_overtaken) > 0: return d_overtaken
        return None

    def __overtakeObject(self, d1, d2, pos):
        return {'subject': [{'driver': d1}],
                'action': 'overtake',
                'object': {
                    'driver': d2,
                    'position': [str(pos)]
                }}

    def driverOut(self, d_name=None):
        drivers_out = []
        lp, names_out = self.ps.lapsPitted(), []
        for d in self.drivers:
            if self.lap_i in lp[d]:
                lt = self.ps.pitTimeForDriverInLap(d, self.lap_i)
                if lt == 0:
                    drivers_out.append(self.__driverOutObject(d))
                    names_out.append(d)
        if d_name and d_name in names_out: return True
        if len(drivers_out) > 0: return drivers_out
        return None

    def __driverOutObject(self, d):
        return {'subject': [{'driver': d}],
                'action': 'retire',
                'object': {
                    'timing': ['lap ' + str(self.lap_i)]
                }}

    def pitstop(self):
        ps_made, ps_stats = [], self.ps.pitStats()
        ps_mean, ps_std, thres = ps_stats['mean'], ps_stats['std'], 1
        for d in self.drivers:
            if self.ps.driverMadeStop(d, self.lap_i):
                # if the driver retired, the pitstop does not count
                if self.driverOut(d): continue
                lt = self.ps.pitTimeForDriverInLap(d, self.lap_i)
                z = (lt - ps_mean) / ps_std
                if z > thres and lt < ps_mean:
                    ps_made.append(self.__pitObject(d, lt, 'fast'))
                elif z > thres and lt > ps_mean:
                    ps_made.append(self.__pitObject(d, lt, 'slow'))
                else: ps_made.append(self.__pitObject(d, lt))
        if len(ps_made) > 0: return ps_made

    def __pitObject(self, d, lt, x=None):
        add_opts = [None, ('timing', ['lap ' + str(self.lap_i)]),
                    ('lap_time', [str(lt)]), None, None]
        pit_obj = {'subject': [{'driver': d}],
                   'action': 'pitstop',
                   'object': {}}
        if x: pit_obj['object']['main'] = [x]
        add_opt = random.choice(add_opts)
        if add_opt: pit_obj['object'][add_opt[0]] = add_opt[1]
        return pit_obj

    def rcMessage(self):
        rc = RaceControl(self.dl, self.lap_i)
        ce, messages = rc.carEvents(), []
        if ce: messages.append(ce)
        if len(messages) > 0: return messages

    def __rcObject(self, msg):
        return {'subject': [{'organisation': 'race control'}],
                'action': 'note',
                'object': {
                    'message': [msg.lower()]
                }}

    def outlier(self):
        thres, i = 1, self.lap_i
        lts, lt_vals, outliers = self.lts.forLap(i), {}, []
        for d in lts.keys():
            if not self.ps.driverMadeStop(d, i) and lts[d] != 0:
                lt_vals[d] = lts[d]
        lt_arr = [lt_vals[d] for d in lt_vals.keys()]
        lap_stats = self.lts.lapStats(np.array(lt_arr))
        mean, std = lap_stats['mean'], lap_stats['std']
        for d in lt_vals.keys():
            z = (lts[d] - mean) / std
            if z > thres and lts[d] < mean:
                outliers.append(self.__outlierObject(
                    d, lts[d], 'fast', mean - lts[d]))
            elif z > thres and lts[d] > mean:
                outliers.append(self.__outlierObject(
                    d, lts[d], 'slow', lts[d] - mean))
        if len(outliers) > 0: return outliers

    def __outlierObject(self, d, lt, info, diff):
        return {'subject': [{'driver': d}],
                'action': 'drive',
                'object': {
                    'main': [str(diff) + 's ' + info + 'er',
                             'than rest', 'on average'],
                    'timing': ['lap ' + str(self.lap_i)],
                    'lap_time': [str(lt)]
                }}

    def novelty(self):
        thres, i, novs = 1, self.lap_i, []
        for d in self.drivers:
            lt_fd = self.lts.forDriver(d)
            if self.ps.driverMadeStop(d, i): continue
            prev_lts, cur_lt = lt_fd[:i], lt_fd[i]
            if len(prev_lts) == 1: continue
            lap_stats = self.lts.lapStats(np.array(prev_lts))
            mean, std = lap_stats['mean'], lap_stats['std']
            z = (cur_lt - mean) / std
            if z > thres and cur_lt < mean:
                novs.append(self.__noveltyObject(
                    d, cur_lt, 'fast', np.max(prev_lts) - cur_lt))
            elif z > thres and cur_lt > mean:
                novs.append(self.__noveltyObject(
                    d, cur_lt, 'slow', cur_lt - mean))
        if len(novs) > 0: return novs

    def __noveltyObject(self, d, lt, info, diff):
        if info == 'slow':
            main = 'a bit'
            if diff > 4: main = 'massively'
            return {'subject': [{'driver': d}],
                    'action': 'slow down',
                    'object': {
                        'main': main,
                        'lap_time': [str(lt)]
                    }}
        elif info == 'fast':
            return {'subject': [{'driver': d}],
                    'action': 'pick up',
                    'object': {
                        'main': ['pace'],
                        'lap_time': [str(lt), str(diff) + ' faster than before']
                    }}

    def drsZone(self, i=None, itr=False):
        if not i: i = self.lap_i
        prev_d, in_zone = None, []
        for d in self.drivers:
            if not prev_d:
                prev_d = d
                continue
            iv = self.ivs.forDriver(d)[i]
            if iv == 0: continue
            if iv < 1 and itr: return True
            if iv < 1 and self.drsZone(i - 1, True):
                pos = self.rank.forDriver(i, d)
                in_zone.append(self.__drsObject(d, prev_d, iv, pos))
            prev_d = d
        if len(in_zone) > 0: return in_zone

    def __drsObject(self, d, prev_d, iv, pos):
        return {'subject': [{'driver': d}],
                'action': 'drs',
                'object': {
                    # 'main': ['in drs zone'],
                    'driver': [prev_d],
                    'position': [str(pos)],
                    'gap': [str(iv)]
                }}

    def approaching(self, i=None, itr=False):
        if not i: i = self.lap_i
        prev_d, appr = None, []
        for d in self.drivers:
            if not prev_d:
                prev_d = d
                continue
            iv = self.ivs.forDriver(d)[i]
            if iv == 0 or iv >= 5: continue
            lt_c = self.lts.forDriver(d)[i]
            lt_p = self.lts.forDriver(prev_d)[i]
            diff = lt_p - lt_c
            if diff > 0.5 and itr: return True
            if diff > 0.5 and not self.approaching(i - 1):
                pos = self.rank.forDriver(i, d) - 1
                appr.append(self.__appObject(d, prev_d, iv, diff, pos))
            prev_d = d
        if len(appr) > 0: return appr

    def __appObject(self, d, prev_d, iv, diff, pos):
        return {'subject': [{'driver': d}],
                'action': 'approach',
                'object': {
                    'main': ['by ' + str(diff), 'per lap'],
                    'driver': [prev_d],
                    'position': [str(pos)],
                    'gap': [str(iv)]
                }}

    def __randomized(self, acts_obj):
        r_ch = random.choice([None, None, None, None, True, None, None])
        if not r_ch: return acts_obj.mainActs()
        i = random.choice([0, 0, 0, 0, 1, 1, 1, 2, 2])
        if i == 0: return acts_obj.subActs()
        elif i == 1: return acts_obj.subSubActs()
        elif i == 2: return acts_obj.subSubSubActs()
