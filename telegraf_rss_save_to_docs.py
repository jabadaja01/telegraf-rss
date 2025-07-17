import requests
from bs4 import BeautifulSoup
from datetime import datetime
from email.utils import format_datetime
import os
import xml.etree.ElementTree as ET

def generate_rss():
    base_url = "https://aero.telegraf.rs"
    news_url = f"{base_url}/najnovije-vesti"
    response = requests.get(news_url, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")
    articles = soup.select("article.telegraf-article")[:10]

    items = []
    for article in articles:
        link_tag = article.find("a", href=True)
        title_tag = article.find("h2")
        if not link_tag or not title_tag:
            continue
        link = link_tag["href"]
        if not link.startswith("http"):
            link = base_url + link
        title = title_tag.get_text(strip=True)

        try:
            article_page = requests.get(link, timeout=10)
            article_soup = BeautifulSoup(article_page.text, "html.parser")
            meta = article_soup.find("meta", {"property": "article:published_time"})
            if meta and meta.get("content"):
                pub_date = datetime.fromisoformat(meta["content"].replace("Z", "+00:00"))
            else:
                pub_date = datetime.utcnow()
        except:
            pub_date = datetime.utcnow()

        items.append((title, link, format_datetime(pub_date)))

    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = "Telegraf Aero - Najnovije vesti"
    ET.SubElement(channel, "link").text = news_url
    ET.SubElement(channel, "description").text = "Validne i ažurne vesti sa sajta Telegraf Aero"
    ET.SubElement(channel, "language").text = "sr"

    for title, link, pub_date in items:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = title
        ET.SubElement(item, "link").text = link
        ET.SubElement(item, "description").text = title
        ET.SubElement(item, "pubDate").text = pub_date

    os.makedirs("docs", exist_ok=True)
    tree = ET.ElementTree(rss)
    tree.write("docs/telegraf_najnovije.xml", encoding="utf-8", xml_declaration=True)
    print("✅ RSS feed uspešno generisan u 'docs/telegraf_najnovije.xml'.")

if __name__ == "__main__":
    generate_rss()
