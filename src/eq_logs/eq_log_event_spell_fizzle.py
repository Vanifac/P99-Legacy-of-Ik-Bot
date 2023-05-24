from src.eq_logs.eq_log_event import EQLogEvent


class EQLogEventSpellFizzle(EQLogEvent):

    def get_triggers(self):
        return [
            '^Your spell fizzles'
        ]

    def should_trigger(self, app):
        return True


