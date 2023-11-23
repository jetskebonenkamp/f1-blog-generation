# expenv
from Identifier import Identifier

import os
import json

data_folder = '../DataExtraction/RaceData/DataSet/'
race_folders = [f for f in os.listdir(data_folder) if 'ipynb' not in f][10:20]

for ri in range(len(race_folders)):
    race_folder = data_folder + race_folders[ri]
    lap_files = [f for f in os.listdir(race_folder) if 'ipynb' not in f]
    for li in range(len(lap_files)):
        action_list = Identifier(ri, li).identifyActions()
        fn = './ExampleEvents/' + race_folders[ri] + '_' + lap_files[li]
        json.dump(action_list, fn)