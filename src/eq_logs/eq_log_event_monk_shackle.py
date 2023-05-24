from src.eq_logs.eq_log_event_wiki_link import EQLogEventWikiLink


class EQLogEventMonkShackle(EQLogEventWikiLink):

    def get_triggers(self):

        return [
            # Stackle of clay
            '.*You have proven yourself a skilled monk. You will now wear the ([\w\s]+)..*',
            # Shackle of stone
            '.*You have done supremely.*You have earned your ([\w\s]+)..*',
            # Copper
            '.*Very good!! Here is your ([\w\s]+). The emperor shall be pleased.*',
            # Bronze
            '.*For your deed, I bestow upon you the ([\w\s]+)!.*',
        ]

    def get_item_name(self):
        item_name = self.match.group(1)
        # Capitalize each word
        item_name = item_name.title()
        # Lowercase of
        item_name = item_name.replace("Of", "of")

        return item_name
