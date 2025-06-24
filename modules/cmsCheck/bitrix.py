import re, requests

VULN_RANGES = [
    ("16.0.0", "16.5.9"),
    ("17.0.0", "17.6.6"),
    ("18.0.0", "18.5.9"),
    ("20.0.0", "20.5.7"),
    ("21.0.0", "21.400.0"),
]

def detect(domain, s):
    r = s.get(domain, timeout=10); html = r.text.lower()
    if ("bitrix" in html or "1c-bitrix" in html or
        "bitrix" in r.headers.get("x-powered-cms", "").lower() or
        "bitrix" in r.headers.get("x-generator", "").lower()):
        
        m = re.search(r'bitrix(?:[ _\-]version)?\s*[:=]?\s*[\'"]?([\d.]{3,})', html)
        version = m.group(1) if m else None
        vuln = False
        if version:
            for low, high in VULN_RANGES:
                if low <= version <= high:
                    vuln = True
                    break
        return {"cms": "Bitrix", "version": version, "vulnerable": vuln}
