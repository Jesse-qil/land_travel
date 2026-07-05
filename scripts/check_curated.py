import json, re
d = json.load(open("travel-app/backend/data/cities_backup.json", "r", encoding="utf-8"))
text = open("scripts/curated_images.py", "r", encoding="utf-8").read()
curated = set(re.findall(r'"([\u4e00-\u9fff]+)": "https://upload\\.wikimedia', text))
print("Curated count:", len(curated))
for c in d["cities"][:60]:
    if c["name"] not in curated:
        print("  MISSING:", c["name"])
