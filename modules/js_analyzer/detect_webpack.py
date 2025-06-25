import re
from modules.base import detect_pattern

MAX_VERSION = 6

def detect_webpack(js_code: str) -> bool:
    patterns = ['webpackChunk', '__webpack_require__', 'webpackJsonp']
    return bool(detect_pattern(js_code, patterns))

def detect_webpack_version(js_code: str) -> str | None:
    match = re.search(r'webpack version:? (\d+\.\d+\.\d+)', js_code, re.I)
    if match:
        return match.group(1)
    return None

def detect(js_code: str, headers: dict) -> str | None:
    if detect_webpack(js_code):
        msg = "Найдено упоминание Webpack"
        version = detect_webpack_version(js_code)
        if version:
            msg += f" {version}"
            try:
                major = int(version.split(".")[0])
                if major < MAX_VERSION:
                    msg += " ⚠️ Версия webpack уязвима"
            except ValueError:
                pass
        return msg
    return None
