from src.eq_logs.eq_log_event import EQLogEvent


class EQLogEventHail(EQLogEvent):

    def get_triggers(self):
        return [
            '^(\w+) say, \'Hail, (\w+)\'',
            '^(\w+) says, \'Hail, (\w+)\'',
        ]

    def get_hailed_name(self):
        return self.match.group(2)

    def get_their_name(self):
        return self.match.group(1)

    def should_trigger(self, app):
        hailed_name = self.match.group(2)
        if hailed_name == app.config.get("eq_char_name"):
            return True

        return False


