from flask import Flask, render_template, request
import requests
import re
import json

app = Flask(__name__)

def extract_box_nos_from_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15A372 Safari/604.1"
    }
    response = requests.get(url, headers=headers)
    html = response.text
    match = re.search(r'"setSkuList":(\[.*?\])', html)
    if not match:
        return []
    set_sku_list = json.loads(match.group(1))
    box_nos = [item["boxNo"] for item in set_sku_list]
    return box_nos

def fetch_sku_list_by_box_no(box_no):
    url = "https://m.popmart.com/sg/api/pop/boxProductDetail"
    params = {"boxNo": box_no}
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15A372 Safari/604.1"
    }
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    set_sku_list = data.get("data", {}).get("setSkuList", [])
    return set_sku_list

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    if request.method == "POST":
        activity_url = request.form["activity_url"]
        target_character = request.form["target_character"].strip().upper()

        box_nos = extract_box_nos_from_page(activity_url)

        if not box_nos:
            results.append("未能取得 boxNo 列表，請檢查網址是否正確。")
        else:
            for idx, box_no in enumerate(box_nos, start=1):
                sku_list = fetch_sku_list_by_box_no(box_no)
                characters = [sku.get("characterName").upper() for sku in sku_list]
                if target_character in characters:
                    results.append(f"盒號 {idx}：包含角色 {target_character}！")
                else:
                    results.append(f"盒號 {idx}：不含 {target_character}")

            results.append("查詢完成，祝您開箱愉快！")

    return render_template("index.html", results=results)

if __name__ == "__main__":
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
