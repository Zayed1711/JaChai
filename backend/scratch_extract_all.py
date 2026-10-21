import sys
import re
import json

sys.stdout.reconfigure(encoding='utf-8')

raw = open('e:/JaChai/Resources/list_extracted.txt', encoding='utf-8').read()
clean = ' '.join(raw.split())

# Cut sections
sec_starts = [
    (1, clean.find('1. Snacks, Dry Foods & Grocery Marketplaces')),
    (2, clean.find('2. Mobile Phones & Consumer Gadgets')),
    (3, clean.find('3. Laptops, Desktops & Computer Components')),
    (4, clean.find('4. Mainstream Fashion & Apparel Brands')),
    (5, clean.find('5. Fine Jewelry & Premium Fashion Jewelry Stores')),
    (6, clean.find('6. Sneakers & Footwear Stores')),
    (7, clean.find('7. Watches & Horology Retailers')),
    (8, clean.find('8. Multi-Category Marketplaces & Platform Aggregators')),
    (9, clean.find('9. Extended Supplementary Local Storefront Seeds')),
    (10, clean.find('Part 1: Budget, Casual & Imitation Jewelry Targets (50 Nodes)')),
    (11, clean.find('Part 2: Small & Medium Saree & Boutique Pages (50 Nodes)')),
    (12, len(clean))
]

def clean_item(text):
    text = re.sub(r'--- PAGE \d+ ---', '', text).strip()
    return text

print("Sections indices:", [(s[0], s[1]) for s in sec_starts])

# Parse bullets for sections 1 to 9
raw_sections = {}
for i in range(len(sec_starts) - 3):
    s_id, start = sec_starts[i]
    _, end = sec_starts[i+1]
    chunk = clean[start:end]
    # Remove header
    header_end = chunk.find('●')
    items_raw = chunk[header_end:].split('●')
    items = [clean_item(it) for it in items_raw if clean_item(it)]
    raw_sections[s_id] = items
    print(f"Section {s_id}: {len(items)} items")

# Parse 50 Jewelry F-Commerce
p1_chunk = clean[sec_starts[9][1]:sec_starts[10][1]]
# Split by number. Name ( @handle ) - description
p1_nodes = re.findall(r'(\d+)\.\s+([^–—\-]+)[–—\-]\s*([^0-9]+(?:\d+(?!\.)[^0-9]*)*)', p1_chunk)
print(f"Part 1 Jewelry nodes: {len(p1_nodes)}")

# Parse 50 Saree F-Commerce
p2_chunk = clean[sec_starts[10][1]:]
p2_nodes = re.findall(r'(\d+)\.\s+([^–—\-]+)[–—\-]\s*([^0-9]+(?:\d+(?!\.)[^0-9]*)*)', p2_chunk)
print(f"Part 2 Saree nodes: {len(p2_nodes)}")

output_data = {
    "sections": raw_sections,
    "jewelry_nodes": [(n[0].strip(), n[1].strip(), n[2].strip()[:60]) for n in p1_nodes],
    "saree_nodes": [(n[0].strip(), n[1].strip(), n[2].strip()[:60]) for n in p2_nodes]
}

with open('e:/JaChai/Resources/structured_stores_parsed.json', 'w', encoding='utf-8') as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False)

print("Parsed successfully to structured_stores_parsed.json")

