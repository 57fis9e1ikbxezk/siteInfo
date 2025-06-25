import requests

def send_message(token: str, chat_id: int, text: str):
    max_len = 1024
    chunks = [text[i:i+max_len] for i in range(0, len(text), max_len)]
    for chunk in chunks:
        resp = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data={"chat_id": chat_id, "text": chunk}
        )
        if not resp.ok:
            print(f"Telegram API error: {resp.status_code}, {resp.text}")