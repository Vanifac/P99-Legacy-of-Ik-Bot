from src.eq_logs.eq_log_event import EQLogEvent


class EQLogEventPetTrack(EQLogEvent):

    def get_triggers(self):
        return [
            "^(\w+) tells you, 'Attacking ([\w\s]+) Master.'",
        ]

    def get_target(self):
        return self.match.group(2)

    def get_pet_name(self):
        return self.match.group(1)

    def should_trigger(self, app):
        return True


