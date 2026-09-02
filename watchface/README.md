# Klar

簡約數字 Garmin 錶面。同一套相對座標佈局適配圓形 AMOLED（Forerunner 165 390×390、Forerunner 970 454×454 等）。用戶可在 Garmin Connect 選邊框樣式與顏色。

## 畫面

- 外圈可選邊框：細環 / 雙環 / 時刻刻度
- 顏色：石墨、金、銀、青綠、珊瑚、靛藍
- 上方：星期 + 日期
- 中央：時間（高功耗顯示秒）
- 下方：心率 | 步數 | 電量
- Always-On：隱藏秒、降低亮度、邊框變細，並輕微位移避免燒屏

座標全部由 [`source/Layout.mc`](source/Layout.mc) 用 `dc.getWidth()` / `dc.getHeight()` 百分比計算，沒有寫死像素。

## 目標機種

`fr165`、`fr165m`、`fr265`、`fr265s`、`fr965`、`fr970`、`venu3`、`venu3s`、`vivoactive5`

`minApiLevel` 為 5.0.0。

## 本機開發

1. 安裝 [Connect IQ SDK](https://developer.garmin.com/connect-iq/sdk/) 與 VS Code **Monkey C** 擴充。
2. Command Palette：`Monkey C: Generate a Developer Key`（金鑰只留本機，不要提交）。
3. 用 VS Code 打開 `watchface/`。
4. Run 模擬器，分別選 **Forerunner 165** 與 **Forerunner 970** 對比例。
5. 模擬器：File → Edit Persistent Storage → Edit Application Properties，改邊框樣式／顏色。
6. 上架：`Monkey C: Export Project` 產出 `.iq`。

## 收費上架

程式第一版是完整可用錶面，未內建付費牆。要在 Connect IQ Store 收費：

1. Garmin 開發者帳號
2. 加入 [Merchant Service](https://developer.garmin.com/connect-iq/monetization/)（年費約 USD 100，另約 15% 抽成）
3. 商店列出標記 **Payment Required**
4. 若提供試用，在描述寫清剩餘日數

### Store listing (English)

Klar is a quiet digital watch face for round AMOLED Garmins. Large time, date, heart rate, steps, and battery — laid out with relative coordinates so one face scales from Forerunner 165 to 970. Choose a thin, double, or tick frame in graphite, gold, silver, teal, coral, or indigo.

### 商店描述（繁體中文）

Klar 係一套簡約數字錶面，專為圓形 AMOLED 設計。大時間、日期、心率、步數、電量；位置跟螢幕尺寸比例計算，Forerunner 165 同 970 用同一套畫面。可選細環、雙環或時刻刻度，顏色包括石墨、金、銀、青綠、珊瑚、靛藍。
