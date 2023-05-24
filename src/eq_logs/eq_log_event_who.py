from src.eq_logs.eq_log_event import EQLogEvent


class EQLogEventWho(EQLogEvent):

    # [1 Warrior] Tomtomtom (Halfling)
    def get_triggers(self):
        return [
            '^\[(\d+) ([\w\s]+)\] (\w+) \((\w+)\)',
        ]

    def should_trigger(self, app):
        return True

    def get_level(self):
        return int(self.match.group(1))

    def get_class_name(self):
        return self.match.group(2)

    def get_character_name(self):
        return self.match.group(3)

    def get_race(self):
        return self.match.group(4)


