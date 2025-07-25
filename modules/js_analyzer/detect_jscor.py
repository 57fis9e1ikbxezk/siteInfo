import re
import os
import json
from pathlib import Path
from modules.base import detect_pattern

MAX_VERSION = 6

def detect_jscor(js_code: str) -> bool:
    patterns = ['jscor', 'JSCor', 'jsCor', 'jsc']
    return bool(detect_pattern(js_code, patterns))

def detect_jscor_version(js_code: str) -> str | None:
    match = re.search(r'jscor version:? (\d+\.\d+\.\d+)', js_code, re.I)
    if match:
        return match.group(1)
    return None

def detect_in_package_json(file_path: str) -> str | None:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            json_data = json.load(file)
            if 'dependencies' in json_data and 'jscor' in json_data['dependencies']:
                return f"JSCor найден в {file_path}"
    except Exception as e:
        return f"Ошибка при обработке файла: {e}"
    return None

def check_for_jscor_file(directory: str) -> str | None:
    for root, dirs, files in os.walk(directory):
        if 'jscor.js' in files:
            return f"Файл jscor.js найден в {root}"
    return None

def detect(js_code: str, headers: dict, file_paths: list) -> str | None:
    if detect_jscor(js_code):
        msg = "Найдено упоминание JSCor"
        version = detect_jscor_version(js_code)
        if version:
            msg += f" {version}"
            try:
                major = int(version.split(".")[0])
                if major < MAX_VERSION:
                    msg += " ⚠️ Версия JSCor уязвима"
            except ValueError:
                pass
        return msg

    for file_path in file_paths:
        result = detect_in_package_json(file_path)
        if result:
            return result

    for file_path in file_paths:
        if os.path.isdir(file_path):
            result = check_for_jscor_file(file_path)
            if result:
                return result

    return None
