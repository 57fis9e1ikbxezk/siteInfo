import re
from modules.base import detect_pattern

KNOWN_VULNERABLE_VERSIONS = [
    "2.0.0",  # исторически уязвимая
    "5.0.0", "5.8.0",  # XSS
    "7.14.1",  # token leakage
    "8.2.3",   # DoS
    "8.10.0",  # auth bypass
]

def detect_firebase(js_code: str) -> bool:
    patterns = ['firebase', 'FIREBASE_REMOTE_CONFIG_URL_BASE', 'firebaseapp.com']
    return bool(detect_pattern(js_code, patterns))

def detect_firebase_version(js_code: str) -> str | None:
    patterns = [
        r'@firebase/app:\s*([0-9]+\.[0-9]+\.[0-9]+)',
        r'firebase(?:@|\s*version\s*[:=]\s*["\'])([0-9]+\.[0-9]+\.[0-9]+)',
        r'version\s*[:=]\s*["\']([0-9]+\.[0-9]+\.[0-9]+)["\']'
    ]
    for pat in patterns:
        m = re.search(pat, js_code, re.I)
        if m:
            return m.group(1)
    return None

def detect(js_code: str, headers: dict) -> str | None:
    if detect_firebase(js_code):
        version = detect_firebase_version(js_code)
        msg = "Найдено упоминание Firebase"
        if version:
            msg += f" {version}"
            if version in KNOWN_VULNERABLE_VERSIONS:
                msg += " ⚠️ Уязвимая версия"
        return msg
    return None
