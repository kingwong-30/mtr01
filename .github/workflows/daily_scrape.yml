import json
import re
import time
import unicodedata
from datetime import date, datetime, timedelta
import requests
from bs4 import BeautifulSoup


def parse_meditation_page(html_text):
    """解析單一頁面的 4 大要素"""
    soup = BeautifulSoup(html_text, "html.parser")

    # 1. 提取主標題 (H1 / Article Title)
    title_el = soup.find(["h1", "h2", "header"])
    title = (
        title_el.get_text(strip=True)
        if title_el
        else "Daily Gospel Meditation"
    )

    # 移除 script/style 干擾標籤
    for tag in soup(["script", "style"]):
        tag.extract()

    raw_text = soup.get_text(separator="\n")
    clean_text = unicodedata.normalize("NFKD", raw_text)

    # 2. 抓取從 "Gospel Reading" 到 "Meditation" 之間的段落
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

    # 3. 提取章節 (reading) 與 內文 (content)
    if lines:
        # 第一行為章節標題，如 "Gospel Reading: Matthew 23:13-22" 或 "Matthew 23:13-22"
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
    """爬取整年份的聖言資料並儲存至 data.json"""
    base_url = "https://www.dailyscripture.net/daily-meditation/"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
    }

    # 嘗試讀取現有的 data.json 以保留已爬取內容
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            all_data = json.load(f)
    except FileNotFoundError:
        all_data = {}

    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)
    delta = timedelta(days=1)

    curr = start_date
    print(f"🚀 開始爬取/更新 {year} 年度的聖言資料...")

    session = requests.Session()

    while curr <= end_date:
        date_key = curr.strftime("%Y-%m-%d")  # 例: 2026-08-24
        formatted_date_str = curr.strftime(
            "%A %d %B %Y"
        )  # 例: Monday 24 August 2026
        url_date_param = curr.strftime("%b%d").lower()  # 例: aug24

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
                print(f"  [✅] {date_key}: {title} | {reading}")
            else:
                print(
                    f"  [⚠️] {date_key}: 網站回應狀態碼 {resp.status_code}"
                )

        except Exception as e:
            print(f"  [❌] {date_key} 爬取失敗: {e}")

        # 適當延遲，避免對目標網站發送過於頻繁的請求
        time.sleep(0.5)
        curr += delta

    # 儲存至 data.json
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    print("🎉 全年資料爬取並成功更新至 data.json！")


if __name__ == "__main__":
    current_year = datetime.now().year
    scrape_year_data(current_year)
