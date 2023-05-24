from src.eq_logs.eq_log_event import EQLogEvent


class EQLogEventDeath(EQLogEvent):

    def get_triggers(self):
        return [
            '^You have been slain by ([\w\s]+)!',
            'You died.',
        ]

    def get_killer_name(self):
        try:
            return self.match.group(1)
        except Exception as e:
            return ""

    def should_trigger(self, app):
        return True


