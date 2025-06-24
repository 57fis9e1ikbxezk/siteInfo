import os
import requests, math
import fake_useragent
import importlib
import pkgutil
from urllib.parse import urlparse
from pathlib import Path

def _load_proxies() -> list[str]:
    proxy_file = Path("proxies.txt")
    if proxy_file.exists():
        with proxy_file.open("r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    else:
        return []

def _parse_proxy(line: str) -> dict[str, str]:
    host, port, protocol, *rest = line.split(":")
    creds = f"{rest[0]}:{rest[1]}@" if len(rest) == 2 and rest[0] else ""
    url = f"{protocol}://{creds}{host}:{port}"
    return {"http": url, "https": url}

_DETECTORS = []
cms_folder = os.path.join(os.path.dirname(__file__))
for _, mod_name, is_pkg in pkgutil.iter_modules([cms_folder]):
    if not is_pkg:
        try:
            mod = importlib.import_module(f"{__name__}.{mod_name}")
            if hasattr(mod, "detect"):
                _DETECTORS.append(mod.detect)
        except Exception as e:
            print(f"⚠️ Не удалось загрузить {mod_name}: {e}")

def _detect(domain: str, session: requests.Session) -> dict:
    results = []
    for d in _DETECTORS:
        try:
            res = d(domain, session)
            if res:
                print(f"\n📘 CMS: {res.get('cms')}")
                print(f"🔢 Версия: {res.get('version') or 'не определена'}")
                match res.get("vulnerable"):
                    case True:
                        print("🚨 Уязвимость: обнаружена")
                    case False:
                        print("✅ Уязвимость: не обнаружена")
                    case _:
                        print("⚠️ Уязвимость: неизвестно")
                if "details" in res:
                    print(f"ℹ️ Подробности: {res['details']}")
                results.append(res)
        except Exception as e:
            print(f"Ошибка в {d.__name__}: {e}")
    if results:
        return results
    print("❌ CMS не определена.")
    return {"cms": "Unknown"}

def send_telegram_message(token: str, chat_id: int, text: str):
    max_len = 1024
    chunks = [text[i:i+max_len] for i in range(0, len(text), max_len)]
    for chunk in chunks:
        resp = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data={"chat_id": chat_id, "text": chunk}
        )
        if not resp.ok:
            print(f"Telegram API error: {resp.status_code}, {resp.text}")

def run(domain: str, tg_token: str, tg_chat: int) -> None:
    if not domain.startswith(("http://", "https://")):
        domain = "https://" + domain

    ua = fake_useragent.UserAgent().random

    for line in _load_proxies():
        try:
            proxies = _parse_proxy(line)
        except ValueError:
            print(f"Неверный формат прокси: {line}")
            continue

        print(f"Попытка подключения: {proxies['http']}")

        with requests.Session() as s:
            s.proxies = proxies
            s.headers.update({"User-Agent": ua})
            try:
                s.get(domain, timeout=10).raise_for_status()
                print(f"Успешное подключение к: {proxies['http']}")
                result = _detect(domain, s)
                if tg_token and tg_chat and result:
                    try:
                        msg = f"📡 CMS-скан сайта: {domain}\n"
                        if isinstance(result, list):
                            for idx, item in enumerate(result, 1):
                                if not isinstance(item, dict):
                                    print(result)
                                    continue
                                msg += f"\n🧩 CMS #{idx}\n"
                                msg += f"📘 CMS: {item.get('cms')}\n"
                                msg += f"🔢 Версия: {item.get('version') or 'не определена'}\n"
                                match item.get("vulnerable"):
                                    case True:
                                        msg += "🚨 Уязвимость: обнаружена\n"
                                    case False:
                                        msg += "✅ Уязвимость: не обнаружена\n"
                                    case _:
                                        msg += "⚠️ Уязвимость: неизвестно\n"
                                if "details" in item:
                                    msg += f"ℹ️ Подробности: {item['details']}\n"
                        else:
                            msg += f"📘 CMS: {result.get('cms')}\n"
                            msg += f"🔢 Версия: {result.get('version') or 'не определена'}\n"
                            match result.get("vulnerable"):
                                case True:
                                    msg += "🚨 Уязвимость: обнаружена\n"
                                case False:
                                    msg += "✅ Уязвимость: не обнаружена\n"
                                case _:
                                    msg += "⚠️ Уязвимость: неизвестно\n"
                            if "details" in result:
                                msg += f"ℹ️ Подробности: {result['details']}\n"
                        send_telegram_message(tg_token, tg_chat, msg)
                    except Exception as e:
                        print(f"Ошибка при отправке сообщения в Telegram: {e}")
                return
            except Exception as e:
                print(f"ошибка: {proxies['http']}: {e}")

    print("❌ Все прокси нерабочие.")
