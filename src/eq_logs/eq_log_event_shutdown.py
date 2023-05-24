from src.eq_logs.eq_log_event import EQLogEvent


class EQLogEventShutdown(EQLogEvent):

    def get_triggers(self):
        return [
            'stop is not online',
        ]

    def should_trigger(self, app):
        return True


