from src.eq_logs.eq_log_event import EQLogEvent


class EQLogEventWhoEnd(EQLogEvent):

    # There are 10 players in Ocean of Tears.
    def get_triggers(self):
        return [
            '^There are (\d+) players in ([\w\s]+)',
        ]

    def should_trigger(self, app):
        return True

    def get_num_players(self):
        return int(self.match.group(1))

    def get_zone_name(self):
        return self.match.group(2)


