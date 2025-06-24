import re

KNOWN_VULNERABLE_VERSIONS = [
    "4.5.0",  
]

def detect_swiper(css_code: str) -> bool:
    patterns = ['swiper', 'Swiper', 'idangero.us/swiper']
    return any(pattern in css_code for pattern in patterns)

def detect_swiper_version(css_code: str) -> str | None:
    patterns = [
        r'Swiper\s+([0-9]+\.[0-9]+\.[0-9]+)', 
        r'@import\s+["\'].*swiper.*["\']',
        r'\/\*\s*Swiper\s+([0-9]+\.[0-9]+\.[0-9]+)\s*\*\/'
    ]
    for pat in patterns:
        m = re.search(pat, css_code, re.I)
        if m:
            return m.group(1)
    return None

def detect(css_code: str, headers: dict) -> str | None:
    if detect_swiper(css_code):
        version = detect_swiper_version(css_code)
        msg = "Найдено упоминание Swiper"
        if version:
            msg += f" {version}"
            if version in KNOWN_VULNERABLE_VERSIONS:
                msg += " ⚠️ Уязвимая версия"
        return msg
    return None