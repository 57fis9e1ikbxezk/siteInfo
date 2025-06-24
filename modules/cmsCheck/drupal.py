import re, requests

def detect(domain: str, s: requests.Session):
    r = s.get(domain, timeout=10)
    h = r.text.lower()
    if "drupal" in h or "drupal" in r.headers.get("x-generator", "").lower():
        m = re.search(r'drupal\s*([\d\.]+)', h)
        return {"cms": "Drupal", "version": m.group(1) if m else None}
