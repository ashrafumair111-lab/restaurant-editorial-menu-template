# restaurant-editorial-menu-template

Public, sanitized template for restaurant websites: a lightweight,
editorial-style static site built from a JSON-driven menu compiler.

## Architecture

- `menu.json` — single source of truth. Holds restaurant metadata (name,
  tagline, motto, hours, delivery), the category list with the editable
  menu (subtitles, descriptions, sizes, prices, options) and the brand
  story paragraphs.
- `_work/template.html` — the full HTML/CSS/JS: editorial typography,
  category sections with subheads, marketing content, guest-reviews
  marquee, story and visit sections.
- `_work/build_index.py` — the compiler. Renders every category section,
  renders the menu item list, and fills the featured "House Favourites"
  section with three selected dishes.
- `_work/check_index.py` — the validator. Verifies `index.html` matches
  `menu.json` (categories, items, prices, options), that every local file
  reference exists, that the generic brand strings are present and that no
  leftover placeholders appear.

## Key behaviours

- **Single-source menu.** Add a category/item to `menu.json` and re-run the
  build to update the site.
- **Tab-style category pills.** The `Eat well.` filter bar starts with
  `All` and lists every category. Clicking a pill filters the menu to just
  that category; clicking `All` shows the whole menu again.
- **Editable prices.** Single-price dishes show a `REGULAR` size row
  (dotted leader + `Rs ...`) below the description; multi-size items
  (Pide, Burgers, Halal Snack Pack, ...) render one row per size.
- **Mobile category scroll.** On small screens the pills bar wraps back
  into the single-row `overflow-x: auto` scroll.
- **Zero-dependency.** Vanilla JS, no frameworks, static output — deploy
  anywhere, including cPanel.

## Demo data

Dishes, sizes, prices, tagline, address, hours, phone, Google Maps links
and artwork placeholders are all generic demo content ("Saffron & Hearth —
Artisanal Dining"). Artwork is a tiny placeholder SVG
(`images/placeholder.svg` / `images/og-cover.svg`).

## Build & check

```
python _work\build_index.py   # menu.json + _work/template.html -> index.html
python _work\check_index.py   # validates index.html against menu.json
```
