import importlib
import inspect
import json
import os
import re


class EQLogParser:

    def __init__(self):
        self.events = []

        log_events_to_ignore = [
            "EQLogEvent",
            # "EQLogEventConsider",
        ]

        # Add all classes in this directory that filename start with eq_log_event to the self.events list
        for filename in os.listdir(os.path.dirname(__file__)):
            if filename.startswith("eq_log_event") and filename.endswith(".py"):
                # import the module
                module = importlib.import_module("src.eq_logs." + filename[:-3])
                # get the class
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and name.startswith("EQLogEvent") and name not in log_events_to_ignore:
                        self.events.append(obj())

    # regex match?
    def try_create_event_for_line_raw(self, line):
        # cut off the leading date-time stamp info
        trunc_line = line[27:]

        return self.try_create_event_for_line(trunc_line)

    # regex match?
    def try_create_event_for_line(self, trunc_line):
        # walk thru the target list and trigger list and see if we have any match
        for new_event in self.events:
            triggers = new_event.get_triggers()
            for trigger in triggers:
                if 'proven yourself a skilled monk' in trigger:
                    print("trying")
                match = re.match(trigger, trunc_line)
                if match:
                    return new_event.set_parsed_data(trunc_line, match)

        # only executes if loops did not return already
        return None

    def parse(self, line):
        new_event = self.try_create_event_for_line_raw(line)

        if line:
            return new_event

        return None
