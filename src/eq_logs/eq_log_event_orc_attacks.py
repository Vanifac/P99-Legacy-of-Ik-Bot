from src.eq_logs.eq_log_event import EQLogEvent


class EQLogEventOrcAttacks(EQLogEvent):
    # 00:05:36 [Thread-11] INFO: [Mon Mar 20 00:05:35 2023] orc centurion says 'Death!! Death to all who oppose the Crushbone orcs!!'

    def get_triggers(self):
        return [
            'orc centurion says',
            'orc pawn says',
        ]

    def should_trigger(self, app):
        return True


