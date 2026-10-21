# JaChai Curated Store Registries (Category-Separated)

This directory contains the master store registries for JaChai, separated by retail categories.

## Included Category Registries:
1. `mobile_phones_and_gadgets.csv` — Mobile Phones & Consumer Gadgets (30 stores)
2. `laptops_and_computers.csv` — Laptops, Desktops & Computer Components (27 stores)
3. `fashion_and_apparel.csv` — Mainstream Fashion & Apparel Brands (37 stores)
4. `grocery_and_snacks.csv` — Snacks, Dry Foods & Grocery Marketplaces (28 stores)
5. `fine_jewelry_and_gold.csv` — Fine Jewelry & Premium Fashion Jewelry Stores (15 stores)
6. `budget_jewelry_fcommerce.csv` — Budget, Casual & Imitation Jewelry Targets (52 stores)
7. `saree_boutiques_fcommerce.csv` — Small & Medium Saree & Boutique Pages (52 stores)
8. `sneakers_and_footwear.csv` — Sneakers & Footwear Stores (26 stores)
9. `watches_and_horology.csv` — Watches & Horology Retailers (24 stores)
10. `appliances_and_electronics.csv` — Home Appliances & White Goods (8 stores)
11. `beauty_and_skincare.csv` — Beauty, Skincare & Lifestyle Stores (12 stores)
12. `cycles_and_evs.csv` — Cycles & Electric Vehicles (EVs) (8 stores)
13. `sportswear_and_gym.csv` — Sportswear, Activewear & Gym Gear (7 stores)

Total: 326 Curated Bangladeshi Stores

---

## Dynamic Column & Row Auto-Update Feature

The JaChai backend automatically monitors this folder for changes.

### 1. Adding New Columns:
You can open any CSV and add any new column header (e.g., `Rating`, `Phone`, `Location`, `Notes`, `Delivery_BDT`).
The backend automatically parses and attaches all extra columns to the store dictionary without crashing or losing data.

### 2. Editing Stores or Adding Rows:
You can add new store rows or modify existing domains, websites, Facebook URLs, or architecture modes (`Engine A (Direct SKU Match)` vs `Engine B (Starts From Benchmark)`).

### 3. Adding New Categories:
You can drop any new `.csv` file into this directory (e.g. `books_and_stationery.csv`). It will automatically be loaded and indexed into the active registry.

### 4. Zero Restart Required:
Whenever a CSV file is saved, JaChai automatically detects the file's modification timestamp (`mtime`) and reloads the registry in-memory (~10ms). You can also manually trigger a reload via `POST /api/v1/admin/registry/reload` or the Admin Command Center UI.

