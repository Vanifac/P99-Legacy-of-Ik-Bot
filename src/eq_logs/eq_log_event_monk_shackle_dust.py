
from src.eq_logs.eq_log_event_wiki_link import EQLogEventWikiLink


class EQLogEventMonkShackleDust(EQLogEventWikiLink):

    def get_triggers(self):

        return [
            '.*Out of nowhere, his tail sweeps forward and places a small shackle upon your wrist.*'
        ]

    def get_item_name(self):
        return 'Shackle of Dust'

    def get_wiki_link(self):
        return "https://wiki.project1999.com/Shackle_of_Dust"


