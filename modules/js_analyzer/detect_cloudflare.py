import re
from modules.base import detect_pattern

_CLOUDFLARE_MARKERS = [
    "cdn-cgi", "cf-ray", "cf-cache-status", "__cfduid",
    "cf_clearance", "cloudflare"
]

_VERSION_RE = re.compile(r"cloudflare(?:[-/]\w+)?[/ ]v?(\d+(?:\.\d+)+)", re.I)

def _detect_cloudflare(text: str) -> bool:
    return detect_pattern(text, _CLOUDFLARE_MARKERS)

def _detect_version_from_headers(headers: dict) -> str | None:
    server = headers.get("Server") or headers.get("server", "")
    if m := _VERSION_RE.search(server):
        return m.group(1)
    return None

def detect(js_code: str, headers: dict) -> str | None:
    combined = " ".join(f"{k}: {v}" for k, v in headers.items()).lower() + " " + js_code.lower()
    if not _detect_cloudflare(combined):
        return None
    version = _detect_version_from_headers(headers)
    msg = "Обнаружен Cloudflare"
    if version:
        msg += f" {version}"
    return msg
