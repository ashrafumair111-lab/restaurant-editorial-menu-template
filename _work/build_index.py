import json, html, re

menu = json.load(open("menu.json", encoding="utf-8"))
tpl = open("_work/template.html", encoding="utf-8").read()

def esc(s):
    return html.escape(s or "", quote=True)

def money(n):
    return f"Rs {n:,}"

def pills(item):
    out = []
    for i, o in enumerate(item.get("options") or []):
        if i:
            out.append('<span class="pill-or">or</span>')
        out.append(f'<span class="pill">{esc(o)}</span>')
    note = item.get("note") or ""
    if note == "8oz":
        out.append('<span class="pill">8oz</span>')
    return "".join(out)

def price_rows(item):
    sizes = item.get("sizes") or [{"label": "Regular", "price": item["price"]}]
    return "".join(
        f'<div class="price-row"><span class="price-label">{esc(s["label"])}</span>'
        f'<span class="dots" aria-hidden="true"></span>'
        f'<span class="price-value">{money(s["price"])}</span></div>'
        for s in sizes
    )

def item_row(cat, item):
    img = item["image"]
    prices = item.get("sizes") or [{"label": "", "price": item["price"]}]
    data_prices = json.dumps(prices, separators=(",", ":"))
    data_options = json.dumps(item.get("options") or [], separators=(",", ":"))
    note = item.get("note") or ""
    data_note = "8oz" if note == "8oz" else ""

    p = pills(item)
    p = f'<span class="pills">{p}</span>' if p else ""
    desc = f'<p class="menu-desc">{esc(item["description"])}</p>' if item["description"] else ""

    return f'''<article class="menu-item" tabindex="0" role="button" aria-label="View {esc(item['name'])} details"
   data-cat="{esc(cat['name'])}" data-name="{esc(item['name'])}" data-image="{esc(img)}"
   data-desc="{esc(item['description'])}" data-prices="{esc(data_prices)}"
   data-options="{esc(data_options)}" data-note="{esc(data_note)}">
   <div class="menu-thumb"><img src="{esc(img)}" alt="{esc(item['name'])}" width="72" height="72" loading="lazy" decoding="async"></div>
   <div class="menu-body">
    <div class="menu-title"><h4>{esc(item['name'])}</h4>{p}</div>
    {desc}
    {price_rows(item)}
   </div>
  </article>'''

categories = []
for cat in menu["categories"]:
    base = f'<p class="base-note">{esc(cat["chooseBase"])}</p>\n   ' if cat.get("chooseBase") else ""
    rows = "\n   ".join(item_row(cat, it) for it in cat["items"])
    categories.append(f'''<section class="menu-cat" id="cat-{cat['id']}" aria-labelledby="cat-{cat['id']}-title">
  <div class="cat-head">
   <h3 id="cat-{cat['id']}-title">{esc(cat['name'])}</h3>
   <p>{esc(cat['description'])}</p>
  </div>
  {base}<div class="cat-items">
  {rows}
  </div>
 </section>''')

by_id = {it["id"]: (cat, it) for cat in menu["categories"] for it in cat["items"]}
fav_order = ["prosciutto-pide", "vegetable-pide", "chicken-kebab"]
favs = []
for fid in fav_order:
    cat, it = by_id[fid]
    img = it["image"]
    if it.get("sizes"):
        low = min(s["price"] for s in it["sizes"])
        price = f"From {money(low)}"
    else:
        price = money(it["price"])
    favs.append(f'''<article class="fav-card">
    <div class="fav-thumb"><img src="{esc(img)}" alt="{esc(it['name'])}" width="92" height="92" loading="lazy" decoding="async"></div>
    <div class="fav-body">
     <div class="fav-name"><h3>{esc(it['name'])}</h3><span class="fav-price">{price}</span></div>
     <p class="fav-desc">{esc(it['description'])}</p>
    </div>
   </article>''')

paras = []
for i, para in enumerate(menu["story"]["paragraphs"]):
    cls = ' class="story-lead"' if i == 0 else ""
    paras.append(f'<p{cls}>{esc(para)}</p>')

out = (tpl
       .replace("%%MENU%%", "\n  ".join(categories))
       .replace("%%FAVOURITES%%", "\n   ".join(favs))
       .replace("%%STORY%%", "\n  ".join(paras))
       .replace("%%SIGNATURE%%", esc(menu["story"]["signature"])))

assert "%%" not in out, "unreplaced placeholder"
open("index.html", "w", encoding="utf-8", newline="\n").write(out)
print("wrote index.html", len(out), "bytes")
print("categories:", len(categories), "| menu items:", sum(len(c["items"]) for c in menu["categories"]))
