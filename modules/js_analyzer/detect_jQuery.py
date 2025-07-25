import re
from modules.base import detect_pattern

def detect_jquery(js_code: str) -> bool:
    patterns = ["jQuery", "$(", "jQuery.fn"]
    return bool(detect_pattern(js_code, patterns))

_VERSION_RGXES: list[re.Pattern] = [
    re.compile(r"jQuery(?:\s+JavaScript Library)?\s+v(?:ersion)?\s*([0-9]+\.[0-9]+\.[0-9]+)", re.I),
    re.compile(r"jQuery[-_\s]?ver(?:sion)?\s*=\s*[\"']([0-9]+\.[0-9]+\.[0-9]+)", re.I),
    re.compile(r"jquery[-_.]?([0-9]+\.[0-9]+\.[0-9]+)(?:\.min)?\.js", re.I),
]

def extract_version(js_code: str) -> str | None:
    for rgx in _VERSION_RGXES:
        m = rgx.search(js_code)
        if m:
            return m.group(1)
    return None

def is_version_vulnerable(ver: str) -> bool:
    try:
        major, minor, patch = map(int, ver.split("."))
    except ValueError:
        return False           # строка странная – лучше считать неизвестной
    if major < 3:
        return True
    if major == 3 and minor < 5:
        return True
    return False

def detect(js_code: str, headers: dict) -> str | None:
    if not detect_jquery(js_code):
        return None

    ver = extract_version(js_code)
    if ver:
        vulnerable = is_version_vulnerable(ver)
        if vulnerable:
            return (
                f"🔍 Найдена jQuery версии {ver} — "
                "известно о публичных уязвимостях (например CVE-2019-11358, CVE-2020-11022/23). "
            )
        else:
            return f"✅ Найдена jQuery версии {ver}"
    else:
        return "ℹ️ Найдено упоминание jQuery, но версию определить не удалось."
