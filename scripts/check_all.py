"""Check all services and verify SVG rendering."""
import urllib.request, json, re, sys

def check(msg, ok):
    icon = "OK" if ok else "FAIL"
    print(f"  [{icon}] {msg}")

# 1. Backend
try:
    d = json.loads(urllib.request.urlopen("http://127.0.0.1:8000/api/info", timeout=5).read())
    check("Backend API", True)
    check("Agent reachable", d["data"]["agent"]["reachable"])
except Exception as e:
    check(f"Backend: {e}", False)
    sys.exit(1)

# 2. Homepage HTML
try:
    html = urllib.request.urlopen("http://127.0.0.1:8000/", timeout=5).read().decode("utf-8")
    m = re.search(r'src="(assets/index-.+?\.js)"', html)
    main_js_name = m.group(1) if m else None
    check(f"Main JS: {main_js_name}", bool(main_js_name))
except Exception as e:
    check(f"HTML: {e}", False)
    main_js_name = None

# 3. Main JS
if main_js_name:
    main_js = urllib.request.urlopen(f"http://127.0.0.1:8000/{main_js_name}", timeout=5).read().decode("utf-8")
    check(f"Main JS size: {len(main_js)} bytes", True)
    
    hm = re.search(r"Home-([A-Za-z0-9_-]+)\.js", main_js)
    home_name = f"Home-{hm.group(1)}.js" if hm else None
    check(f"Home chunk: {home_name}", bool(home_name))
else:
    home_name = None

# 4. Home chunk
if home_name:
    home_js = urllib.request.urlopen(f"http://127.0.0.1:8000/assets/{home_name}", timeout=5).read().decode("utf-8")
    check(f"Home chunk size: {len(home_js)} bytes", True)
    check("Has SVG encodeURIComponent", "encodeURIComponent" in home_js)
    check("Has SVG linearGradient", "linearGradient" in home_js)
    check("Has SVG xmlns", 'svg xmlns="http://www.w3.org/2000/svg"' in home_js)
    check("Has charCodeAt (hash function)", "charCodeAt" in home_js)
    check("Has palette colors", "#667eea" in home_js)

# 5. Weather API
try:
    w = json.loads(urllib.request.urlopen("http://127.0.0.1:8000/api/weather/%E5%8C%97%E4%BA%AC", timeout=10).read())
    check(f"Weather: Beijing {w['data']['temp']}C {w['data']['weather']}", w['code'] == 0)
except Exception as e:
    check(f"Weather: {e}", False)

print("\n=== ALL CHECKS COMPLETE ===")
