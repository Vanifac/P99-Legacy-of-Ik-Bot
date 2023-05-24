from src.eq_logs.eq_log_event import EQLogEvent


class EQLogEventPCAttacks(EQLogEvent):
    # TODO: Could try to parse the damage done & who did it, but it's tricky
    # Example: A bat bites YOU for 1 point of damage

    def get_triggers(self):
        return [
            '^(\w+) (\w+) ([\w\s]+) for (\d+) points of damage',
        ]

    def get_player_name(self):
        return self.matches.group(1)

    def get_dmg_type(self):
        return self.matches.group(2)

    def get_mob_name(self):
        return self.matches.group(3)

    def get_dmg(self):
        return self.matches.group(4)

    def should_trigger(self, app):
        return True


