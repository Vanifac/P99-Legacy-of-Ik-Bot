from src.eq_logs.eq_log_event import EQLogEvent


class EQLogEventSpellResist(EQLogEvent):

    def get_triggers(self):
        return [
            '^Your target resisted'
        ]

    def should_trigger(self, app):
        return True


