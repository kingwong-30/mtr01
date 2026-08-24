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

    cleaned_lines = []
    for line in lines:
        if re.match(r"^Gospel\s+Reading:?$", line, re.IGNORECASE):
            continue
        sub_line = re.sub(
            r"^Gospel\s+Reading:\s*", "", line, flags=re.IGNORECASE
        ).strip()
        if sub_line:
            cleaned_lines.append(sub_line)

    reading = ""
    content = ""

    if cleaned_lines:
        first_line = cleaned_lines[0]
        # 【修復問題 5】用正則驗證第一行是否包含經文出處格式 (例如 "17:22" 或 "Matthew 17:22-27")
        has_chapter_ref = bool(re.search(r"\d+:\d+", first_line))

        if len(cleaned_lines) == 1:
            if has_chapter_ref:
                reading = first_line
                content = ""
            else:
                reading = ""
                content = first_line
        else:
            if has_chapter_ref:
                reading = first_line
                body_lines = cleaned_lines[1:]
            else:
                reading = ""
                body_lines = cleaned_lines
            content = "\n".join(body_lines).strip()

    return title, reading, content


def scrape_current_and_next_month_data():
    today = date.today()

    # 【修復問題 3】起點設為本月 1 號
    start_date = date(today.year, today.month, 1)

    # 計算下一個月的年份與月份
    if today.month == 12:
        next_year = today.year + 1
        next_month = 1
    else:
        next_year = today.year
        next_month = today.month + 1

    # 終點設為下個月的最後一天
    last_day_of_next_month = calendar.monthrange(next_year, next_month)[1]
    end_date = date(next_year, next_month, last_day_of_next_month)

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

    curr = start_date
    delta = timedelta(days=1)

    print(
        f"🚀 開始爬取【本月與下個月】聖言資料 ({start_date} 至 {end_date})..."
    )
    session = requests.Session()

    while curr <= end_date:
        date_key = curr.strftime("%Y-%m-%d")
        formatted_date_str = curr.strftime("%A %d %B %Y")
        url_date_param = curr.strftime("%b%d").lower()

        target_url = f"{base_url}?ds_year={curr.year}&date={url_date_param}"

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
                print(f"  [✅] {date_key}: {title} | {reading}")
            else:
                print(f"  [⚠️] {date_key}: 狀態碼 {resp.status_code}")
        except Exception as e:
            print(f"  [❌] {date_key} 失敗: {e}")

        time.sleep(0.3)
        curr += delta

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    print(f"\n🎉 資料爬取完成，已儲存至 data.json (共 {len(all_data)} 筆資料)")


if __name__ == "__main__":
    scrape_current_and_next_month_data()
