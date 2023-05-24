from src.eq_logs.eq_log_event import EQLogEvent


class EQLogEventConsider(EQLogEvent):

    # INFO: [Mon Mar 20 00:46:14 2023] orc centurion glares at you threateningly -- what would you like your tombstone to say?
    # INFO: [Mon Mar 20 00:45:31 2023] Guard Fireblight looks your way apprehensively -- what would you like your tombstone to say?

    def get_triggers(self):
        return [
            '^([\w\s]+) (judges you amiably|regards you indifferently|glowers at you dubiously|glares|scowls|looks your way apprehensively|regards you as an ally)',
            # '^((\w+|\s)+) (regards you indifferently|glowers at you dubiously|glares|scowls|looks your way apprehensively|regards you as an ally)',
            # This one causes infinite loop
            # '^((?:\w+\s?)+?) (regards you indifferently|glowers at you dubiously|glares|scowls|looks your way apprehensively|regards you as an ally)',
        ]

    def get_target(self):
        return self.match.group(1)

    def get_con_rating(self):
        return self.match.group(2)

    def should_trigger(self, app):
        return True


