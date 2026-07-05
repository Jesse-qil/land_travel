"""
Fetch real city photos from Wikipedia for all cities.
Each city's Wikipedia page image is used as the cover.
"""
import json, urllib.request, urllib.parse, time, os
from pathlib import Path

os.environ["NO_PROXY"] = "zh.wikipedia.org,upload.wikimedia.org,127.0.0.1"

DATA_DIR = Path(__file__).resolve().parent.parent / "travel-app" / "backend" / "data"
path = DATA_DIR / "cities_backup.json"
data = json.loads(path.read_text(encoding="utf-8"))

HEADERS = {"User-Agent": "TravelApp/1.0 (travel-recommender)"}
total = len(data["cities"])
success = 0

for i, city in enumerate(data["cities"]):
    name = city["name"]
    encoded = urllib.parse.quote(name)
    url = f"https://zh.wikipedia.org/w/api.php?action=query&prop=pageimages&format=json&piprop=original&titles={encoded}&redirects=1"
    
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as r:
            d = json.loads(r.read().decode("utf-8"))
        
        pages = d.get("query", {}).get("pages", {})
        img_url = None
        for pid, info in pages.items():
            if pid != "-1" and "original" in info:
                img_url = info["original"]["source"]
                break
        
        if img_url:
            city["cover_img"] = img_url
            success += 1
        else:
            city["cover_img"] = f"https://picsum.photos/seed/{urllib.parse.quote(name)}/600/400"
    except Exception:
        city["cover_img"] = f"https://picsum.photos/seed/{urllib.parse.quote(name)}/600/400"
    
    if (i + 1) % 20 == 0:
        print(f"  [{i+1}/{total}] {success} images found...")
    time.sleep(0.3)

path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\nDone! {success}/{total} cities got Wikipedia images, others use picsum fallback")
