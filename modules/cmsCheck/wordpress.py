import re, requests
from urllib.parse import urljoin

VULN_MAX_VERSION = "6.2"

def _meta_version(html):
    m = re.search(r'content=["\']wordpress\s*([\d\.]+)', html, re.I)
    return m.group(1) if m else None

def detect(domain, s):
    r = s.get(domain, timeout=10); html = r.text.lower()
    if "wp-content" in html or "wordpress" in r.headers.get("x-generator","").lower():
        version = _meta_version(html) or None
        vuln = (version is not None and version <= VULN_MAX_VERSION)
        return {"cms": "WordPress", "version": version, "vulnerable": vuln}
