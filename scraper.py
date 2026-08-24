import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

URL = "https://www.dailyscripture.net/"

def fetch_daily_scripture():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(URL, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # 根據 dailyscripture.net 結構抓取元素 (草稿邏輯)
        # 標題
        title_el = soup.find('h1') or soup.find('h2')
        title = title_el.get_text(strip=True) if title_el else "Daily Reading"

        # 福音經節出處 (例如 GOSPEL READING: Matthew 23:13-22)
        reading = "GOSPEL READING"
        content_paragraphs = []

        # 擷取本文內文
        for p in soup.find_all('p'):
            text = p.get_text(strip=True)
            if "GOSPEL READING" in text.upper():
                reading = text
            elif text and not text.startswith("Copyright"):
                content_paragraphs.append(text)

        full_content = "\n\n".join(content_paragraphs[:3]) # 擷取主內文

        today_data = {
            "date": datetime.now().strftime("%B %d, %Y"),
            "title": title,
            "reading": reading,
            "content": full_content
        }

        # 讀取舊 data.json 以更新 yesterday
        try:
            with open("data.json", "r", encoding="utf-8") as f:
                old_data = json.load(f)
                yesterday_data = old_data.get("today", {})
        except FileNotFoundError:
            yesterday_data = today_data

        result = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "today": today_data,
            "yesterday": yesterday_data
        }

        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print("data.json 更新成功！")

    except Exception as e:
        print(f"抓取失敗: {e}")

if __name__ == "__main__":
    fetch_daily_scripture()
