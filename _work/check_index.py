import json, re, html, os, sys

menu = json.load(open("menu.json", encoding="utf-8"))
doc = open("index.html", encoding="utf-8").read()
errors, notes = [], []

def err(m):
    errors.append(m)

# 1. every local file reference exists
for m in re.finditer(r'(?:src|href)="([^"#][^"]*)"', doc):
    ref = m.group(1)
    if ref.startswith(("http://", "https://", "mailto:", "tel:", "data:")):
        continue
    if not os.path.isfile(ref):
        err(f"missing local file: {ref}")

# 2. no client branding / no client data remains
for s in ("IKKA", "Turkish Pide", "House of Turkish Pide",
          "+92516126013", "+92 330 666 6449", "051 612 6013", "33.6292697", "Raheman"):
    if s in doc:
        err(f"client data/branding still present: {s!r}")

# 3. generic brand present
for s in ("Saffron & Hearth",):
    if s not in doc:
        err(f"brand missing: {s!r}")

# 4. placeholders exist
for img in ("images/placeholder.svg", "images/og-cover.svg"):
    if not os.path.isfile(img):
        err(f"placeholder missing: {img}")
    elif not re.search(r'<svg\b[^>]*xmlns="http://www.w3.org/2000/svg"', open(img, encoding="utf-8").read()):
        err(f"placeholder is not a lightweight SVG: {img}")

# 5. categories rendered in order with ids
ids = re.findall(r'<section class="menu-cat" id="cat-([a-z0-9-]+)"', doc)
expect_ids = [c["id"] for c in menu["categories"]]
if ids != expect_ids:
    err(f"category order/ids: {ids} != {expect_ids}")
for c in menu["categories"]:
    if c["name"] not in doc:
        err(f"category name missing: {c['name']}")

# 6. rendered rows must match menu.json exactly
rows = re.findall(r'<article class="menu-item".*?</article>', doc, re.S)
print(f"rendered menu rows: {len(rows)}")

def attr(block, name):
    m = re.search(r'data-%s="([^"]*)"' % name, block)
    return html.unescape(m.group(1)) if m else None

by_id = {(cat["name"], it["name"]): (cat, it) for cat in menu["categories"] for it in cat["items"]}
seen = set()
for block in rows:
    name = attr(block, "name"); catname = attr(block, "cat")
    if (catname, name) not in by_id:
        err(f"rendered item not in menu.json: {catname} / {name}"); continue
    cat, it = by_id[(catname, name)]
    seen.add((catname, name))
    if attr(block, "cat") != cat["name"]: err(f"{name}: category mismatch")
    if attr(block, "image") != it["image"]: err(f"{name}: image mismatch")
    if attr(block, "desc") != it["description"]: err(f"{name}: description mismatch")
    if attr(block, "prices") != json.dumps(it.get("sizes") or [{"label": "", "price": it["price"]}], separators=(",", ":")):
        err(f"{name}: prices mismatch")
    if attr(block, "options") != json.dumps(it.get("options") or [], separators=(",", ":")):
        err(f"{name}: options mismatch")

missing = set(by_id) - seen
if missing:
    err(f"items in menu.json not rendered: {sorted(missing)}")

# 7. every price in html exists in menu.json (same rule as original checker)
allowed = set()
for cat in menu["categories"]:
    for it in cat["items"]:
        if "sizes" in it:
            allowed |= {s["price"] for s in it["sizes"]}
        else:
            allowed.add(it["price"])
for n in sorted(allowed):
    if f"Rs {n:,}" not in doc:
        err(f"price not rendered: Rs {n:,}")
html_prices = set(int(n.replace(",", "")) for n in re.findall(r"Rs ([\d,]+)", doc))
if extra := html_prices - allowed:
    err(f"prices in html that are not in menu.json: {sorted(extra)}")

# 8. featured cards render the generic demo dishes
fav_names = re.findall(r'class="fav-name"><h3>([^<]+)</h3>', doc)
if fav_names != ["Prosciutto Pide", "Vegetable Pide", "Chicken Kebab"]:
    err(f"featured cards wrong: {fav_names}")

print(f"categories: {len(ids)}  items: {len(rows)}  prices in html: {sorted(html_prices)}")
print("RESULT:", "FAIL" if errors else "OK — menu.json and index.html agree")
for n in notes:
    print("  NOTE:", n)
for e in errors:
    print("  ERROR:", e)
sys.exit(1 if errors else 0)
