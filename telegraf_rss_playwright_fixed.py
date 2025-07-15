
import os
import asyncio
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import format_datetime
import subprocess

def generate_rss():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://aero.telegraf.rs/najnovije-vesti", timeout=60000)
        page.wait_for_selector("a.group", timeout=15000, state="attached")  # <- ključna izmena
        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")
    articles = soup.select("a.group")

    print(f"🔍 Pronađeno linkova: {len(articles)}")
    for a in articles[:5]:
        print("–", a.get_text(strip=True), "|", a.get("href"))

    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = "Telegraf Aero - Najnovije vesti"
    ET.SubElement(channel, "link").text = "https://aero.telegraf.rs/najnovije-vesti"
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
            import requests
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
    subprocess.run(["git", "commit", "-m", "✅ Ispravljen selektor sa state=attached"])
    subprocess.run(["git", "push"])
    print("✅ RSS uspešno generisan Playwright-om (sa čekanjem na attached state).")

if __name__ == "__main__":
    generate_rss()
