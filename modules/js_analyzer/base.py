def detect_pattern(content: str, patterns: list[str]) -> list[str]:
    found = []
    for p in patterns:
        if p.lower() in content.lower():
            found.append(p)
    return found
