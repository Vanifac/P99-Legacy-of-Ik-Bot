from src.eq_logs.eq_log_event_wiki_link import EQLogEventWikiLink


class EQLogEventMonkShackleRock(EQLogEventWikiLink):

    def get_triggers(self):

        return [
            '.*This is yours. It is one of the keys to the third rung.*'
        ]

    def get_item_name(self):
        return 'Shackle of Rock'
