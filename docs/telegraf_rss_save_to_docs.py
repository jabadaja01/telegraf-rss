import os
from bs4 import BeautifulSoup
from datetime import datetime

def generate_rss():
    # Primer podataka, zameni sa stvarnim
    title = "Telegraf.rs Najnovije"
    link = "https://aero.telegraf.rs/najnovije-vesti"
    description = "Najnovije vesti sa sajta Telegraf.rs"
    language = "sr"

    items = [
        {
            "title": "Naslov vesti 1",
            "link": "https://aero.telegraf.rs/vest1",
            "description": "Opis vesti 1",
            "pubDate": datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0200"),
        },
        # Dodaj više vesti ovde
    ]

    rss = BeautifulSoup(features="xml")
    rss_tag = rss.new_tag("rss", version="2.0")
    channel_tag = rss.new_tag("channel")

    title_tag = rss.new_tag("title")
    title_tag.string = title
    channel_tag.append(title_tag)

    link_tag = rss.new_tag("link")
    link_tag.string = link
    channel_tag.append(link_tag)

    desc_tag = rss.new_tag("description")
    desc_tag.string = description
    channel_tag.append(desc_tag)

    lang_tag = rss.new_tag("language")
    lang_tag.string = language
    channel_tag.append(lang_tag)

    for item in items:
        item_tag = rss.new_tag("item")

        i_title = rss.new_tag("title")
        i_title.string = item["title"]
        item_tag.append(i_title)

        i_link = rss.new_tag("link")
        i_link.string = item["link"]
        item_tag.append(i_link)

        i_desc = rss.new_tag("description")
        i_desc.string = item["description"]
        item_tag.append(i_desc)

        i_date = rss.new_tag("pubDate")
        i_date.string = item["pubDate"]
        item_tag.append(i_date)

        channel_tag.append(item_tag)

    rss_tag.append(channel_tag)
    rss.append(rss_tag)

    # ✅ OVDE SE MENJA NAZIV FAJLA
    with open("docs/telegraf_najnovije.xml", "w", encoding="utf-8") as f:
        f.write(str(rss.prettify()))

if __name__ == "__main__":
    generate_rss()
