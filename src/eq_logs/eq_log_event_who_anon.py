from src.eq_logs.eq_log_event_who import EQLogEventWho


class EQLogEventWhoAnon(EQLogEventWho):

    # [ANONYMOUS] Kaneh
    # [ANONYMOUS] Tappwind  <Vigor>
    def get_triggers(self):
        return [
            '^\[ANONYMOUS\] (\w+)',
        ]

    def get_level(self):
        return None

    def get_class_name(self):
        return None

    def get_character_name(self):
        return self.match.group(1)

    def get_race(self):
        return None


