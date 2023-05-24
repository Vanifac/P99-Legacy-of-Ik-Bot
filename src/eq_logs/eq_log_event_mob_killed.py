from src.eq_logs.eq_log_event import EQLogEvent


class EQLogEventMobKilled(EQLogEvent):

    def get_triggers(self):
        return [
            '^You have slain'
        ]

    def should_trigger(self, app):
        return True


