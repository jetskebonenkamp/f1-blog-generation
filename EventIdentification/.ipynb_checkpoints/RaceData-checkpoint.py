import sys


sys.path.append('../')


from LinguisticFeatureExtraction.AltNames import driverAltNames
import json
import os


class RaceData:
    def __init__(self, race_i, folder):
        self.i, self.f = race_i, folder

    def dataList(self):
        return [self.__sortedData(self.__replaceNames(d)) for d
                in self.__loadData(self.i)]

    def __replaceNames(self, data):
        stats, alt_names = data['stats'], driverAltNames()
        d_info, n_stats, n_info = data['driver_info'], {}, {}
        for dn in stats.keys():
            orig_dn = dn
            if '_' in dn: dn = dn.split('_')[-1]
            for code in alt_names.keys():
                if dn in alt_names[code]:
                    n_stats[code] = stats[orig_dn]
                    n_info[code] = d_info[orig_dn]
        data['stats'], data['driver_info'] = n_stats, n_info
        return data

    def __sortedData(self, data):
        stats, p = data['stats'], 'position'
        s_stats = {d: s for d, s in sorted(
            stats.items(), key=lambda x: x[1][p]
            if x[1][p] > 0 else float('inf'))}
        data['stats'] = s_stats
        return data

    def __loadData(self, race_i, lap_i=None):
        # folder = '../DataExtraction/RaceData/DataSet'
        race_folders = [f for f in os.listdir(self.f) if 'ipynb' not in f]
        sample_rf = self.f + race_folders[race_i] + '/'
        lap_files = [f for f in os.listdir(sample_rf) if 'ipynb' not in f]
        if lap_i:
            sample_lap = sample_rf + lap_files[lap_i]
            with open(sample_lap, 'r') as f: data = json.load(f)
            return data
        data = []
        for lf in lap_files:
            full_fn = sample_rf + '/' + lf
            with open(full_fn, 'r') as f: data.append(json.load(f))
        return data