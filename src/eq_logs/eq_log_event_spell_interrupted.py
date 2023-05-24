from src.eq_logs.eq_log_event import EQLogEvent


class EQLogEventSpellInterrupted(EQLogEvent):

    def get_triggers(self):
        return [
            '^Your spell is interrupted'
        ]

    def should_trigger(self, app):
        return True


