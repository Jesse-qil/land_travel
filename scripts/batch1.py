"""Batch process city images: first 100 cities."""
import json, urllib.request, urllib.parse, time, ssl, os
os.environ["NO_PROXY"] = "en.wikipedia.org,upload.wikimedia.org,127.0.0.1"

path = "travel-app/backend/data/cities_backup.json"
d = json.load(open(path, "r", encoding="utf-8"))
headers = {"User-Agent": "Mozilla/5.0"}
ssl_ctx = ssl.create_default_context()

start, end = 0, 100
found = 0
for i in range(start, end):
    c = d["cities"][i]
    if "upload.wikimedia" in c.get("cover_img", ""):
        found += 1
        continue
    try:
        url = "https://en.wikipedia.org/w/api.php?action=query&prop=pageimages&format=json&piprop=original&titles=" + urllib.parse.quote(c["name"]) + "&redirects=1"
        req = urllib.request.Request(url, headers=headers)
        data = json.loads(urllib.request.urlopen(req, timeout=8, context=ssl_ctx).read().decode("utf-8"))
        for p, v in data.get("query", {}).get("pages", {}).items():
            if p != "-1" and "original" in v:
                c["cover_img"] = v["original"]["source"]
                found += 1
                break
    except:
        pass
    time.sleep(0.15)

json.dump(d, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"Batch {start}-{end}: {found} images")
