import os, re, mimetypes, queue, uuid, warnings, requests, fake_useragent
from pathlib import Path
from urllib.parse import urlparse, urljoin, unquote, urlunparse
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

MAX_URLS = 100000
MAX_SIZE_MB = 12400
SESSION_TIMEOUT = 15

COMMON_FILES = [
    ".env", ".git/config", ".gitignore", "composer.json", "composer.lock", "package.json", "package-lock.json",
    "yarn.lock", "config.php", "wp-config.php", "local.xml", "settings.py", "settings.php", "database.sql",
    "backup.sql", "dump.sql", "backup.zip", "backup.tar.gz", "backup.tar", "db.sqlite3", "db.sql", "adminer.php",
    "phpinfo.php", "robots.txt", ".htaccess", ".well-known/security.txt", ".DS_Store", "Thumbs.db", "web.config",
    "crossdomain.xml", "config.json", "settings.ini", "setup.py", "install.php"
]

def _load_proxies():
    p = Path("proxies.txt")
    return [l.strip() for l in p.read_text().splitlines() if l.strip()] if p.exists() else []

def _parse_proxy(line: str):
    parts = line.split(":")
    if len(parts) < 3:
        return {}
    host, port, proto = parts[:3]
    creds = f"{parts[3]}:{parts[4]}@" if len(parts) == 5 else ""
    u = f"{proto}://{creds}{host}:{port}"
    return {"http": u, "https": u}

def _ua():
    try:
        return fake_useragent.UserAgent().random
    except Exception:
        return "Mozilla/5.0 (compatible; SiteDownloader/1.0)"

def _normalize_url(u: str):
    p = urlparse(u)
    scheme = p.scheme or "https"
    netloc = p.netloc
    path = p.path or "/"
    if path.endswith("/index.html"):
        path = path[:-11] + "/"
    return urlunparse((scheme, netloc, path, "", "", ""))

def _local_path(output_dir: Path, u: str):
    up = urlparse(u)
    path = unquote(up.path)
    if path.endswith("/"):
        path += "index.html"
    if path.startswith("/"):
        path = path[1:]
    local = output_dir / path
    local.parent.mkdir(parents=True, exist_ok=True)
    return local

def _unique_path(p: Path):
    if not p.exists():
        return p
    stem, suffix = p.stem, p.suffix
    for i in range(1, 10000):
        np = p.with_name(f"{stem}_{i}{suffix}")
        if not np.exists():
            return np
    return p.with_name(f"{stem}_{uuid.uuid4().hex}{suffix}")

def _save(resp, out_path: Path):
    out_path.write_bytes(resp.content)
    print(f"Сохранён файл: {out_path}")

def _extract_urls_from_css(base: str, css_text: str):
    urls = set()
    for m in re.findall(r"url\(([^)]+)\)", css_text):
        href = m.strip().strip("'").strip('"')
        urls.add(urljoin(base, href))
    for m in re.findall(r"@import\s+(?:url\()?['\"]([^'\"]+)['\"]", css_text):
        urls.add(urljoin(base, m))
    return urls

def _extract_links(base: str, html: str):
    soup = BeautifulSoup(html, "lxml")
    links = set()
    for tag, attr in [("a", "href"), ("link", "href"), ("script", "src"), ("img", "src"), ("source", "src"), ("video", "src"), ("audio", "src")]:
        for t in soup.find_all(tag):
            v = t.get(attr)
            if v:
                links.add(urljoin(base, v))
    for t in soup.find_all(style=True):
        links.update(_extract_urls_from_css(base, t["style"]))
    for s in soup.find_all("style"):
        if s.string:
            links.update(_extract_urls_from_css(base, s.string))
    if "Index of" in html and "<a href" in html:
        for a in soup.find_all("a"):
            href = a.get("href")
            if href and href not in ("../", "/"):
                links.add(urljoin(base, href))
    return links

def _guess_type(path: Path):
    mt, _ = mimetypes.guess_type(str(path))
    return mt or "application/octet-stream"

def _download(s: requests.Session, u: str, out: Path, non_media_list: list):
    r = s.get(u, timeout=SESSION_TIMEOUT)
    r.raise_for_status()
    p = _unique_path(_local_path(out, u))
    _save(r, p)
    ctype = r.headers.get("Content-Type", _guess_type(p)).lower()
    if not any(x in ctype for x in ("text/html", "text/css", "image", "video", "audio", "font", "application/javascript")):
        non_media_list.append(str(p.relative_to(out)))
    size = len(r.content)
    if not any(p.suffix.lower().endswith(x) for x in [".html", ".htm", ".css", ".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".mp4", ".mp3", ".wav", ".ogg", ".webm"]):
        with (out / "non_media_files.txt").open("a", encoding="utf-8") as f:
            f.write(str(p) + "\n")

    return size, ctype, r.text if "text/html" in ctype or ".html" in u else ""

def _crawl(s: requests.Session, start: str, out: Path, domain: str, non_media_list: list):
    q: queue.Queue[str] = queue.Queue()
    q.put(start)
    seen = set()
    total = 0
    count = 0
    limit = MAX_SIZE_MB * 1024 * 1024
    while not q.empty() and count < MAX_URLS and total < limit:
        u = _normalize_url(q.get())
        if u in seen:
            continue
        seen.add(u)
        try:
            size, ctype, html = _download(s, u, out, non_media_list)
            total += size
            count += 1
            if html:
                for link in _extract_links(u, html):
                    n = _normalize_url(link)
                    if urlparse(n).netloc == domain and n not in seen:
                        q.put(n)
        except Exception:
            continue

def _try_common(s: requests.Session, base: str, out: Path, non_media_list: list):
    root = base if base.endswith("/") else base + "/"
    for f in COMMON_FILES:
        u = urljoin(root, f)
        try:
            _download(s, u, out, non_media_list)
        except Exception:
            pass

def run(domain: str):
    if not domain.startswith(("http://", "https://")):
        domain = "https://" + domain
    parsed = urlparse(domain)
    base_domain = parsed.netloc
    out_dir = Path(base_domain)
    out_dir.mkdir(exist_ok=True)
    proxies = _load_proxies() or [None]
    non_media = []
    for pr in proxies:
        cfg = _parse_proxy(pr) if pr else {}
        try:
            with requests.Session() as s:
                s.proxies = cfg
                s.headers["User-Agent"] = _ua()
                s.get(domain, timeout=SESSION_TIMEOUT).raise_for_status()
                _try_common(s, domain, out_dir, non_media)
                _crawl(s, domain, out_dir, base_domain, non_media)
                break
        except Exception:
            continue
    if non_media:
        (out_dir / "non_media_files.txt").write_text("\n".join(non_media))
        print(f"Записан список непрофильных файлов: {out_dir / 'non_media_files.txt'}")
    else:
        print("Нет непрофильных файлов для записи.")
