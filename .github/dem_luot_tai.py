"""Cộng lượt tải bản Windows (.zip) và Mac (.dmg) qua mọi phiên bản.
Số đã thấy của từng file được lưu trong luot-tai/du-lieu.json và không bao giờ giảm,
nên nâng cấp hay xoá bản cũ cũng không mất lượt tải."""
import json, os, re, urllib.request

repo, token = os.environ["REPO"], os.environ.get("GH_TOKEN", "")
data_path = "luot-tai/du-lieu.json"
saved = json.load(open(data_path, encoding="utf-8")) if os.path.exists(data_path) else {}

page = 1
while True:
    req = urllib.request.Request(f"https://api.github.com/repos/{repo}/releases?per_page=100&page={page}",
                                 headers={"Accept": "application/vnd.github+json",
                                          **({"Authorization": f"Bearer {token}"} if token else {})})
    releases = json.load(urllib.request.urlopen(req, timeout=30))
    if not releases:
        break
    for rel in releases:
        for a in rel.get("assets", []):
            name = a.get("name", "")
            os_name = "win" if re.search(r"Windows\.zip$", name) else "mac" if re.search(r"Mac\.dmg$", name) else None
            if not os_name:
                continue
            key = str(a["id"])
            old = saved.get(key, {}).get("n", 0)
            saved[key] = {"os": os_name, "ten": f'{rel.get("tag_name")}/{name}', "n": max(old, a.get("download_count", 0))}
    page += 1

win = sum(v["n"] for v in saved.values() if v["os"] == "win")
mac = sum(v["n"] for v in saved.values() if v["os"] == "mac")
fmt = lambda n: f"{n:,}".replace(",", ".")

def badge(path, label, n):
    json.dump({"schemaVersion": 1, "label": label, "message": f"{fmt(n)} lượt",
               "color": "D9B45A", "labelColor": "1B1B1E", "cacheSeconds": 1800},
              open(path, "w", encoding="utf-8"), ensure_ascii=False)

os.makedirs("luot-tai", exist_ok=True)
json.dump(saved, open(data_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
badge("luot-tai/tong.json", "Tổng lượt tải", win + mac)
badge("luot-tai/windows.json", "Windows", win)
badge("luot-tai/mac.json", "Mac", mac)
print("Windows", win, "Mac", mac)
