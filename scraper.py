import json
import re
import unicodedata
import requests
from bs4 import BeautifulSoup


def scrape_daily_gospel():
    # 1. 更正為最新每日聖言目標網址
    url = "https://www.dailyscripture.net/daily-meditation/"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # 移除干擾文字的 Script 及 Style 標籤
        for script in soup(["script", "style"]):
            script.extract()

        # 取得純文字並進行字元標準化 (去除 \xa0 等特殊隱藏空格)
        raw_text = soup.get_text(separator="\n")
        clean_text = unicodedata.normalize("NFKD", raw_text)

        # 2. 正則表達式：不區分大小寫 (re.IGNORECASE) 抓取 Gospel Reading 至 Meditation 之間
        pattern = (
            r"(Gospel\s+Reading:?[\s\S]*?)(?=(?:Meditation|Old\s+Testament|$))"
        )
        match = re.search(pattern, clean_text, re.IGNORECASE)

        if match:
            extracted = match.group(1).strip()
        else:
            # 備用方案：嘗試搜尋 Alternate reading
            alt_pattern = r"(Alternate\s+reading:?[\s\S]*?)(?=(?:Meditation|Old\s+Testament|$))"
            alt_match = re.search(alt_pattern, clean_text, re.IGNORECASE)
            extracted = alt_match.group(1).strip() if alt_match else ""

        if not extracted:
            raise ValueError("未能比對出福音經文內容")

        # 3. 清理與拆分行文字
        lines = [line.strip() for line in extracted.split("\n") if line.strip()]

        # 第一行為讀經章節（例如 Gospel Reading: Matthew 23:13-22）
        reading_title = lines[0] if lines else "Gospel Reading"
        
        # 其餘行數組合成經文內文
        content_lines = lines[1:] if len(lines) > 1 else lines
        body_content = "\n".join(content_lines).strip()

        # 4. 構建輸出 JSON
        data = {
            "today": {
                "title": "✝️ Daily Gospel",
                "reading": reading_title,
                "content": body_content,
                "date": "Daily Scripture",
            }
        }

        # 寫入 data.json
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print("✅ 成功擷取每日聖言並更新 data.json！")

    except Exception as e:
        print(f"❌ 爬取失敗: {e}")
        # 失敗時產生的 fallback json，確保前端不會壞掉
        error_data = {
            "today": {
                "title": "✝️ Daily Gospel",
                "reading": "載入失敗",
                "content": "暫時無法取得每日聖言，請稍後再試。",
                "date": "",
            }
        }
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(error_data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    scrape_daily_gospel()
