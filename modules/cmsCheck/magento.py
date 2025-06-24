import re, requests, json
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from packaging.version import Version, InvalidVersion

_VERSION_HTML_RE   = re.compile(r'magento(?:\s*(?:commerce|ver|version))?\s*v?([\d.]+)', re.I)
_VERSION_META_RE   = re.compile(r'<meta[^>]+name=["\']generator["\'][^>]+content=["\']magento\s*v?([\d.]+)', re.I)
_VERSION_JS_RE     = re.compile(r'["\']?version["\']?\s*[:=]\s*["\']([\d.]+)["\']', re.I)

# CVE-based минимальное «безопасное» ядро (2.4.6 → патч, 2.4.7 и выше безопасен)
SAFE_MIN_VERSION = Version("2.4.6")

def _fetch(url: str, s: requests.Session, timeout=5):
    try:
        r = s.get(url, timeout=timeout, allow_redirects=True)
        if r.ok:
            return r.text
    except Exception:
        pass
    return ""

def _detect_version_from_html(html: str) -> str | None:
    for regex in (_VERSION_META_RE, _VERSION_HTML_RE):
        m = regex.search(html)
        if m:
            return m.group(1)
    return None

def _detect_version_from_js(js_code: str) -> str | None:
    m = _VERSION_JS_RE.search(js_code)
    return m.group(1) if m else None

def _scan_linked_scripts(domain: str, html: str, s: requests.Session) -> str | None:
    soup = BeautifulSoup(html, "lxml")
    parsed_root = urlparse(domain)
    for script in soup.find_all("script", src=True)[:10]:           
        src = urljoin(domain, script["src"])
        if urlparse(src).netloc != parsed_root.netloc:               
            continue
        js = _fetch(src, s)
        v = _detect_version_from_js(js)
        if v:
            return v
    return None

def _scan_composer(domain: str, s: requests.Session) -> str | None:
    content = _fetch(urljoin(domain, "composer.json"), s)
    try:
        data = json.loads(content)
        pkg = data.get("name", "")
        ver = data.get("version") or data.get("extra", {}).get("magento", {}).get("version")
        if "magento" in pkg.lower() and ver:
            return ver
    except Exception:
        pass
    m = _VERSION_HTML_RE.search(content)
    return m.group(1) if m else None

def _is_vulnerable(ver_str: str) -> bool:
    try:
        return Version(ver_str) < SAFE_MIN_VERSION
    except InvalidVersion:
        return True   #  подозрительно

def detect(domain: str, s: requests.Session):
    html = _fetch(domain, s, timeout=10).lower()
    if ("magento" in html or "mage-" in html or
        "x-magento" in " ".join(k.lower() for k in s.headers.keys())):

        version = (_detect_version_from_html(html) or
                   _scan_linked_scripts(domain, html, s) or
                   _scan_composer(domain, s))

        vuln = _is_vulnerable(version) if version else None

        return {
            "cms": "Magento",
            "version": version,
            "vulnerable": vuln
        }
