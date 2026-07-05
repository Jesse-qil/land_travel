"""
Generate inline SVG cover images for all cities.
Each city gets a unique colored gradient with its name.
"""
import json, hashlib
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "travel-app" / "backend" / "data"
path = DATA_DIR / "cities_backup.json"
data = json.loads(path.read_text(encoding="utf-8"))

# Color palette for gradients
PALETTE = [
    ("#667eea", "#764ba2"), ("#f093fb", "#f5576c"), ("#4facfe", "#00f2fe"),
    ("#43e97b", "#38f9d7"), ("#fa709a", "#fee140"), ("#a18cd1", "#fbc2eb"),
    ("#fccb90", "#d57eeb"), ("#e0c3fc", "#8ec5fc"), ("#f5576c", "#ff6f91"),
    ("#30cfd0", "#330867"), ("#a1c4fd", "#c2e9fb"), ("#667db6", "#0082c8"),
    ("#1fa2ff", "#12d8fa"), ("#fa8bff", "#2bd2ff"), ("#ff758c", "#ff7eb3"),
    ("#3a1c71", "#d76d77"), ("#00b4db", "#0083b0"), ("#73fa79", "#0cce6b"),
    ("#fc5c7d", "#6a82fb"), ("#00c9ff", "#92fe9d"),
]

def hash_color(name):
    h = hashlib.md5(name.encode()).hexdigest()
    idx = int(h[:8], 16) % len(PALETTE)
    return PALETTE[idx]

def make_svg(name):
    c1, c2 = hash_color(name)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="400" viewBox="0 0 600 400">
  <defs>
    <linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{c1}"/>
      <stop offset="100%" style="stop-color:{c2}"/>
    </linearGradient>
  </defs>
  <rect width="600" height="400" fill="url(#g)"/>
  <text x="300" y="180" text-anchor="middle" font-size="80" font-weight="bold" fill="rgba(255,255,255,0.2)" font-family="sans-serif">{name[0]}</text>
  <text x="300" y="240" text-anchor="middle" font-size="22" fill="rgba(255,255,255,0.5)" font-family="sans-serif">{name}</text>
</svg>'''
    return "data:image/svg+xml;base64," + svg.encode("utf-8").hex()
    # Actually, let me use proper base64
    import base64
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode()

for city in data["cities"]:
    name = city["name"]
    city["cover_img"] = make_svg(name)

path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Generated SVG images for {len(data['cities'])} cities")
