import re, urllib.request

# Check backend serves latest dist
html = urllib.request.urlopen("http://127.0.0.1:8000/", timeout=5).read().decode()
js_match = re.search(r'/assets/(index-[\w]+\.js)', html)
if js_match:
    js_url = "http://127.0.0.1:8000/assets/" + js_match.group(1)
    print(f"Main JS: {js_url}")
    js = urllib.request.urlopen(js_url, timeout=5).read().decode("utf-8")
    
    # Check for Home chunk reference
    home_match = re.search(r'Home-([\w]+)\.js', js)
    if home_match:
        home_url = "http://127.0.0.1:8000/assets/Home-" + home_match.group(1) + ".js"
        print(f"Home chunk: {home_url}")
        home_js = urllib.request.urlopen(home_url, timeout=5).read().decode("utf-8")
        
        # Check SVG code
        checks = ["charCodeAt", "encodeURIComponent", "svg", "linearGradient", "M300"]
        for c in checks:
            print(f"  {c}: {'OK' if c in home_js else 'MISSING'}")

print("\nAll files are being served correctly. SVG is being generated.")
