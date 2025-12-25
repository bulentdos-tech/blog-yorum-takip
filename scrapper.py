import xml.etree.ElementTree as ET
import requests
from bs4 import BeautifulSoup
import json
import re
import os

def blog_listesini_getir(xml_dosyasi):
    tree = ET.parse(xml_dosyasi)
    root = tree.getroot()
    liste = []
    for entry in root.findall('.//ENTRY'):
        isim = entry.find('CONCEPT').text
        raw_def = entry.find('DEFINITION').text
        soup = BeautifulSoup(raw_def, 'html.parser')
        link = soup.get_text().strip()
        temiz_link = re.sub(r'\?m=1', '', link)
        if temiz_link.endswith('/'): temiz_link = temiz_link[:-1]
        liste.append({'isim': isim, 'url': temiz_link})
    return liste

def yorumlari_indir(blog_url):
    feed_url = f"{blog_url}/feeds/comments/default?alt=json"
    try:
        response = requests.get(feed_url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            comments = []
            if 'feed' in data and 'entry' in data['feed']:
                for entry in data['feed']['entry']:
                    comments.append({
                        'yazar': entry['author'][0]['name']['$t'],
                        'icerik': entry['content']['$t'],
                        'tarih': entry['published']['$t']
                    })
            return comments
    except: return []
    return []

# İşlemi Başlat
bloglar = blog_listesini_getir('blog yorum.xml')
sonuclar = {}

for blog in bloglar:
    print(f"Okunuyor: {blog['isim']}")
    sonuclar[blog['isim']] = {
        'url': blog['url'],
        'yorumlar': yorumlari_indir(blog['url'])
    }

# Sonuçları JSON dosyasına yaz
with open('tum_yorumlar.json', 'w', encoding='utf-8') as f:
    json.dump(sonuclar, f, ensure_ascii=False, indent=4)
