import re
from modules.base import detect_pattern

VULNERABLE_VERSIONS_EXPRESS = [
    "4.0.0", "4.16.0", "5.0.0"
]

def detect_express(js_code: str, headers: dict) -> bool:
    patterns = ['express', 'Express']
    return bool(detect_pattern(js_code, patterns))

def detect_express_version(js_code: str) -> str | None:
    patterns = [
        r'express(?:@|\s*version\s*[:=]\s*["\'])([0-9]+\.[0-9]+\.[0-9]+)',
    ]
    for pat in patterns:
        m = re.search(pat, js_code, re.I)
        if m:
            return m.group(1)
    return None

def detect(js_code: str, headers: dict) -> str | None:
    if detect_express(js_code, headers):
        version = detect_express_version(js_code)
        msg = "Найдено упоминание Express.js"
        if version:
            msg += f" {version}"
            if version in VULNERABLE_VERSIONS_EXPRESS:
                msg += " ⚠️ Уязвимая версия"
        return msg
    return None
