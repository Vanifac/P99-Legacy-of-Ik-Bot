from src.eq_logs.eq_log_event_wiki_link import EQLogEventWikiLink


class EQLogEventMonkShackleDust(EQLogEventWikiLink):

    def get_triggers(self):

        return [
            '.*an Iksar slave hands you a shackle and removes the coppernickel shackle so he may flee. He places your shackles on his wrists and darts into the darkness.*'
        ]

    def get_item_name(self):
        return 'Shackle of Steel'


