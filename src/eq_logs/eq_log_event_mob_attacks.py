from src.eq_logs.eq_log_event import EQLogEvent


class EQLogEventMobAttacks(EQLogEvent):
    # TODO: Could try to parse the damage done & who did it, but it's tricky
    # Example: A bat bites YOU for 1 point of damage

    def get_triggers(self):
        return [
            '^([\w\s]+) YOU, but misses',
            '^([\w\s]+) YOU for',
        ]

    def should_trigger(self, app):
        return True


