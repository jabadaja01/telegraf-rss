
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from datetime import datetime
import xml.etree.ElementTree as ET
import os

def generate_rss():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://aero.telegraf.rs/najnovije-vesti", timeout=60000)
        page.wait_for_selector("a:has(h2)", timeout=15000)
        links = page.query_selector_all("a:has(h2)")
        items = []

        for link in links[:10]:  # uzimamo prvih 10 vesti
            href = link.get_attribute("href")
            title_element = link.query_selector("h2")
            title = title_element.inner_text().strip() if title_element else "Bez naslova"

            if not href.startswith("http"):
                href = "https://aero.telegraf.rs" + href

            # Otvaranje vesti radi datuma
            article = page.context.new_page()
            article.goto(href)
            html = article.content()
            soup = BeautifulSoup(html, "html.parser")

            # Pronađi meta tag za datum
            meta = soup.find("meta", {"property": "article:published_time"})
            if meta:
                raw_date = meta["content"]
                pub_date = datetime.fromisoformat(raw_date.replace("Z", "+00:00"))
                pub_date_rss = pub_date.strftime("%a, %d %b %Y %H:%M:%S %z")
            else:
                pub_date_rss = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")

            items.append((title, href, pub_date_rss))
            article.close()

        # RSS struktura
        rss = ET.Element("rss", version="2.0")
        channel = ET.SubElement(rss, "channel")
        ET.SubElement(channel, "title").text = "Telegraf Aero - Najnovije vesti"
        ET.SubElement(channel, "link").text = "https://aero.telegraf.rs/najnovije-vesti"
        ET.SubElement(channel, "description").text = "Validne i ažurne vesti sa sajta Telegraf Aero"
        ET.SubElement(channel, "language").text = "sr"

        for title, link, pub_date in items:
            item = ET.SubElement(channel, "item")
            ET.SubElement(item, "title").text = title
            ET.SubElement(item, "link").text = link
            ET.SubElement(item, "description").text = title
            ET.SubElement(item, "pubDate").text = pub_date

        tree = ET.ElementTree(rss)
        tree.write("telegraf_valid_feed.xml", encoding="utf-8", xml_declaration=True)
        print("✅ RSS generisan kao 'telegraf_valid_feed.xml'.")

if __name__ == "__main__":
    generate_rss()
