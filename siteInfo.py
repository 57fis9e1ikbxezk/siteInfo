import importlib

MODULES = [
    {"number": 1, "name": "CMS-Краулер", "file": "cmsCheck"},
    {"number": 2, "name": "JS-анализ", "file": "js_analyzer"},
    {"number": 3, "name": "Парсер Доступных Данных", "file": "parser"},
]

def pick_module():
    print("Доступные модули:")
    for m in MODULES:
        print(f"{m['number']}. {m['name']}")
    print("100. Все модули поочереди")
    while True:
        try:
            choice = int(input("Введите номер модуля: "))
            if choice == 100 or any(m["number"] == choice for m in MODULES):
                return choice
            else:
                print("Неизвестный номер модуля, попробуйте ещё раз.")
        except ValueError:
            print("Пожалуйста, введите число.")

def run_module(module_file, domain, tg_token, tg_chat):
    module = importlib.import_module(f"modules.{module_file}")
    if hasattr(module, "run"):
        module.run(domain, tg_token, tg_chat)
    else:
        print(f"У модуля {module_file} нет функции run(domain)")

def main():
    domains_input = input("Введите домен/URL или список доменов через запятую: ").strip()
    domains = [d.strip() for d in domains_input.split(",") if d.strip()]
    if not domains:
        print("Домен не введён")
        return
    print("Получить инфо об уведомлениях в Telegram — введите `info` при вводе токена.")

    tg_token = None
    while True:
        tg_token_input = input("Введите токен Telegram-бота (или нажмите Enter, чтобы пропустить): ").strip()
        if tg_token_input.lower() == "info":
            print("\nУведомления в Telegram отправляются при:\n"
                "1) Обнаружении реального конфигурационного файла\n"
                "2) Определении CMS сайта\n"
                "3) Обнаружении JavaScript/Framework технологий\n")
        elif tg_token_input:
            tg_token = tg_token_input
            break
        else:
            break

    tg_chat = None
    if tg_token:
        tg_chat_input = input("Введите ID Telegram-чата (или нажмите Enter, чтобы пропустить): ").strip()
        if tg_chat_input:
            try:
                tg_chat = int(tg_chat_input)
            except ValueError:
                print("⚠️  Неверный формат ID чата. Уведомления отключены.")
                tg_token = None
                tg_chat = None

    choice = pick_module()

    if choice == 100:
        for domain in domains:
            print(f"\nОбработка домена: {domain} всеми модулями")
            for m in MODULES:
                run_module(m["file"], domain, tg_token, tg_chat)
    else:
        mod_info = next(m for m in MODULES if m["number"] == choice)
        for domain in domains:
            print(f"\nОбработка домена: {domain} модулем {mod_info['name']}")
            run_module(mod_info["file"], domain, tg_token, tg_chat)

if __name__ == "__main__":
    main()
