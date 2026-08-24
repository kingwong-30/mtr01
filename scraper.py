import json
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


def scrape_year_data(year=2026):
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

    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)
    delta = timedelta(days=1)

    curr = start_date
    print(f"🚀 開始爬取 {year} 年度聖言資料...")

    session = requests.Session()

    while curr <= end_date:
        date_key = curr.strftime("%Y-%m-%d")
        formatted_date_str = curr.strftime("%A %d %B %Y")
        url_date_param = curr.strftime("%b%d").lower()

        target_url = f"{base_url}?ds_year={year}&date={url_date_param}"

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

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    print("🎉 資料已成功儲存至 data.json！")


if __name__ == "__main__":
    current_year = datetime.now().year
    scrape_year_data(current_year)
