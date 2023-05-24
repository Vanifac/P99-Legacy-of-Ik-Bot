from src.eq_logs.eq_log_event import EQLogEvent


class EQLogEventStartAutomation(EQLogEvent):

    def get_triggers(self):
        return [
            '^starta'
        ]

    def should_trigger(self, app):
        return True


