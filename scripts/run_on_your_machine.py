"""
Run this on your local machine to fetch real Wikipedia images for ALL cities.
One-time script, takes about 2 minutes.
"""
import json, urllib.request, urllib.parse, time, ssl, os
os.environ["NO_PROXY"] = "en.wikipedia.org,upload.wikimedia.org"

path = "travel-app/backend/data/cities_backup.json"
d = json.load(open(path, "r", encoding="utf-8"))
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
ssl_ctx = ssl.create_default_context()

# Use batch API - 50 cities per request
BATCH_SIZE = 50
found = sum(1 for c in d["cities"] if "upload.wikimedia" in c.get("cover_img", ""))

for batch_start in range(0, len(d["cities"]), BATCH_SIZE):
    batch = d["cities"][batch_start : batch_start + BATCH_SIZE]
    titles = "|".join(urllib.parse.quote(c["name"] + ", China") for c in batch)
    
    try:
        url = "https://en.wikipedia.org/w/api.php?action=query&prop=pageimages&format=json&piprop=original&titles=" + titles + "&redirects=1"
        req = urllib.request.Request(url, headers=headers)
        data = json.loads(urllib.request.urlopen(req, timeout=30, context=ssl_ctx).read().decode("utf-8"))
        
        # Map titles to image URLs
        for c in batch:
            if "upload.wikimedia" in c.get("cover_img", ""):
                continue
            for pid, info in data.get("query", {}).get("pages", {}).items():
                if pid != "-1" and "original" in info:
                    title = info.get("title", "").replace(", China", "")
                    if c["name"] in title or title in c["name"]:
                        c["cover_img"] = info["original"]["source"]
                        found += 1
                        break
    except Exception as e:
        print(f"Batch {batch_start} error: {e}")
    
    time.sleep(0.5)
    print(f"Progress: {found}/{len(d['cities'])} (batch {batch_start//BATCH_SIZE + 1})")
    json.dump(d, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

print(f"Done! {found}/{len(d['cities'])} cities have Wikipedia images")
