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
    choice = int(input("Введите номер модуля: "))
    return next((m for m in MODULES if m["number"] == choice), None)

def main():
    domain = input("Введите домен/URL: ").strip()
    mod_info = pick_module()
    if not mod_info:
        print("Неизвестный номер модуля")
        return
    module = importlib.import_module(f"modules.{mod_info['file']}")
    if hasattr(module, "run"):
        module.run(domain)
    else:
        print("У выбранного модуля нет функции run(domain)")

if __name__ == "__main__":
    main()
