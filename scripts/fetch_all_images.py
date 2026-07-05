"""Fetch real Wikipedia images for ALL cities, with progress saving."""
import json, urllib.request, urllib.parse, time, ssl, os, sys

os.environ["NO_PROXY"] = "en.wikipedia.org,upload.wikimedia.org,127.0.0.1"

path = "travel-app/backend/data/cities_backup.json"
d = json.load(open(path, "r", encoding="utf-8"))

headers = {"User-Agent": "Mozilla/5.0 TravelApp/1.0"}
ssl_ctx = ssl.create_default_context()

total = len(d["cities"])
found = 0

for i, c in enumerate(d["cities"]):
    name = c["name"]
    # Skip if already has a Wikipedia image
    if "upload.wikimedia" in c.get("cover_img", ""):
        found += 1
        continue
    
    try:
        # Try English Wikipedia first (better coverage for Chinese cities)
        url = ("https://en.wikipedia.org/w/api.php?action=query"
               "&prop=pageimages&format=json&piprop=original"
               "&titles=" + urllib.parse.quote(name) + ",China&redirects=1")
        req = urllib.request.Request(url, headers=headers)
        data = json.loads(urllib.request.urlopen(req, timeout=10, context=ssl_ctx).read().decode("utf-8"))
        
        img_url = None
        for pid, info in data.get("query", {}).get("pages", {}).items():
            if pid != "-1" and "original" in info:
                img_url = info["original"]["source"]
                break
        
        if img_url:
            c["cover_img"] = img_url
            found += 1
        else:
            # Try Chinese Wikipedia as fallback
            url2 = ("https://zh.wikipedia.org/w/api.php?action=query"
                    "&prop=pageimages&format=json&piprop=original"
                    "&titles=" + urllib.parse.quote(name) + "&redirects=1")
            req2 = urllib.request.Request(url2, headers=headers)
            data2 = json.loads(urllib.request.urlopen(req2, timeout=10, context=ssl_ctx).read().decode("utf-8"))
            for pid, info in data2.get("query", {}).get("pages", {}).items():
                if pid != "-1" and "original" in info:
                    c["cover_img"] = info["original"]["source"]
                    found += 1
                    break
    except Exception:
        pass
    
    # Progress save every 20 cities
    if (i + 1) % 20 == 0:
        json.dump(d, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        pct = found * 100 // (i + 1)
        sys.stdout.write(f"\rProgress: {i+1}/{total} ({found} images, {pct}%)")
        sys.stdout.flush()
    
    time.sleep(0.3)

# Final save
json.dump(d, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"\nDone! {found}/{total} cities have Wikipedia images")
