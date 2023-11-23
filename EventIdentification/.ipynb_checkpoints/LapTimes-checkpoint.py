import numpy as np


class LapTimes:
    def __init__(self, data_list):
        self.dl = data_list
        self.race, self.lap = self.perDriver(), self.perLap()

    def perDriver(self):
        return [{d: self.__ltsForDriver(d)} for d in self.dl[0]['stats'].keys()]

    def forDriver(self, driver):
        return self.__ltsForDriver(driver)

    def __ltsForDriver(self, driver):
        return [d['stats'][driver]['lap_time'] for d in self.dl]

    def perLap(self):
        return [self.__ltsForLap(d) for d in self.dl]

    def forLap(self, lap):
        return self.perLap()[lap]

    def lapStats(self, lap_arr):
        return {'mean': np.mean(lap_arr), 'std': np.std(lap_arr)}

    def __ltsForLap(self, data):
        stats, lap_times = data['stats'], {}
        for driver in stats.keys():
            lap_times[driver] = stats[driver]['lap_time']
        return lap_times