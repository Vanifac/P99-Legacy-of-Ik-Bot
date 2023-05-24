from src.eq_logs.eq_log_event import EQLogEvent


class EQLogEventCorpseTooFar(EQLogEvent):

    def get_triggers(self):
        return [
            'You are too far away to loot',
        ]

    def should_trigger(self, app):
        return True


