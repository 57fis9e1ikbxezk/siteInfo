import re
from modules.base import detect_pattern

VULNERABLE_VERSIONS_EMBER = [
    "1.10.0", "2.13.3", "2.16.0", "3.4.4", "3.8.1"
]

def detect_ember(js_code: str) -> bool:
    patterns = ['Ember', 'Ember.Application']
    return bool(detect_pattern(js_code, patterns))

def detect_ember_version(js_code: str) -> str | None:
    patterns = [
        r'ember(?:@|\s*version\s*[:=]\s*["\'])([0-9]+\.[0-9]+\.[0-9]+)',
    ]
    for pat in patterns:
        m = re.search(pat, js_code, re.I)
        if m:
            return m.group(1)
    return None

def detect(js_code: str, headers: dict) -> str | None:
    if detect_ember(js_code):
        version = detect_ember_version(js_code)
        msg = "Найдено упоминание Ember.js"
        if version:
            msg += f" {version}"
            if version in VULNERABLE_VERSIONS_EMBER:
                msg += " ⚠️ Уязвимая версия"
        return msg
    return None
