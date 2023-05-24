from src.eq_logs.eq_log_event import EQLogEvent


class EQLogEventSpellNotRecovered(EQLogEvent):

    def get_triggers(self):
        return [
            '^You haven\'t recovered yet'
        ]

    def should_trigger(self, app):
        return True


