from src.eq_logs.eq_log_event import EQLogEvent


class EQLogEventSpellCantSee(EQLogEvent):

    def get_triggers(self):
        return [
            "^You can't see your target from here"
        ]

    def should_trigger(self, app):
        return True


