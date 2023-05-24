from src.eq_logs.eq_log_event import EQLogEvent


class EQLogEventConsiderFail(EQLogEvent):

    def get_triggers(self):
        return [
            '^Consider whom?',
        ]

    def should_trigger(self, app):
        return True


