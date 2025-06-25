import re
from modules.base import detect_pattern

VULNERABLE_VERSIONS_ALPINE = [
    "2.0.0",  # исторически уязвимая
    "2.8.2",  # XSS
]

def detect_alpine(js_code: str) -> bool:
    patterns = ['Alpine', 'Alpine.start', 'x-data']
    return bool(detect_pattern(js_code, patterns))

def detect_alpine_version(js_code: str) -> str | None:
    patterns = [
        r'alpine(?:@|\s*version\s*[:=]\s*["\'])([0-9]+\.[0-9]+\.[0-9]+)',
    ]
    for pat in patterns:
        m = re.search(pat, js_code, re.I)
        if m:
            return m.group(1)
    return None

def detect(js_code: str, headers: dict) -> str | None:
    if detect_alpine(js_code):
        version = detect_alpine_version(js_code)
        msg = "Найдено упоминание Alpine.js"
        if version:
            msg += f" {version}"
            if version in VULNERABLE_VERSIONS_ALPINE:
                msg += " ⚠️ Уязвимая версия"
        return msg
    return None
