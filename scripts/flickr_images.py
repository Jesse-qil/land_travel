"""All cities get real Flickr photos via loremflickr.com."""
import json, urllib.parse

path = "travel-app/backend/data/cities_backup.json"
d = json.load(open(path, "r", encoding="utf-8"))

# Keep existing Wikipedia curated images, rest use loremflickr
count = 0
for c in d["cities"]:
    name = c["name"]
    # Keep existing Wikipedia image if already set
    if "upload.wikimedia" in c.get("cover_img", ""):
        count += 1
        continue
    # Use loremflickr which returns real Flickr photos matching the city name
    c["cover_img"] = "https://loremflickr.com/600/400/" + urllib.parse.quote(name) + "?random=" + str(hash(name) % 10000)

json.dump(d, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"Done! {count} Wikipedia + {len(d['cities'])-count} Flickr = {len(d['cities'])} total cities with real photos")
