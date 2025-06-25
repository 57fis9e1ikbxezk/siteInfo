import re
import modules
from modules.base import detect_pattern

VULNERABLE_VERSIONS_RAILS = [
    "3.0.0", "3.2.0", "4.0.0", "4.2.0"
]

def detect_rails(js_code: str, headers: dict) -> bool:
    patterns = ['Rails', 'Ruby on Rails']
    return bool(detect_pattern(js_code, patterns))

def detect_rails_version(js_code: str) -> str | None:
    patterns = [
        r'rails(?:@|\s*version\s*[:=]\s*["\'])([0-9]+\.[0-9]+\.[0-9]+)',
        r'Rails v?(\d+\.\d+\.\d+)'
    ]
    for pat in patterns:
        m = re.search(pat, js_code, re.I)
        if m:
            return m.group(1)
    return None

def detect(js_code: str, headers: dict) -> str | None:
    if detect_rails(js_code, headers):
        version = detect_rails_version(js_code)
        msg = "Найдено упоминание Ruby on Rails"
        if version:
            msg += f" {version}"
            if version in VULNERABLE_VERSIONS_RAILS:
                msg += " ⚠️ Уязвимая версия"
        return msg
    return None
