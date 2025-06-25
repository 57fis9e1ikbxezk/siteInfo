import re
from modules.base import detect_pattern

VULNERABLE_VERSIONS_SVELTE = [
    "3.0.0",  # исторически уязвимая
    "3.12.0",  # XSS
]

def detect_svelte(js_code: str) -> bool:
    patterns = ['svelte', 'SvelteComponent']
    return bool(detect_pattern(js_code, patterns))

def detect_svelte_version(js_code: str) -> str | None:
    patterns = [
        r'svelte(?:@|\s*version\s*[:=]\s*["\'])([0-9]+\.[0-9]+\.[0-9]+)',
    ]
    for pat in patterns:
        m = re.search(pat, js_code, re.I)
        if m:
            return m.group(1)
    return None

def detect(js_code: str, headers: dict) -> str | None:
    if detect_svelte(js_code):
        version = detect_svelte_version(js_code)
        msg = "Найдено упоминание Svelte"
        if version:
            msg += f" {version}"
            if version in VULNERABLE_VERSIONS_SVELTE:
                msg += " ⚠️ Уязвимая версия"
        return msg
    return None
