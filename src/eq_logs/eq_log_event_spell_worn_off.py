from src.eq_logs.eq_log_event import EQLogEvent


class EQLogEventSpellWornOff(EQLogEvent):

    def get_triggers(self):
        return [
            '^Your (\w+) spell has worn off'
        ]

    def get_spell_name(self):
        return self.match.group(1)

    def should_trigger(self, app):
        return True


