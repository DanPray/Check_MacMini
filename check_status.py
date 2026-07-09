import os
import requests

# 從 GitHub Secrets 讀取 LINE 金鑰
LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
LINE_USER_ID = os.getenv("LINE_USER_ID")
#TARGET_URL = "https://nextcloud-proxy.17pray.workers.dev"
TARGET_URL = "https://google.com/error404test"
def send_line(message):
    if not LINE_ACCESS_TOKEN or not LINE_USER_ID:
        print("錯誤：找不到 LINE 憑證設定")
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
        r = requests.post("https://api.line.me/v2/bot/message/push", headers=headers, json=body, timeout=10)
        print(f"LINE 傳送狀態: {r.status_code}")
    except Exception as e:
        print(f"LINE 發送失敗: {e}")

def main():
    try:
        response = requests.get(TARGET_URL, timeout=15)
        
        # 狀況 A：Worker 直接噴 5xx 錯誤
        if response.status_code >= 400:
            send_line(f"🚨 外部監控警報：Nextcloud 代理服務異常！\n狀態碼：{response.status_code}")
            return

        # 狀況 B：雖然狀態碼 200，但內容其實是 Cloudflare 的斷線錯誤網頁
        # 我們檢查網頁內容有沒有 Nextcloud 該有的關鍵字（例如 status.php 的 "installed"）
        # 如果你戳的是首頁，可以改檢查 "Nextcloud" 關鍵字
        if "Nextcloud" not in response.text and "installed" not in response.text:
            send_line(f"🚨 外部監控警報：網頁可連線，但內容異常（可能 trycloudflare 已斷線或跳轉失敗）")
        else:
            print(f"服務正常，狀態碼：{response.status_code}")
            
    except requests.exceptions.RequestException as e:
        send_line(f"🚨 外部監控警報：無法連線至 Worker 服務\n錯誤原因：{e}")

if __name__ == "__main__":
    main()
