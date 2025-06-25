from modules.base import detect_pattern

def detect_zonejs(js_code: str) -> bool:
    patterns = ['Zone', 'ZoneAwarePromise', 'zoneDelegate']
    return bool(detect_pattern(js_code, patterns))

def detect(js_code: str, headers: dict) -> str | None:
    if detect_zonejs(js_code):
        return "Найдено упоминание Zone(ZoneAwarePromise, zoneDelegate)"
    return None