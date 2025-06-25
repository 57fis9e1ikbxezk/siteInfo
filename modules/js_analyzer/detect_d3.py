import re
from modules.base import detect_pattern

VULNERABLE_VERSIONS_D3 = [
    "4.0.0", "5.0.0"
]

def detect_d3(js_code: str) -> bool:
    patterns = ['d3', 'D3']
    return bool(detect_pattern(js_code, patterns))

def detect_d3_version(js_code: str) -> str | None:
    patterns = [
        r'd3(?:@|\s*version\s*[:=]\s*["\'])([0-9]+\.[0-9]+\.[0-9]+)',
    ]
    for pat in patterns:
        m = re.search(pat, js_code, re.I)
        if m:
            return m.group(1)
    return None

def detect(js_code: str, headers: dict) -> str | None:
    if detect_d3(js_code):
        version = detect_d3_version(js_code)
        msg = "Найдено упоминание D3.js"
        if version:
            msg += f" {version}"
            if version in VULNERABLE_VERSIONS_D3:
                msg += " ⚠️ Уязвимая версия"
        return msg
    return None
