import json
import re
import requests
from bs4 import BeautifulSoup


def scrape_daily_gospel():
    # 假設目標網址 (請替換為您實際爬取的網址)
    url = "https://www.dailyscripture.servantsofword.org/readings/"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # 這裡根據網頁結構取得純文字內容
        soup = BeautifulSoup(response.text, "html.parser")

        # 取得網頁整體純文字（或特定區塊文字）
        full_text = soup.get_text(separator="\n")

        # --- 文字過濾邏輯 ---
        # 1. 截取從 "GOSPEL READING:" 或 "Alternate reading:" 開始，到 "Meditation" 為止的文字
        pattern = r"(GOSPEL READING:[\s\S]*?)(?=Meditation)"
        match = re.search(pattern, full_text)

        if match:
            gospel_content = match.group(1).strip()
        else:
            # 備用方案：若找不到 GOSPEL READING，嘗試抓取 Alternate reading 至 Meditation 之間
            alt_pattern = (
                r"Alternate reading:[^\n]*\n+([\s\S]*?)(?=Meditation)"
            )
            alt_match = re.search(alt_pattern, full_text)
            gospel_content = (
                alt_match.group(1).strip()
                if alt_match
                else "未能找到福音經文"
            )

        # 拆分出第一行（例如 "GOSPEL READING: Matthew 23:13-22"）作為標題/讀經章節
        lines = gospel_content.split("\n")
        reading_title = lines[0] if lines else "GOSPEL READING"
        body_text = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""

        # 構造輸出 json
        data = {
            "today": {
                "title": "✝️ Daily Gospel",
                "reading": reading_title,
                "content": body_text,
                "date": "Saint Matthew",
            }
        }

        # 寫入 data.json
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print("成功更新 data.json")

    except Exception as e:
        print(f"爬取失敗: {e}")
        # 若失敗則輸出錯誤訊息 json 避免前端崩潰
        error_data = {
            "today": {
                "title": "✝️ Daily Gospel",
                "reading": "",
                "content": "載入聖言失敗，請稍後再試。",
                "date": "",
            }
        }
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(error_data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    scrape_daily_gospel()
