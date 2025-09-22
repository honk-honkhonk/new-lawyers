import hashlib, json, os, re, time
from pathlib import Path
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).parent
TARGETS = json.loads(
    json.dumps(__import__("yaml").safe_load(open(ROOT/"targets.yaml")))
)

def clean_text(html, selector=None):
    soup = BeautifulSoup(html, "html.parser")
    if selector:
        hit = soup.select_one(selector)
        soup = BeautifulSoup(str(hit or ""), "html.parser")
    # remove script/style/nav/footer
    for t in soup(["script","style","noscript"]): t.decompose()
    text = soup.get_text("\n", strip=True)
    # collapse blank lines
    text = re.sub(r"\n{2,}", "\n", text).strip()
    return text

def slug(s): 
    return re.sub(r"[^a-z0-9]+","-", s.lower()).strip("-")

out = ROOT / "data"
out.mkdir(exist_ok=True)

changed = False
ua = {"User-Agent":"git-scrape/1.0 (+https://github.com/)"}
for t in TARGETS:
    url, sel = t["url"], t.get("select")
    r = requests.get(url, headers=ua, timeout=30)
    r.raise_for_status()
    text = clean_text(r.text, sel)
    fname = out / f"{slug(url)}.txt"
    old = fname.read_text() if fname.exists() else ""
    if text != old:
        fname.write_text(text)
        print("CHANGED:", url)
        changed = True
    else:
        print("no change:", url)

open(out/"_last_run.txt","w").write(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
exit(0 if changed else 0)

