class Ranking:
    def __init__(self, data_list):
        self.dl = data_list

    def rankArray(self, lap_i):
        stats = self.dl[lap_i]['stats']
        drivers = list(stats.keys())
        return {i + 1: drivers[i] for i in range(len(stats))}

    def forDriver(self, lap_i, driver):
        stats = self.dl[lap_i]['stats']
        return list(stats.keys()).index(driver) + 1


class Intervals:
    def __init__(self, data_list):
        self.dl = data_list

    def perDriver(self):
        return [{d: self.__ivsForDriver(d)} for d in self.dl[0]['stats'].keys()]

    def forDriver(self, driver):
        return self.__ivsForDriver(driver)

    def __ivsForDriver(self, driver):
        return [d['stats'][driver]['interval'] for d in self.dl]