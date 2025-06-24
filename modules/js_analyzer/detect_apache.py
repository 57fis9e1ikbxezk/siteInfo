from .base import detect_pattern

def detect_apache_license(js_code: str) -> bool:
    patterns = ['Apache License', 'SPDX-License-Identifier: Apache-2.0']
    return bool(detect_pattern(js_code, patterns))

def detect(js_code: str, headers: dict) -> str | None:
    if detect_apache_license(js_code):
        return "Найдена лицензия Apache"
    return None