import re, requests

def detect(domain: str, s: requests.Session):
    r = s.get(domain, timeout=10)
    html = r.text.lower()
    if ("prestashop" in html or
        "ps_version" in html or
        "x-prestashop-cache" in r.headers):
        ver = None
        m = re.search(r'prestashop(?:\s*[\w]*)\s*([\d.]+)', html)
        if m: ver = m.group(1)
        return {
            "cms": "PrestaShop",
            "version": ver,
            "vulnerable": None
        }
