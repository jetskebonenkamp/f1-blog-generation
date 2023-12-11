def driverAltNames():
    # possible nicknames of all drivers that have driven between
    # 2018 and 2023
    return {
        'VER': ['max', 'verstappen', 'dutchman'],
        'PER': ['sergio', 'checo', 'perez', 'mexican'],
        'HAM': ['lewis', 'hamilton'],
        'SAI': ['carlos', 'sainz'],
        'ALO': ['fernando', 'alonso'],
        'NOR': ['lando', 'norris'],
        'LEC': ['charles', 'leclerc', 'monegasque'],
        'RUS': ['george', 'russell'],
        'PIA': ['oscar', 'piastri'],
        'GAS': ['pierre', 'gasly'],
        'STR': ['lance', 'stroll'],
        'OCO': ['esteban', 'ocon'],
        'ALB': ['alex', 'alexander', 'albon'],
        'BOT': ['valtteri', 'bottas'],
        'HUL': ['nico', 'hulkenberg'],
        'TSU': ['yuki', 'tsunoda'],
        'ZHO': ['zhou', 'guanyu'],
        'MAG': ['kevin', 'magnussen'],
        'LAW': ['liam', 'lawson'],
        'SAR': ['logan', 'sargeant'],
        'RIC': ['daniel', 'ricciardo', 'honey badger'],
        'DEV': ['nyck', 'de vries', 'devries'],
        'RAI': ['kimi', 'raikkonen', 'ice man', 'iceman'],
        'VET': ['sebastian', 'seb', 'vettel'],
        'GRO': ['romain', 'grosjean'],
        'VAN': ['stoffel', 'vandoorne'],
        'ERI': ['marcus', 'ericsson'],
        'HAR': ['brendon', 'hartley'],
        'SIR': ['sergey', 'sirotkin'],
        'MAZ': ['nikita', 'mazepin'],
        'KUB': ['robert', 'kubica'],
        'GIO': ['antonio', 'giovinazzi'],
        'KVY': ['daniil', 'kvyat'],
        'LAT': ['nicolas', 'latifi'],
        'AIT': ['jack', 'aitken'],
        'FIT': ['pietro', 'fittipaldi'],
        'MSC': ['mick', 'schumacher']
    }


def allAltNames():
    all_alts = []
    alt_names = driverAltNames()
    for name_code in alt_names.keys():
        all_alts.append(name_code)
        for alt in alt_names[name_code]:
            all_alts.append(alt)
    return all_alts


def teamNames():
    return ['Bull', 'Ferrari', 'Mercedes', 'Aston', 'Martin',
            'Alpine', 'McLaren', 'Williams', 'Alfa', 'Romeo',
            'Alpha', 'Tauri', 'Haas', 'Scuderia']


def labelPairs():
    driver_names = allAltNames()
    return {'TIMING': ['lap'],
            'POSITION': ['place', 'behind', 'front', 'ahead'],
            'LOCATION': ['turn', 'corner'],
            'MEASURE': ['penalty'],
            'TYRE': ['tyre', 'tyres'],
            'TECH': ['engine', 'gear'],
            'FIA': ['fia', 'stewards', 'race control'],
            'TOOL': ['safety', 'drs'],
            'EVENT': ['race', 'grand', 'prix'],
            'DRIVER': driver_names,
            'TEAM': [t.lower() for t in teamNames()]}