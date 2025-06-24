import re, requests

def detect(domain: str, s: requests.Session):
    r = s.get(domain, timeout=10)
    html = r.text.lower()
    if ("static.wixstatic.com" in html or
        "x-wix-request-id" in r.headers or
        "wix.com" in html):
        # У wix версии ядра не раскрываются, дополните если имеете информацию о том, как их получить. Добавьте исправленный код в исешку(issue) и я ОБЯЗАТЕЛЬНО добавлю это коммитом
        return {
            "cms": "Wix",
            "version": None,
            "vulnerable": None
        }
