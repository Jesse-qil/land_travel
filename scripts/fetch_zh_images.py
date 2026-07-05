"""Re-fetch city images using Chinese Wikipedia for accurate results."""
import json, urllib.request, urllib.parse, time, ssl, os

os.environ["NO_PROXY"] = "zh.wikipedia.org,upload.wikimedia.org,127.0.0.1"

path = "travel-app/backend/data/cities_backup.json"
d = json.load(open(path, "r", encoding="utf-8"))

headers = {"User-Agent": "TravelApp/1.0"}
ssl_ctx = ssl.create_default_context()
found = 0

for i, c in enumerate(d["cities"][:60]):
    name = c["name"]
    try:
        url = ("https://zh.wikipedia.org/w/api.php?action=query"
               "&prop=pageimages&format=json&piprop=original"
               "&titles=" + urllib.parse.quote(name) + "&redirects=1")
        req = urllib.request.Request(url, headers=headers)
        data = json.loads(urllib.request.urlopen(req, timeout=10, context=ssl_ctx).read().decode("utf-8"))
        pages = data.get("query", {}).get("pages", {})
        img_url = None
        for pid, info in pages.items():
            if pid != "-1" and "original" in info:
                img_url = info["original"]["source"]
                break
        if img_url:
            c["cover_img"] = img_url
            found += 1
    except Exception:
        pass
    time.sleep(0.3)

json.dump(d, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"Done! {found}/60 cities updated with Chinese Wikipedia images")
