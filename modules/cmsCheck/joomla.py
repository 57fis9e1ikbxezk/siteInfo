import re, requests

VULN_RANGES = [
    ("4.0.0", "4.4.12"),
    ("5.0.0", "5.2.5"),
    ("3.0.0", "3.10.16"),
    ("4.0.0", "4.4.6"),
    ("5.0.0", "5.1.2"),
]

def detect(domain, s):
    r = s.get(domain, timeout=10); html = r.text.lower()
    if "joomla" in html or "joomla" in r.headers.get("x-generator","").lower():
        m = re.search(r'joomla[\s\/]?([\d\.]+)', html)
        version = m.group(1) if m else None
        vuln = False
        if version:
            for low,high in VULN_RANGES:
                if low <= version <= high:
                    vuln = True
                    break
        return {"cms": "Joomla", "version": version, "vulnerable": vuln}
