"""Build shops.json: NPC shop listings (coins only) from the OSRS Wiki storeline bucket.

Usage: python3 tools/build_shops.py shops.json
"""
import json, sys, time, urllib.parse, urllib.request

API = "https://oldschool.runescape.wiki/api.php"
UA = {"User-Agent": "osrs-hc-flip-planner/1.0 (github.com/sjoyner945/osrs-hc-flipper)"}
FIELDS = ["sold_by", "sold_item", "store_sell_price", "store_currency", "store_delta",
          "store_stock", "store_sell_multiplier", "restock_time", "sold_item_json"]


def query(offset, limit=500):
    q = "bucket('storeline').select(%s).limit(%d).offset(%d).run()" % (
        ",".join("'%s'" % f for f in FIELDS), limit, offset)
    url = API + "?" + urllib.parse.urlencode({"action": "bucket", "format": "json", "query": q})
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        body = json.load(r)
    if "error" in body:
        raise RuntimeError(body["error"])
    return body["bucket"]


def num(v):
    try:
        return int(float(str(v).replace(",", "")))
    except (TypeError, ValueError):
        return None


def main(out):
    rows, offset = [], 0
    while True:
        page = query(offset)
        rows.extend(page)
        if len(page) < 500:
            break
        offset += 500
        time.sleep(0.5)
    shops = []
    for r in rows:
        if (r.get("store_currency") or "Coins") != "Coins":
            continue
        price = num(r.get("store_sell_price"))
        stock = num(r.get("store_stock"))
        if not price or price <= 0:
            continue
        try:
            extra = json.loads(r.get("sold_item_json") or "{}")
        except ValueError:
            extra = {}
        loc = extra.get("Location") or ""
        if isinstance(loc, list):
            loc = ", ".join(str(x) for x in loc)
        loc = str(loc)
        while "[[" in loc:
            a = loc.index("[["); b = loc.find("]]", a)
            if b < 0:
                break
            inner = loc[a + 2:b].split("|")[-1]
            loc = loc[:a] + inner + loc[b + 2:]
        shops.append({
            "item": extra.get("Display name") or r["sold_item"],
            "shop": (r.get("sold_by") or "").rstrip("."),
            "loc": loc,
            "mem": 1 if extra.get("Members") == "Yes" else 0,
            "price": price,
            "stock": stock,          # None = unlimited / not listed
            "sellMult": num(r.get("store_sell_multiplier")),
            "delta": num(r.get("store_delta")),
        })
    shops.sort(key=lambda s: (s["item"], s["price"]))
    with open(out, "w") as f:
        json.dump({"builtAt": int(time.time()), "shops": shops}, f, separators=(",", ":"))
    print("wrote", out, len(shops), "coin shop listings from", len(rows), "rows")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "shops.json")
