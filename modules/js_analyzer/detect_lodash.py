import re
from modules.base import detect_pattern

VULNERABLE_VERSIONS_LODASH = [
    "3.0.0", "4.0.0"
]

def detect_lodash(js_code: str) -> bool:
    patterns = ['lodash']
    return bool(detect_pattern(js_code, patterns))

def detect_lodash_version(js_code: str) -> str | None:
    patterns = [
        r'lodash(?:@|\s*version\s*[:=]\s*["\'])([0-9]+\.[0-9]+\.[0-9]+)',
    ]
    for pat in patterns:
        m = re.search(pat, js_code, re.I)
        if m:
            return m.group(1)
    return None

def detect(js_code: str, headers: dict) -> str | None:
    if detect_lodash(js_code):
        version = detect_lodash_version(js_code)
        msg = "Найдено упоминание Lodash"
        if version:
            msg += f" {version}"
            if version in VULNERABLE_VERSIONS_LODASH:
                msg += " ⚠️ Уязвимая версия"
        return msg
    return None
