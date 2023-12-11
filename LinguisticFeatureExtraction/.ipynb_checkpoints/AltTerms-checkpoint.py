import random


def alternativeVerbs():
    return {'overtake': ['overtake', 'pass', 
                         (['breeze', 'fly', 'go', 'move', 'get'], 'past'),
                         (['gain', 'take'], 'position')],
            'approach': ['approach', 'chase', 'catch', (['catch'], 'up')],
            'pitstop': ['pit', (['stop'], 'for tyres'), 'pitstop',
                        (['make', 'do'], 'pitstop'), (['enter'], 'pitlane'),
                        (['come', 'go'], 'in pit'), (['change'], 'tyres')],
            'drs': [(['be'], 'in drs zone'), 'threat', (['take'], 'drs'),
                    (['plan', 'want'], 'overtake'),
                    (['be', 'drive'], 'on tail')],
            'retire': [(['retire'], 'car'), (['is'], 'out of race'),
                       (['do', 'will'], 'not continue'),
                       (['end'], 'his race')],
            'lead': [(['drive', 'run'], 'first'), (['be'], 'in lead'),
                     'lead', (['lead'], 'race'), (['lead'], 'pack'),
                     (['drive', 'be'], 'in front')]
            }


def randomizeAction(action, data_obj):
    av = alternativeVerbs()
    opts = [av[k] for k in av.keys() if action in k]
    if len(opts) == 0: return data_obj
    opt = opts[0]
    rc = random.choice(opt)
    if type(rc) is not tuple:
        data_obj['action'] = rc
        return data_obj
    n_act, m_obj = random.choice(rc[0]), rc[1]
    data_obj['action'] = n_act
    if 'main' in data_obj['object'].keys():
        data_obj['object']['main'].insert(0, m_obj)
        return data_obj
    data_items = list(data_obj['object'].items())
    data_items.insert(0, ('main', [m_obj]))
    data_obj['object'] = dict(data_items)
    return data_obj

