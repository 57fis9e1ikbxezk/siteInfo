import re
from .base import detect_pattern

# Это универсальный модуль. Его расширение - нужно. Отправляйте в исешках коды если хотите больше возможностей софта и не делать ничего сами

VULNERABLE_VERSIONS = {
    "React": [
        "16.0.0", "16.8.0", "16.12.0", "17.0.0", "17.0.1"
    ],
    "Angular": [
        "2.0.0", "4.0.0", "4.3.6", "5.0.0", "5.2.0", "6.0.0", "7.2.15", "8.0.0"
    ],
    "Vue": [
        "2.0.0", "2.1.8", "2.5.16", "2.6.10", "3.0.0", "3.2.0"
    ],
    "Ember": [
        "1.10.0", "2.13.3", "2.16.0", "3.4.4", "3.8.1"
    ],
    "Backbone": [
        "1.1.2", "1.2.0", "1.3.3"
    ]
}


FRAMEWORKS = {
    "Angular": ["platformBrowser", "NgModule", "angularfire2"],
    "React": ["React.createElement", "ReactDOM", "react-dom"],
    "Vue": ["new Vue", "Vue.component", "vue.runtime"],
    "Svelte": ["$$render", "$$result"],
    "Ember": ["Ember.Application", "ember.js"],
    "Backbone": ["Backbone.View", "Backbone.Model"],
    "Alpine.js": ["Alpine.start", "x-data"],
    "Next.js": ["__NEXT_DATA__"],
    "Nuxt.js": ["window.__NUXT__"]
}

VERSION_PATTERNS = {
    "React": [r"React v(\d+\.\d+\.\d+)", r"react@(\d+\.\d+\.\d+)"],
    "Angular": [r"Angular v(\d+\.\d+\.\d+)", r"angular@(\d+\.\d+\.\d+)"],
    "Vue": [r"Vue(?:\.js)? v?(\d+\.\d+\.\d+)"],
}

def detect_frameworks(js_code: str) -> dict:
    found = {}
    for name, patterns in FRAMEWORKS.items():
        if detect_pattern(js_code, patterns):
            found[name] = True
    return found

def detect_framework_versions(js_code: str, found_frameworks: dict) -> dict:
    versions = {}
    for fw in found_frameworks:
        for pat in VERSION_PATTERNS.get(fw, []):
            m = re.search(pat, js_code, re.I)
            if m:
                versions[fw] = m.group(1)
                break
    return versions

def detect(js_code: str, headers: dict) -> str | None:
    frameworks = detect_frameworks(js_code)
    if not frameworks:
        return None

    versions = detect_framework_versions(js_code, frameworks)

    results = []
    for fw in frameworks:
        version_info = ""
        if fw in versions:
            version = versions[fw]
            version_info = f" {version}"
            if fw in VULNERABLE_VERSIONS and version in VULNERABLE_VERSIONS[fw]:
                version_info += " ⚠️ уязвимая версия"
        results.append(f"{fw}{version_info}")

    return f"🔍 Обнаружены JS-фреймворки: {', '.join(results)}"
