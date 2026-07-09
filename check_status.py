import os
import requests
from datetime import datetime, timedelta

LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
LINE_USER_ID = os.getenv("LINE_USER_ID")
TARGET_URL = "https://nextcloud-proxy.17pray.workers.dev"

def send_line(message):
    if not LINE_ACCESS_TOKEN or not LINE_USER_ID:
        return
    headers = {
        "Authorization": f"Bearer {LINE_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    body = {
        "to": LINE_USER_ID,
        "messages": [{"type": "text", "text": message}]
    }
    try:
        requests.post("https://api.line.me/v2/bot/message/push", headers=headers, json=body, timeout=10)
    except Exception as e:
        print(f"LINE 發送失敗: {e}")

def main():
    # 1. 處理時區：GitHub 伺服器預設是 UTC，我們加上 8 小時轉換為台灣時間
    tw_time = datetime.utcnow() + timedelta(hours=8)
    
    # 2. 判斷是否為 03:00 ~ 03:30 路由器重啟時段
    if tw_time.hour == 3 and tw_time.minute < 30:
        print(f"[{tw_time.strftime('%Y-%m-%d %H:%M')}] ⚠️ 路由器重啟時段，跳過外部檢查")
        return

    try:
        response = requests.get(TARGET_URL, timeout=15)
        if response.status_code >= 400:
            send_line(f"🚨 外部監控警報：Nextcloud 代理服務異常！\n狀態碼：{response.status_code}")
        elif "Nextcloud" not in response.text and "installed" not in response.text:
            send_line(f"🚨 外部監控警報：網頁可連線，但內容異常（可能 trycloudflare 斷線）")
        else:
            print(f"服務正常，狀態碼：{response.status_code}")
            
    except requests.exceptions.RequestException as e:
        send_line(f"🚨 外部監控警報：無法連線至 Nextcloud（可能家裡網路斷線或死機）\n原因：{e}")

if __name__ == "__main__":
    main()
