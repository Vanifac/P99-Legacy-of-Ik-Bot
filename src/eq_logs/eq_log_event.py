class EQLogEvent:

    def __init__(self):
        self.log_line = None
        self.match = None

    def set_parsed_data(self, trunc_line, match):
        self.log_line = trunc_line
        self.match = match
        return self

    def run(self, app):
        pass

    def get_triggers(self):
        pass
