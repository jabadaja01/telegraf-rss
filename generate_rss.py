
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import xml.etree.ElementTree as ET

url = "https://aero.telegraf.rs/najnovije-vesti"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

articles = soup.select("ul.article-listing li.article a")[:10]

rss = ET.Element("rss", version="2.0")
channel = ET.SubElement(rss, "channel")
ET.SubElement(channel, "title").text = "Telegraf Aero - Najnovije vesti"
ET.SubElement(channel, "link").text = url
ET.SubElement(channel, "description").text = "Najnovije vesti sa sajta Telegraf Aero"
ET.SubElement(channel, "language").text = "sr"

for a in articles:
    title = a.get_text(strip=True)
    link = a["href"]
    if not link.startswith("http"):
        link = "https://aero.telegraf.rs" + link
    item = ET.SubElement(channel, "item")
    ET.SubElement(item, "title").text = title
    ET.SubElement(item, "link").text = link
    ET.SubElement(item, "description").text = title
    ET.SubElement(item, "pubDate").text = datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0200')

tree = ET.ElementTree(rss)
tree.write("telegraf_najnovije.xml", encoding="utf-8", xml_declaration=True)
