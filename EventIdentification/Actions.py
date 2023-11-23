from AltTerms import randomizeAction


class Actions:
    def __init__(self, ei, rc):
        self.ei, self.rc = ei, rc

    def mainActs(self):
        actions = []
        overtakes = self.randAct(self.ei.overtake())
        drivers_out = self.randAct(self.ei.driverOut())
        pitstops = self.randAct(self.ei.pitstop())
        flags = self.randAct(self.rc.flagsWaved())
        penalties = self.randAct(self.rc.penalty())
        incidents = self.randAct(self.rc.incident())
        if overtakes: [actions.append(o) for o in overtakes]
        if drivers_out: [actions.append(do) for do in drivers_out]
        if pitstops: [actions.append(ps) for ps in pitstops]
        if flags: [actions.append(f) for f in flags]
        if penalties: [actions.append(pe) for pe in penalties]
        if incidents: [actions.append(i) for i in incidents]
        if len(actions) > 0: return actions

    def subActs(self):
        actions, car_events = [], self.rc.carEvents()
        drs_zones = self.randAct(self.ei.drsZone())
        if car_events: [actions.append(ce) for ce in car_events]
        if drs_zones and self.ei.lap_i > 5: [actions.append(d) for d in drs_zones]
        if len(actions) > 0: return actions

    def subSubActs(self):
        actions, approaching = [], self.ei.approaching()
        outliers, novelties = self.ei.outlier(), self.ei.novelty()
        if outliers: [actions.append(ou) for ou in outliers]
        if novelties: [actions.append(n) for n in novelties]
        elif approaching:
            if self.ei.lap_i > 5: [actions.append(a) for a in approaching]
        if len(actions) > 0: return actions

    def subSubSubActs(self):
        actions, blue_flags = [], self.rc.blueFlagsWaved()
        track_limits = self.rc.trackLimits()
        if blue_flags: [actions.append(bf) for bf in blue_flags]
        if track_limits: [actions.append(tl) for tl in track_limits]
        if len(actions) > 0: return actions

    def randAct(self, data_objs):
        if not data_objs: return None
        return [randomizeAction(do['action'], do) for do in data_objs]