import json, urllib.request, time

# Check backend city data + image URLs
d = json.loads(urllib.request.urlopen("http://127.0.0.1:8000/api/cities?size=5").read())
for c in d["data"]["items"]:
    name = c["name"]
    url = c["cover_img"]
    print(f"City: {name[:4]} | has_url: {bool(url)}")
    if url:
        t0 = time.time()
        try:
            r = urllib.request.urlopen(url, timeout=8)
            size = len(r.read())
            print(f"  HTTP {r.status} | {r.headers.get('Content-Type','?')} | {size}B | {time.time()-t0:.1f}s")
        except Exception as e:
            print(f"  FAIL: {type(e).__name__}")
