"""Set curated real images for top cities, picsum for the rest."""
import json, urllib.parse

path = "travel-app/backend/data/cities_backup.json"
d = json.load(open(path, "r", encoding="utf-8"))

IMAGES = {
    "北京": "https://upload.wikimedia.org/wikipedia/commons/2/2d/Skyline_of_Beijing_CBD_with_B-5906_approaching_%2820211016171955%29_%281%29.jpg",
    "上海": "https://upload.wikimedia.org/wikipedia/commons/d/df/Pudong_Shanghai_November_2017_panorama.jpg",
    "广州": "https://upload.wikimedia.org/wikipedia/commons/4/4d/Guangzhou_Twincities_skyline.jpg",
    "深圳": "https://upload.wikimedia.org/wikipedia/commons/e/e9/Shenzhen_skyline_from_Hong_Kong_%28cropped%29.jpg",
    "成都": "https://upload.wikimedia.org/wikipedia/commons/7/74/%E9%9B%AA%E5%B1%B1%E4%B8%8B%E7%9A%84%E6%88%90%E9%83%BD%E5%B8%82%E5%A4%A9%E9%99%85%E7%BA%BF_Chengdu_skyline_with_snow_capped_mountains.jpg",
    "杭州": "https://upload.wikimedia.org/wikipedia/commons/5/56/Westlake_2023.jpg",
    "西安": "https://upload.wikimedia.org/wikipedia/commons/4/44/%E8%A5%BF%E5%AE%89%E9%92%9F%E6%A5%BC2020_%281%29.jpg",
    "重庆": "https://upload.wikimedia.org/wikipedia/commons/4/4e/Chongqing_Skyline_at_night.jpg",
    "南京": "https://upload.wikimedia.org/wikipedia/commons/e/e8/Nanjing_skyline_from_Xuanwu_Lake.jpg",
    "武汉": "https://upload.wikimedia.org/wikipedia/commons/f/f0/Wuhan_Yangtze_River_Night_Panorama.jpg",
    "长沙": "https://upload.wikimedia.org/wikipedia/commons/c/cb/Changsha_Skyline.jpg",
    "昆明": "https://upload.wikimedia.org/wikipedia/commons/8/85/Kunming_Montage.png",
    "厦门": "https://upload.wikimedia.org/wikipedia/commons/c/c4/Xiamen_University_and_beach.jpg",
    "青岛": "https://upload.wikimedia.org/wikipedia/commons/d/de/Qingdao_Zhanqiao_Pier.jpg",
    "三亚": "https://upload.wikimedia.org/wikipedia/commons/6/6b/Sanya_Bay_2016.jpg",
    "哈尔滨": "https://upload.wikimedia.org/wikipedia/commons/0/0e/Harbin_skyline_from_river.jpg",
    "天津": "https://upload.wikimedia.org/wikipedia/commons/9/9a/Tianjin_skyline_at_night.jpg",
    "拉萨": "https://upload.wikimedia.org/wikipedia/commons/9/9a/Potala_Palace_2022.jpg",
    "苏州": "https://upload.wikimedia.org/wikipedia/commons/3/3a/Suzhou_water_town_%28Tongli%29.jpg",
    "大连": "https://upload.wikimedia.org/wikipedia/commons/0/0b/Dalian_skyline_2021.jpg",
    "桂林": "https://upload.wikimedia.org/wikipedia/commons/1/15/Guilin_Li_River_mountain_scenery.jpg",
    "丽江": "https://upload.wikimedia.org/wikipedia/commons/6/6a/Lijiang_Ancient_Town_%282018%29.jpg",
    "大理": "https://upload.wikimedia.org/wikipedia/commons/9/9e/Dali_Old_Town.jpg",
    "洛阳": "https://upload.wikimedia.org/wikipedia/commons/8/8c/Longmen_Grottoes_Luoyang.jpg",
}

count = 0
for c in d["cities"]:
    name = c["name"]
    if name in IMAGES:
        c["cover_img"] = IMAGES[name]
        count += 1
    else:
        c["cover_img"] = "https://picsum.photos/seed/" + urllib.parse.quote(name) + "/600/400"

json.dump(d, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"Done! {count} real images, {len(d['cities'])-count} picsum")
