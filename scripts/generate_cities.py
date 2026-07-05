"""
Generate all Chinese prefecture-level cities via Amap API.
Usage: python scripts/generate_cities.py
"""
import json, urllib.request, time, ssl, os
from pathlib import Path

os.environ["NO_PROXY"] = "restapi.amap.com,127.0.0.1,localhost"

AMAP_KEY = "ed8d2854cd16f5cbdc7bc30a61095780"
DATA_DIR = Path(__file__).resolve().parent.parent / "travel-app" / "backend" / "data"
HEADERS = {"User-Agent": "Mozilla/5.0"}
SSL_CTX = ssl.create_default_context()

# Province adcodes (pre-cached to avoid the initial API call)
PROVINCES = [
    ("110000", "北京"), ("120000", "天津"), ("130000", "河北"), ("140000", "山西"),
    ("150000", "内蒙古"), ("210000", "辽宁"), ("220000", "吉林"), ("230000", "黑龙江"),
    ("310000", "上海"), ("320000", "江苏"), ("330000", "浙江"), ("340000", "安徽"),
    ("350000", "福建"), ("360000", "江西"), ("370000", "山东"), ("410000", "河南"),
    ("420000", "湖北"), ("430000", "湖南"), ("440000", "广东"), ("450000", "广西"),
    ("460000", "海南"), ("500000", "重庆"), ("510000", "四川"), ("520000", "贵州"),
    ("530000", "云南"), ("540000", "西藏"), ("610000", "陕西"), ("620000", "甘肃"),
    ("630000", "青海"), ("640000", "宁夏"), ("650000", "新疆"),
]

TAG_MAP = {
    "北京": ["文化","美食","亲子","自驾"], "上海": ["文化","美食","亲子"],
    "天津": ["文化","美食"], "重庆": ["美食","自驾"],
    "广州": ["美食","文化"], "深圳": ["亲子","自驾"], "成都": ["美食","亲子","自驾"],
    "杭州": ["文化","自驾","亲子"], "南京": ["文化","美食"], "武汉": ["美食","文化"],
    "长沙": ["美食","文化"], "西安": ["文化","美食"], "昆明": ["自驾","自然"],
    "贵阳": ["自然","美食"], "郑州": ["文化"], "济南": ["文化","美食"],
    "石家庄": ["文化"], "沈阳": ["文化","美食"], "哈尔滨": ["亲子","美食"],
    "长春": ["自然"], "合肥": ["文化"], "南昌": ["文化","美食"],
    "福州": ["美食","文化"], "海口": ["亲子","自然"], "南宁": ["美食","自然"],
    "拉萨": ["自驾","自然"], "乌鲁木齐": ["美食","自驾"],
    "西宁": ["自驾","自然"], "兰州": ["美食","自驾"],
    "银川": ["文化","自驾"], "太原": ["文化","美食"], "呼和浩特": ["美食","自驾"],
    "苏州": ["文化","美食"], "厦门": ["亲子","自然"], "青岛": ["美食","亲子"],
    "大连": ["亲子","美食"], "三亚": ["亲子","自驾"], "桂林": ["自驾","自然"],
    "丽江": ["自驾","自然"], "大理": ["自驾","自然"], "洛阳": ["文化"],
    "张家界": ["自然","自驾"], "黄山": ["自然","自驾"], "威海": ["亲子","自然"],
    "珠海": ["亲子","自然"], "烟台": ["美食","亲子"], "泉州": ["文化","美食"],
    "扬州": ["文化","美食"], "绍兴": ["文化","美食"], "嘉兴": ["文化","亲子"],
    "宁波": ["美食","文化"], "无锡": ["文化","亲子"], "常州": ["亲子"],
    "徐州": ["文化","美食"], "镇江": ["文化"], "南通": ["美食"],
    "温州": ["美食"], "金华": ["文化"], "中山": ["美食"],
    "佛山": ["美食","文化"], "东莞": ["美食"], "惠州": ["亲子","自然"],
    "汕头": ["美食"], "北海": ["亲子","自然"],
    "秦皇岛": ["亲子","自驾"], "承德": ["文化","自驾"], "开封": ["文化"],
    "宜昌": ["自然","自驾"], "襄阳": ["文化"],
    "九江": ["自然"], "景德镇": ["文化"], "遵义": ["文化","自然"],
    "乐山": ["文化","美食"], "九寨沟": ["自然","自驾"],
    "敦煌": ["文化","自驾"], "西双版纳": ["自然","亲子"],
}

DAY_MAP = {
    "北京":3,"上海":3,"广州":3,"深圳":2,"成都":3,"杭州":2,"南京":2,"武汉":2,
    "长沙":2,"西安":3,"重庆":3,"昆明":3,"贵阳":2,"郑州":2,"济南":2,"沈阳":2,
    "哈尔滨":3,"长春":2,"合肥":1,"南昌":2,"福州":2,"海口":3,"南宁":2,"拉萨":4,
    "乌鲁木齐":3,"西宁":2,"兰州":2,"银川":2,"太原":2,"呼和浩特":2,"天津":2,
    "石家庄":1,"苏州":2,"厦门":3,"青岛":3,"大连":3,"三亚":4,"桂林":3,
    "丽江":3,"大理":3,"洛阳":2,"张家界":3,"黄山":3,"威海":2,"珠海":2,"烟台":2,
    "扬州":2,"绍兴":2,"无锡":2,"宁波":2,"北海":3,"秦皇岛":2,"承德":2,"开封":2,
    "九江":2,"景德镇":2,"乐山":2,"九寨沟":3,"敦煌":2,"西双版纳":3,
}


def api(url, retries=2):
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=15, context=SSL_CTX) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            if attempt < retries:
                time.sleep(2)
                continue
            raise


def main():
    cities = []
    idx = 0
    for adcode, prov_name in PROVINCES:
        print(f"  {prov_name}...", end=" ", flush=True)
        try:
            url = f"https://restapi.amap.com/v3/config/district?keywords={adcode}&subdistrict=1&key={AMAP_KEY}"
            data = api(url)
            dists = data.get("districts", [{}])[0].get("districts", [])
            count = 0
            for d in dists:
                if d.get("level") != "city":
                    continue
                name = d["name"].rstrip("市地区自治州").rstrip("盟")
                idx += 1
                tags = TAG_MAP.get(name, [])
                days = DAY_MAP.get(name, 2)
                city = {
                    "id": f"city-{name.lower()}",
                    "name": name,
                    "pinyin": name.lower(),
                    "cover_img": "",
                    "tags": tags,
                    "sort_weight": 100 - idx + 50 if tags else 50,
                    "plan_days": days,
                    "center": d.get("center", ""),
                }
                cities.append(city)
                count += 1
            print(f"{count} cities")
        except Exception as e:
            print(f"FAILED: {e}")
        time.sleep(0.3)

    cities.sort(key=lambda c: c["sort_weight"], reverse=True)
    output = {"cities": cities}
    path = DATA_DIR / "cities_backup.json"
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nDone! {len(cities)} cities saved")


if __name__ == "__main__":
    main()
