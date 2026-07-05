import json
d = json.load(open("travel-app/backend/data/cities_backup.json", "r", encoding="utf-8"))
print("Total:", len(d["cities"]))
print("With tags:", sum(1 for c in d["cities"] if c["tags"]))
for c in d["cities"][:5]:
    print(" ", c["name"], c["tags"], c["plan_days"])
print("  ...")
for c in d["cities"][-3:]:
    print(" ", c["name"], c["tags"])
