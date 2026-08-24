import calendar
import datetime
import json
import os
import re
import time
import unicodedata
from bs4 import BeautifulSoup
import requests


def get_date_range():
    """計算從當月 1 號到下個月最後一天的日期列表"""
    today = datetime.date.today()
    start_date = today.replace(day=1)

    if today.month == 12:
        next_month_year = today.year + 1
        next_month = 1
    else:
        next_month_year = today.year
        next_month = today.month + 1

    _, last_day_of_next_month = calendar.monthrange(
        next_month_year, next_month
    )
    end_date = datetime.date(
        next_month_year, next_month, last_day_of_next_month
    )

    date_list = []
    current_date = start_date
    while current_date <= end_date:
        date_list.append(current_date)
        current_date += datetime.timedelta(days=1)

    return date_list


def parse_meditation_page(html_content):
    """解析 HTML 內容，擷取福音經文與出處"""
    soup = BeautifulSoup(html_content, "html.parser")

    # 清理非文字內容標籤
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    # 優先定位主要內容區域
    content_area = (
        soup.find("div", class_=re.compile(r"entry-content|post-content"))
        or soup
    )

    text = content_area.get_text(separator="\n")
    normalized_text = unicodedata.normalize("NFKC", text)

    # 修正後的 Regex：匹配 Gospel Reading / Alternate reading，直到遇到 Meditation/Reflection 或頁尾才停止
    pattern = r"(?:Gospel Reading|Alternate reading):\s*(.*?)(?=\n\s*(?:Meditation|Reflection|Copyright|\Z))"
    gospel_match = re.search(pattern, normalized_text, re.DOTALL | re.IGNORECASE)

    if not gospel_match:
        return None

    raw_gospel = gospel_match.group(1).strip()
    lines = [line.strip() for line in raw_gospel.split("\n") if line.strip()]

    if not lines:
        return None

    # 分離經文出處與正文
    reference = ""
    passage_lines = []

    # 第一行通常包含章節格式（例如 "Matthew 23:13-22"）
    if re.search(r"\d+:\d+", lines[0]):
        reference = lines[0]
        passage_lines = lines[1:]
    else:
        passage_lines = lines

    passage = "\n".join(passage_lines).strip()

    return {"reference": reference, "passage": passage}


def main():
    json_filename = "data.json"

    if os.path.exists(json_filename):
        try:
            with open(json_filename, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}
    else:
        data = {}

    date_range = get_date_range()

    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                " (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
            )
        }
    )

    for date_obj in date_range:
        date_str = date_obj.strftime("%Y-%m-%d")
        url = f"https://www.dailyscripture.net/daily-meditation/?ds_date={date_str}"

        try:
            response = session.get(url, timeout=10)
            if response.status_code == 200:
                result = parse_meditation_page(response.text)
                if result:
                    data[date_str] = result
                    print(f"[{date_str}] 成功抓取數據")
                else:
                    print(f"[{date_str}] 未能解析出福音內容")
            else:
                print(f"[{date_str}] 請求失敗，狀態碼: {response.status_code}")
        except Exception as e:
            print(f"[{date_str}] 發生錯誤: {e}")

        time.sleep(0.3)

    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("\n資料爬取與更新完成！")


if __name__ == "__main__":
    main()
