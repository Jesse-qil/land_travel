"""
Generate cover images for all cities using picsum.photos (free, fast, no API key).
Each city gets a unique seeded image.
"""
import json, urllib.parse
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "travel-app" / "backend" / "data"
path = DATA_DIR / "cities_backup.json"
data = json.loads(path.read_text(encoding="utf-8"))

for city in data["cities"]:
    name = city["name"]
    seed = urllib.parse.quote(name)
    city["cover_img"] = f"https://picsum.photos/seed/{seed}/600/400"

path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Updated {len(data['cities'])} cities with picsum.photos images")
