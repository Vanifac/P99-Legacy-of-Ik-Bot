from src.eq_logs.eq_log_event import EQLogEvent


class EQLogEventLoc(EQLogEvent):

    def get_triggers(self):
        return [
            '^Your Location is (-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+)$'
        ]

    def get_loc_x(self):
        loc_val = self.match.group(1)
        # return float value of loc_val
        return float(loc_val)

    def get_loc_y(self):
        loc_val = self.match.group(2)
        # return float value of loc_val
        return float(loc_val)

    def get_loc_z(self):
        loc_val = self.match.group(3)
        # return float value of loc_val
        return float(loc_val)

    def get_loc(self):
        return self.get_loc_x(), self.get_loc_y(), self.get_loc_z()

    def should_trigger(self, app):
        return True


