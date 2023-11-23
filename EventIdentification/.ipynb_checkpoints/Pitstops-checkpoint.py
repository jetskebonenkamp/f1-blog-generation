import numpy as np

from LapTimes import LapTimes


class Pitstops:
    def __init__(self, data_list):
        self.dl = data_list
        self.sl = [d['stats'] for d in self.dl]
        self.drivers = self.sl[0].keys()

    def lapsPitted(self):
        # stats_list = [d['stats'] for d in self.dl]
        prev_nr, pitstops = 0, {d: [] for d in self.drivers}
        for d in self.drivers:
            for s in self.sl:
                lap_i = self.sl.index(s)
                if s[d]['nr_pitstops'] != prev_nr:
                    if lap_i != 0: pitstops[d].append(lap_i)
                    prev_nr = s[d]['nr_pitstops']
        return pitstops

    def pitTimes(self):
        pit_times = {d: [] for d in self.drivers}
        for d in self.drivers:
            laps_pitted = self.lapsPitted()[d]
            lap_times = LapTimes(self.dl).forDriver(d)
            for lap in laps_pitted:
                try: pit_times[d].append(lap_times[lap])
                except IndexError: continue
        return pit_times

    def pitStats(self):
        pit_times, ps_list = self.pitTimes(), []
        for d in pit_times: ps_list += pit_times[d]
        ps_arr = np.array(ps_list)
        return {'mean': np.mean(ps_arr), 'std': np.std(ps_arr)}

    def driverMadeStop(self, driver, lap):
        lp = self.lapsPitted()[driver]
        if lap in lp: return True
        return False

    def pitTimeForDriverInLap(self, driver, lap):
        return LapTimes(self.dl).forDriver(driver)[lap]