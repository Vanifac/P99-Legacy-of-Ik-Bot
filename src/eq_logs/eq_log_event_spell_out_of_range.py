from src.eq_logs.eq_log_event import EQLogEvent


class EQLogEventSpellOutOfRange(EQLogEvent):

    def get_triggers(self):
        return [
            '^Your target is out of range'
        ]

    def should_trigger(self, app):
        return True


