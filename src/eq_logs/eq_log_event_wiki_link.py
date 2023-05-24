from src.eq_logs.eq_log_event import EQLogEvent


class EQLogEventWikiLink(EQLogEvent):

    def get_triggers(self):
        return []

    def get_wiki_link(self):
        return f"http://wiki.project1999.com/{self.get_item_name().replace(' ', '_')}"

    def get_item_name(self):
        return ""


