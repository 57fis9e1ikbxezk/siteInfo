import re, requests
from urllib.parse import urljoin

def detect(domain: str, s: requests.Session):
    r = s.get(domain, timeout=10, allow_redirects=True)
    html = r.text.lower()
    if ("cdn.shopify.com" in html or                         
        "x-shopify-stage" in r.headers or                    # спец. заголовок
        "shopify" in r.headers.get("x-powered-by", "").lower()):
        # У Shopify версии ядра не раскрываются, дополните если имеете информацию о том, как их получить. Добавьте исправленный код в исешку(issue) и я ОБЯЗАТЕЛЬНО добавлю это коммитом
        return {
            "cms": "Shopify",
            "version": None,
            "vulnerable": None
        }
