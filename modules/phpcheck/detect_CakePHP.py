import re
from modules.base import detect_pattern

VULNERABLE_VERSIONS_CAKEPHP = [
    "2.0.0", "2.10.0", "3.0.0", "3.8.0"
]

def detect_cakephp(js_code: str, headers: dict) -> bool:
    patterns = ['CakePHP', 'cakephp']
    return bool(detect_pattern(js_code, patterns))

def detect_cakephp_version(js_code: str) -> str | None:
    patterns = [
        r'cakephp(?:@|\s*version\s*[:=]\s*["\'])([0-9]+\.[0-9]+\.[0-9]+)',
        r'CakePHP v?(\d+\.\d+\.\d+)'
    ]
    for pat in patterns:
        m = re.search(pat, js_code, re.I)
        if m:
            return m.group(1)
    return None

def detect(js_code: str, headers: dict) -> str | None:
    if detect_cakephp(js_code, headers):
        version = detect_cakephp_version(js_code)
        msg = "Найдено упоминание CakePHP"
        if version:
            msg += f" {version}"
            if version in VULNERABLE_VERSIONS_CAKEPHP:
                msg += " ⚠️ Уязвимая версия"
        return msg
    return None
