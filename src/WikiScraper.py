import requests
from bs4 import BeautifulSoup

class WikiScraper:

    def __init__(self):
        self.name = "WikiScraper"

    # only returns item description at the moment, but may try to parse more (ex: image)
    def scrape_wikipage_item(self, url):
        # this requests.get() uses https and complains about not finding a certificate
        #page = requests.get(url)
        
        # this does not use HTTPS so it does not look for certificate
        page = requests.get(url, verify=False)
        soup = BeautifulSoup(page.content, "html.parser")
        
        return self.parse_description(soup)

    # gets the item/weapon description text
    def parse_description(self, page_text):
        results = page_text.find(id="mw-content-text")
        job_elements = results.find("div", class_="itemdata")
        paragraph = job_elements.find("p")
        return paragraph.text

    # gets weapon/item icon img source URL (currently not showing up in embeds)
    def parse_icon(self, page_text):
        results = page_text.find("div", class_="itemicon")
        icon_srcs = results.find("img")
        icon_src = icon_srcs['src']
        return "https://wiki.project1999.com" + icon_src

