import calendar
import json
import os
import re
import time
import unicodedata
from datetime import date, datetime, timedelta
import requests
from bs4 import BeautifulSoup


def parse_meditation_page(html_text):
    soup = BeautifulSoup(html_text, "html.parser")

    title_el = soup.find(["h1", "h2", "header"])
    title = (
        title_el.get_text(strip=True)
        if title_el
        else "Daily Gospel Meditation"
    )

    for tag in soup(["script", "style"]):
        tag.extract()

    raw_text = soup.get_text(separator="\n")
    clean_text = unicodedata.normalize("NFKD", raw_text)

    pattern = (
        r"(Gospel\s+Reading:?[\s\S]*?)(?=(?:Meditation|Old\s+Testament|$))"
    )
    match = re.search(pattern, clean_text, re.IGNORECASE)

    extracted = ""
    if match:
        extracted = match.group(1).strip()
    else:
        alt_pattern = r"(Alternate\s+reading:?[\s\S]*?)(?=(?:Meditation|Old\s+Testament|$))"
        alt_match = re.search(alt_pattern, clean_text, re.IGNORECASE)
        extracted = alt_match.group(1).strip() if alt_match else ""

    lines = [line.strip() for line in extracted.split("\n") if line.strip()]

    if lines:
        first_line = lines[0]
        reading = re.sub(
            r"^Gospel\s+Reading:\s*", "", first_line, flags=re.IGNORECASE
        ).strip()
        body_lines = lines[1:] if len(lines) > 1 else []
        content = "\n".join(body_lines).strip()
    else:
        reading = "Gospel Reading"
        content = extracted

    return title, reading, content


def scrape_next_month_data():
    today = date.today()
    
    # 計算下一個月份與年份（支援跨年：12 月自動切換至明年 1 月）
    if today.month == 12:
        next_year = today.year + 1
        next_month = 1
    else:
        next_year = today.year
        next_month = today.month + 1

    base_url = "https://www.dailyscripture.net/daily-meditation/"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
    }

    try:
        with open("data.json", "r", encoding="utf-8") as f:
            all_data = json.load(f)
    except FileNotFoundError:
        all_data = {}

    # 計算「下一個月」的第一天與最後一天
    start_date = date(next_year, next_month, 1)
    last_day = calendar.monthrange(next_year, next_month)[1]
    end_date = date(next_year, next_month, last_day)
    delta = timedelta(days=1)

    curr = start_date
    print(f"🚀 開始爬取【下一個月】{next_year} 年 {next_month} 月份聖言資料 ({start_date} 至 {end_date})...")

    session = requests.Session()

    while curr <= end_date:
        date_key = curr.strftime("%Y-%m-%d")
        formatted_date_str = curr.strftime("%A %d %B %Y")
        url_date_param = curr.strftime("%b%d").lower()

        target_url = f"{base_url}?ds_year={next_year}&date={url_date_param}"

        try:
            resp = session.get(target_url, headers=headers, timeout=12)
            if resp.status_code == 200:
                title, reading, content = parse_meditation_page(resp.text)
                all_data[date_key] = {
                    "title": title,
                    "date": formatted_date_str,
                    "reading": reading,
                    "content": content,
                }
                print(f"  [✅] {date_key}: {title}")
            else:
                print(
                    f"  [⚠️] {date_key}: 狀態碼 {resp.status_code}"
                )
        except Exception as e:
            print(f"  [❌] {date_key} 失敗: {e}")

        time.sleep(0.5)
        curr += delta

    # 寫入檔案
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    # 驗證數據寫入狀態
    print("\n" + "=" * 40)
    print("🧪 開始驗證 data.json 寫入狀態...")

    if os.path.exists("data.json"):
        file_size = os.path.getsize("data.json")
        print(f"✅ 檔案存在：data.json ({file_size / 1024:.2f} KB)")
    else:
        print("❌ 錯誤：找不到 data.json 檔案！")

    try:
        with open("data.json", "r", encoding="utf-8") as f:
            verified_data = json.load(f)
        
        final_count = len(verified_data)
        print(f"📊 總資料筆數：{final_count} 筆")
        
        recent_keys = sorted(verified_data.keys())[-3:]
        print("🗓️ 最新寫入的日期範例：")
        for key in recent_keys:
            print(f"   - {key}: {verified_data[key].get('title')}")

    except Exception as e:
        print(f"❌ 讀取驗證失敗：{e}")
    
    print("=" * 40 + "\n")
    print(f"🎉 {next_year} 年 {next_month} 月份資料已成功儲存並驗證完成！")


if __name__ == "__main__":
    scrape_next_month_data()
