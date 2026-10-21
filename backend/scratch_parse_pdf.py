import sys
import re
import json

sys.stdout.reconfigure(encoding='utf-8')

raw = open('e:/JaChai/Resources/list_extracted.txt', encoding='utf-8').read()
clean = ' '.join(raw.split())

# Locate where 100 F-Commerce starts
f_comm_idx = clean.find('1. FANTORA')
main_text = clean[:f_comm_idx]
f_comm_text = clean[f_comm_idx:]

print(f"Main text: {len(main_text)} chars, F-Commerce: {len(f_comm_text)} chars")

# Split sections 1 to 9
sec_titles = [
    (1, "Snacks, Dry Foods & Grocery Marketplaces"),
    (2, "Mobile Phones & Consumer Gadgets"),
    (3, "Laptops, Desktops & Computer Components"),
    (4, "Mainstream Fashion & Apparel Brands"),
    (5, "Fine Jewelry & Premium Fashion Jewelry Stores"),
    (6, "Sneakers & Footwear Stores"),
    (7, "Watches & Horology Retailers"),
    (8, "Multi-Category Marketplaces & Platform Aggregators"),
    (9, "Extended Supplementary Local Storefront Seeds"),
]

section_data = {}

for idx, (num, title) in enumerate(sec_titles):
    start_str = f"{num}. {title.split('&')[0].strip()}"
    start_pos = main_text.find(str(num) + ".")
    if idx < len(sec_titles) - 1:
        next_num = sec_titles[idx + 1][0]
        end_pos = main_text.find(str(next_num) + ".")
        chunk = main_text[start_pos:end_pos]
    else:
        chunk = main_text[start_pos:]
    
    bullets = [b.strip() for b in chunk.split('●') if b.strip()]
    header = bullets[0] if bullets else ""
    items = bullets[1:] if len(bullets) > 1 else []
    section_data[num] = {
        "title": title,
        "items": items
    }
    print(f"Section {num}: {title} -> {len(items)} items")
    for item in items[:5]:
        print(f"   - {item[:60]}")

# Parse the 100 F-Commerce items
f_comm_items = []
# Items are numbered 1. FANTORA ... 100. Boutique Purnima
pattern = r'(\d+)\.\s+([^–—\-]+)[–—\-]\s*([^0-9]+(?:\d+(?!\.)[^0-9]*)*)'
f_items_raw = re.split(r'(?=\b\d+\.\s+[A-Za-z])', f_comm_text)
print(f"F-Commerce raw split: {len(f_items_raw)} items")
for item in f_items_raw[:10]:
    if item.strip():
        print(f"   [F] {item.strip()[:70]}")

# Dump to json for inspection
with open('e:/JaChai/Resources/parsed_sections.json', 'w', encoding='utf-8') as f:
    json.dump({
        "sections": section_data,
        "f_commerce_count": len(f_items_raw)
    }, f, indent=2, ensure_ascii=False)

