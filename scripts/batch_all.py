"""Fetch real Wikimedia images for ALL cities using batch API."""
import json, urllib.request, urllib.parse, time, ssl, os
os.environ["NO_PROXY"] = "en.wikipedia.org,upload.wikimedia.org,127.0.0.1"

path = "travel-app/backend/data/cities_backup.json"
d = json.load(open(path, "r", encoding="utf-8"))
headers = {"User-Agent": "Mozilla/5.0 TravelApp/1.0"}
ssl_ctx = ssl.create_default_context()

BATCH_SIZE = 50
found = 0

# Group cities into batches of 50
cities_list = d["cities"]
for batch_start in range(0, len(cities_list), BATCH_SIZE):
    batch = cities_list[batch_start : batch_start + BATCH_SIZE]
    
    # Skip if all in batch already have Wikipedia images
    already = sum(1 for c in batch if "upload.wikimedia" in c.get("cover_img", ""))
    if already == len(batch):
        found += already
        continue
    
    # Build titles parameter (up to 50 city names)
    titles = "|".join(urllib.parse.quote(c["name"]) for c in batch)
    
    try:
        url = ("https://en.wikipedia.org/w/api.php?action=query"
               "&prop=pageimages&format=json&piprop=original"
               "&titles=" + titles + "&redirects=1")
        req = urllib.request.Request(url, headers=headers)
        data = json.loads(urllib.request.urlopen(req, timeout=30, context=ssl_ctx).read().decode("utf-8"))
        
        # Map page ID to original image URL
        page_map = {}
        for pid, info in data.get("query", {}).get("pages", {}).items():
            if pid != "-1" and "original" in info:
                page_map[pid] = info["original"]["source"]
        
        # Match back to city names via redirects/normalized titles
        norm_map = {}
        for n in data.get("query", {}).get("normalized", []):
            norm_map[n["from"]] = n["to"]
        for r in data.get("query", {}).get("redirects", []):
            norm_map[r["from"]] = r["to"]
        
        for c in batch:
            name = c["name"]
            if "upload.wikimedia" in c.get("cover_img", ""):
                found += 1
                continue
            # The API might have returned the page under the original or redirected name
            for pid, info in data.get("query", {}).get("pages", {}).items():
                title = info.get("title", "")
                if name in title or title in name:
                    if "original" in info:
                        c["cover_img"] = info["original"]["source"]
                        found += 1
                        break
    except Exception as e:
        print(f"  Batch {batch_start} failed: {e}")
    
    time.sleep(0.5)
    print(f"  Batch {batch_start//BATCH_SIZE + 1}/{(len(cities_list)+BATCH_SIZE-1)//BATCH_SIZE}: {found} images")

json.dump(d, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"\nDone! {found}/{len(cities_list)} cities have real Wikipedia images")
