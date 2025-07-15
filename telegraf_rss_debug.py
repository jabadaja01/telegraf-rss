
import os
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from datetime import datetime
import subprocess
from email.utils import format_datetime

url = "https://aero.telegraf.rs/najnovije-vesti"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")
articles = soup.select("ul.article-listing li.article a")

print(f"🔍 Pronađeno linkova: {len(articles)}")
for a in articles[:5]:
    print("–", a.get_text(strip=True), "|", a.get("href"))

rss = ET.Element("rss", version="2.0")
channel = ET.SubElement(rss, "channel")
ET.SubElement(channel, "title").text = "Telegraf Aero - Najnovije vesti"
ET.SubElement(channel, "link").text = url
ET.SubElement(channel, "description").text = "Najnovije i validne vesti sa sajta Telegraf Aero"
ET.SubElement(channel, "language").text = "sr"

count = 0
for a in articles:
    if count >= 10:
        break
    title = a.get_text(strip=True)
    link = a.get("href")
    if not link.startswith("http"):
        link = "https://aero.telegraf.rs" + link

    try:
        check = requests.get(link, timeout=5)
        if check.status_code != 200:
            continue
        if "Došli ste na pogrešnu stranicu" in check.text:
            continue
        article_soup = BeautifulSoup(check.text, "html.parser")
        meta_time = article_soup.find("meta", {"property": "article:published_time"})
        if not meta_time:
            continue
        pub_datetime = datetime.fromisoformat(meta_time["content"])
        pubDate = format_datetime(pub_datetime)
    except Exception as e:
        print("⚠️ Greška:", e)
        continue

    item = ET.SubElement(channel, "item")
    ET.SubElement(item, "title").text = title
    ET.SubElement(item, "link").text = link
    ET.SubElement(item, "description").text = title
    ET.SubElement(item, "pubDate").text = pubDate
    ET.SubElement(item, "guid").text = link
    count += 1

repo_path = r"C:\Users\gordan.brkic\Desktop\telegraf-rss"
os.chdir(repo_path)
output_file = "telegraf_najnovije.xml"
tree = ET.ElementTree(rss)
tree.write(output_file, encoding="utf-8", xml_declaration=True)

subprocess.run(["git", "add", output_file])
subprocess.run(["git", "commit", "-m", "DEBUG: RSS test sa ispisom"])
subprocess.run(["git", "push"])
print("✅ RSS test završen. Proveri ispis iznad.")
