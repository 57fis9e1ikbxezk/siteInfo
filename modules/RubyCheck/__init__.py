import os
import pkgutil
import importlib
import requests
import modules
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import fake_useragent

_DETECTORS = []

def _load_proxies() -> list[str]:
    p = Path("proxies.txt")
    if not p.exists():
        print("⚠️  Файл proxies.txt не найден, работаем без прокси")
        return []
    print("📖  Загружаю список прокси из proxies.txt")
    lines = [l.strip() for l in p.read_text().splitlines() if l.strip()]
    print(f"🔢  Найдено {len(lines)} строк(и) прокси")
    return lines

def _parse_proxy(line: str) -> dict[str, str] | None:
    try:
        host, port, proto, *rest = line.split(":")
    except ValueError:
        print(f"❌  Неверный формат строки прокси: {line}")
        return None
    creds = ""
    if len(rest) == 2:
        user, pwd = rest
        creds = f"{user}:{pwd}@"
    proxy_url = f"{proto}://{creds}{host}:{port}"
    return {"http": proxy_url, "https": proxy_url}

def add_detectors():
    if _DETECTORS:
        return
    folder = Path(__file__).parent
    package = __package__ or ""
    print("🔍  Ищу детекторы в директории", folder)
    for _, mod_name, is_pkg in pkgutil.iter_modules([folder]):
        if is_pkg:
            continue
        full_name = f"{package}.{mod_name}" if package else mod_name
        try:
            mod = importlib.import_module(full_name)
            if hasattr(mod, "detect"):
                _DETECTORS.append(mod.detect)
                print(f"✅  Детектор '{full_name}' загружен")
            else:
                print(f"⚠️  Модуль '{full_name}' без функции detect")
        except Exception as e:
            print(f"❌  Ошибка при импорте '{full_name}': {e}")

def _collect_ruby(url: str, s: requests.Session) -> tuple[str, dict]:
    print(f"🌐  GET {url}")
    r = s.get(url, timeout=10)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")
    
    code = []
    
    for tag in soup.find_all("a"):
        href = tag.get("href")
        if href and href.endswith(".rb"): 
            ruby_url = urljoin(url, href)
            try:
                print(f"📥  Скачиваю Ruby {ruby_url}")
                ruby_code = s.get(ruby_url, timeout=7).text
                code.append(ruby_code)
            except Exception as e:
                print(f"⚠️  Не удалось скачать {ruby_url}: {e}")

    print(f"🗂️  Собрано {len(code)} Ruby фрагментов")
    return "\n".join(code), r.headers

def run(domain: str, tg_token: str, tg_chat: int) -> None:
    if not domain.startswith(("http://", "https://")):
        domain = "https://" + domain

    ua = None
    if fake_useragent:
        try:
            ua = fake_useragent.UserAgent().random
            print("🕶️  Случайный User-Agent:", ua)
        except Exception as e:
            print("⚠️  Не удалось сгенерировать User-Agent:", e)

    proxies_list = _load_proxies()
    if not proxies_list:
        proxies_list = [None]  

    add_detectors()
    if not _DETECTORS:
        print("❌  Нет ни одного загруженного детектора – выходим")
        return

    for line in proxies_list:
        proxies = _parse_proxy(line) if line else None
        print("🚀  Пробую прокси:", proxies or "БЕЗ ПРОКСИ")
        with requests.Session() as s:
            if proxies:
                s.proxies = proxies
            if ua:
                s.headers.update({"User-Agent": ua})
            try:
                ruby, headers = _collect_ruby(domain, s)
            except Exception as e:
                print(f"⚠️  Ошибка при скачивании сайта через прокси {proxies}: {e}")
                continue

            found = False
            reses = []
            for detector in _DETECTORS:
                try:
                    res = detector(ruby, headers)
                    if res:
                        print(f"🎯  Детектор {detector.__module__} нашёл: {res}")
                        reses += res + " "
                        found = True
                except Exception as e:
                    print(f"⚠️  Детектор {detector.__module__} упал: {e}")

            if found:
                print("🏁  Готово, останавливаю цикл")
                if tg_token and tg_chat:
                    try:
                        print(f"📡 Отправляю в Telegram чат {tg_chat}")
                        modules.telegram.send_message(tg_token, tg_chat, f"Найдены ruby фреймы для сайта: {domain}\n" + "".join(map(str, reses)))
                    except Exception as e:
                        print(f"Ошибка при отправки сообщения в телеграмм: {e}")
                return

    print("😔  Все прокси нерабочие или детекторы ничего не нашли")
