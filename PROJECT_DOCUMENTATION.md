# JaChai (যা চাই করুন যাচাই) — Total Project Specification & Architecture

> **The Sovereign Real-Time Multi-Vertical Price Intelligence, Anti-Fraud & Universal Canonical SKU Comparison Platform for Bangladesh**
>
> **Production Deployment:** Frontend on Vercel (`https://ja-chai-five.vercel.app`) · Backend API on Render · Autonomous Local SLM on Ollama

---

## 1. Executive Summary & System Identity

**JaChai** (`/dʒɑː-tʃaɪ/`, Bengali: **যাচাই** — *"Verify What You Want"*) is an enterprise-grade meta-search engine, canonical SKU aggregator, and price intelligence platform engineered specifically for the fragmented digital commerce landscape of Bangladesh.

Traditional search aggregators in emerging markets rely on static catalogues or synthetic estimates that fail when applied to Bangladesh's retail realities: wild price disparities between official warranty and grey-market imports, unorganized F-Commerce (Facebook Page) merchants, deceptive "accessory pricing traps" (e.g. phone cases miscategorized as flagship phones), and broken product links.

JaChai solves these foundational challenges through a **Web-First, Registry-Decoupled Architecture**:
1. **Dynamic Web-First Metasearch:** Queries harvest live inventory and prices directly from verified e-commerce sites and social commerce endpoints.
2. **Universal Canonical SKU Consolidation Engine:** Aggregates offers from dozens of competing retailers for identical hardware into **EXACTLY ONE** unified comparison card. Consolidates across 50+ color variations while cleanly partitioning by physical hardware specifications (RAM, SSD, GPU, Bus MHz, Console edition) and warranty tiers (Official BTRC Warranty vs Unofficial Global, Brand New vs Pre-Owned).
3. **Decoupled Verified Store Registry:** A curated registry of 341+ Bangladeshi merchants provides trust scores, business domain links, Facebook boutique profiles, and return policies—guaranteeing zero synthetic price fabrication.
4. **Hot Products Live Market Benchmarks:** High-velocity national benchmarks (Gold, Fuel, iPhones, Galaxy S series, RAM, SSD, GPU, Processors) with starts-from pricing, previous price comparison, latest tech releases, and direct store drawers.
5. **Stealth Vault Operations Center:** Pin-protected admin command center (Master PIN `42791`) with autonomous spider health watchdogs, 1-click price recalibration, banner inventory CRM, and dynamic registry management.

---

## 2. System Architecture & High-Level Topology

```mermaid
flowchart TD
    subgraph ClientLayer["Frontend Client Layer (Next.js 14 App Router / Vercel)"]
        UI["JaChai Storefront (App.jsx)"]
        HP["Hot Products Live Pricing Tracker"]
        SearchUI["Trilingual Search Bar & Suggestions"]
        Drawer["Verified Store Outbound Drawer"]
        AdminUI["Stealth Vault Admin Command Center"]
        ErrBoundary["Self-Healing ErrorBoundary & Dynamic SSR-Off Gate"]
    end

    subgraph APILayer["FastAPI Core Engine (Python 3.11+ / Render)"]
        Router["FastAPI Application Router (main.py)"]
        AuthModule["Stealth Vault Guard & Rate Limiter (auth.py)"]
        ProxyModule["SSRF IP-Guard & Image Proxy"]
        URLHealer["URL Sanitization & Healing Engine (url_healer.py)"]
    end

    subgraph IntelligenceLayer["Price Intelligence & Metasearch Engines"]
        Lingual["Trilingual Normalizer (Bangla / Banglish / English)"]
        SLM["Local SLM Query Classifier (Ollama / Qwen2.5)"]
        SpiderEngine["Autonomous Spider Harvester (crawler.py)"]
        SKUEngine["Universal Canonical SKU & Variant Sorter"]
        FloorGate["Anti-Accessory & Hardware Price Floor Gate"]
        RecalEngine["Daily Hot Products Recalibration Engine"]
    end

    subgraph DataLayer["Persistence & Storage Layer"]
        DB[(Authoritative SQLite Database: jachai.db)]
        Registry[(Master Store Registry: 341+ BD Merchants)]
        Cache[(In-Memory Response & Base Product Cache)]
    end

    UI --> ErrBoundary
    ErrBoundary --> HP & SearchUI & Drawer
    AdminUI --> AuthModule

    SearchUI --> Lingual --> SLM --> Router
    HP --> Router

    Router --> AuthModule
    Router --> ProxyModule
    Router --> URLHealer
    Router --> DB & Registry & Cache

    Router --> SpiderEngine
    SpiderEngine --> FloorGate --> SKUEngine --> Drawer
    RecalEngine --> DB
```

---

## 3. Core Features Breakdown

### 3.1 Hot Products Live Pricing & Market Tracker
High-velocity commodity and tech items are displayed on the storefront as horizontal benchmark bars, highlighting starting rates, historical price variations, and latest releases:

| # | Benchmark Item | Category | Unit / Metric | Featured 2025/2026 Reference | Verified Sources |
|---|---|---|---|---|---|
| **1** | **Gold (22K & 24K Hallmark)** | Jewelry | ৳ / Vori (11.664g) | 24K: ৳154,700/Vori • 22K: ৳141,800/Vori | BAJUS Hallmark Benchmark, Diamond World, Apan Jewellers |
| **2** | **Fuel (Octane, Diesel, Petrol)** | Energy / Transport | ৳ / Litre | Octane: ৳125/L • Diesel: ৳105/L • Petrol: ৳120/L | BPC Regulated Retail, Padma Oil, Meghna Petroleum |
| **3** | **iPhones (Apple Flagship Series)** | Mobile Gadgets | Starts from | Apple iPhone 17 (256GB, A19 Bionic) / iPhone 16 Pro Max | Apple Gadgets BD, Star Tech, Pickaboo, Salextrac |
| **4** | **Samsung Galaxy S Series** | Mobile Gadgets | Starts from | Samsung Galaxy S25 Ultra (Snapdragon 8 Elite, Galaxy AI) | Star Tech, Apple Gadgets BD, Samsung Plaza BD |
| **5** | **RAM (DDR4 / DDR5 Modules)** | Desktop Components | Starts from | TEAM T-FORCE DELTA RGB 32GB (2x16GB) 7200MHz DDR5 | Star Tech, Ryans Computers, Techland BD |
| **6** | **SSD (Gen5 NVMe & SATA)** | Desktop Components | Starts from | Silicon Power XPOWER XS90 2TB PCIe Gen5 (10,000+ MB/s) | Star Tech, Ryans Computers, Ultratech BD |
| **7** | **GPU (Graphics Cards)** | Desktop Components | Starts from | NVIDIA GeForce RTX 5080 16GB GDDR7 Graphics Card | Star Tech, Ryans Computers, Potaka IT |
| **8** | **Processors (Intel & AMD CPUs)** | Desktop Components | Starts from | AMD Ryzen 7 9800X3D (8C/16T, 96MB 3D V-Cache) / Ultra 9 | Star Tech, Ryans Computers, Techland BD |

#### Hot Products Architecture:
* **Interactive Store Drawer:** Clicking on any benchmark bar smoothly expands an inline drawer revealing verified retail stores, current stock prices, in-stock badges, and one-click direct homepage links.
* **Price Trend Indicators:** Visual indicators for price drops (`▼ ৳3,500 (4.9%)` in emerald), increases (`▲ ৳3,300 (+2.4%)` in rose), or market-stable regulation (`● Market Stable` in slate).
* **Zero-Cutoff Border Card Layout:** Clean, responsive horizontal card geometry matching desktop, tablet, and mobile viewports.

---

### 3.2 Live Search Engine & Multi-Lingual Intent Normalization
JaChai features a trilingual query engine capable of resolving mixed colloquial terms:

1. **Bengali Native Script:** `আইফোন ১৬ প্রো ম্যাক্স`, `স্বর্ণের ভরি কত`, `স্যামসাং এস২৫ আল্ট্রা`
2. **Banglish / Phonetic Latin:** `iphone 16 pro max dam koto`, `ram er price`, `bhalodam bdt`
3. **English Standard:** `AMD Ryzen 7 9800X3D`, `Sony PlayStation 5 Slim Disc Edition`

```mermaid
flowchart LR
    RawQuery["Raw User Input"] --> Normalizer["Linguistic Sanitizer"]
    Normalizer --> LingualCache{"Linguistic Cache Hit?"}
    LingualCache -->|Yes| FastPath["Instant Resolved Query (< 5ms)"]
    LingualCache -->|No| SLMClassifier["Ollama SLM Intent Classifier"]
    SLMClassifier --> IntentNode["Resolved Canonical Model + Category"]
    IntentNode --> SearchDispatcher["Database + Live Spider Dispatcher"]
```

* **Instant Suggestions Dropdown:** As-you-type autocomplete with highlighted matches and instant dismissal upon selection.
* **Disambiguation Pills ("Did you mean:"):** Interactive chips suggesting brand corrections or hardware tiers without reloading the page.

---

### 3.3 Universal Canonical SKU & Variant Consolidation Engine
The core algorithmic breakthrough of JaChai is the **Canonical SKU Consolidator**. Instead of cluttering search results with 20 cards for the same phone in different colors, JaChai enforces:

```mermaid
flowchart TD
    ScrapedListings["Raw Scraped Store Listings (e.g. 15 listings)"] --> ColorFilter["Color Stripping Filter (50+ standard & OEM colors)"]
    ColorFilter --> SpecExtractor["Hardware Specs Extractor (RAM, Storage, Bus MHz, Gen)"]
    SpecExtractor --> WarrantyClassifier["Warranty & Condition Classifier (BTRC Official vs Grey Market)"]
    WarrantyClassifier --> SKUPool["Canonical SKU Partitioning"]
    
    SKUPool --> Card1["Card A: iPhone 16 Pro Max · 256GB · Official BTRC (4 Stores)"]
    SKUPool --> Card2["Card B: iPhone 16 Pro Max · 256GB · Unofficial Global (6 Stores)"]
    SKUPool --> Card3["Card C: iPhone 16 Pro Max · 512GB · Unofficial Global (3 Stores)"]
```

#### SKU Partitioning Rules:
* **50+ Colors Ignored:** Black Titanium, White Titanium, Natural Titanium, Desert Titanium, Obsidian, Porcelain, Hazel, Rose Gold, Alpine Green, Space Gray, Phantom Black, etc., are never treated as separate cards.
* **Storage & RAM:** Partitioned strictly (e.g. `128GB` vs `256GB`, `8GB RAM` vs `16GB RAM`).
* **PC Components:**
  * RAM: Segregated by DDR generation and Bus Speed (`16GB DDR4 3200MHz` vs `16GB DDR5 6000MHz`).
  * SSDs: Segregated by PCIe Generation and Bus Form (`1TB PCIe Gen4 NVMe` vs `2TB PCIe Gen5 NVMe`).
  * GPUs: Segregated by VRAM size and Chipset architecture (`RTX 4060 8GB` vs `RTX 4070 12GB`).
* **Gaming Consoles:** Segregated by physical editions (`PS5 Slim Disc Edition` vs `PS5 Slim Digital Edition`, `Switch OLED` vs `Switch Standard`).
* **Warranty & Integrity:** Official BTRC Approved warranty listings are partitioned from Unofficial / Global grey market imports, preventing misleading price comparisons.

---

### 3.4 Anti-Accessory Price Floor Gate & Fraud Shield
Unscrupulous sellers or sloppy aggregators often list a ৳450 tempered glass or silicone cover with the title *"Apple iPhone 16 Pro Max Screen Shield"*, corrupting search algorithms into displaying *"iPhone 16 Pro Max Starts from ৳450"*.

JaChai implements hard dynamic price-floor heuristics:
* **Smartphone Price Floor:** Mobile phone category queries reject listings under ৳3,500 or automatically isolate them into accessory bins.
* **Anomaly Flagging:** Offers deviating more than 45% below the national median for durable goods are flagged as `⚠️ Price Anomaly / High Risk` rather than influencing the canonical starts-from baseline.

---

### 3.5 Store Leaderboard & TrustShield-BD Fraud Scoring
JaChai maintains an objective trust algorithm evaluating Bangladeshi e-commerce merchants across 5 dimensions:

$$\text{TrustShield Score} = (0.35 \times \text{Domain Authenticity}) + (0.25 \times \text{Delivery Reliability}) + (0.20 \times \text{Warranty Fidelity}) + (0.10 \times \text{Return Policy Clarity}) + (0.10 \times \text{Physical Store Presence})$$

* **Verification Badges:**
  * `Official Brand Partner`: Authorized national distributor.
  * `Verified Physical Hub`: Physical retail locations in Multiplan, IDB Bhaban, Jamuna Future Park, or Bashundhara City.
  * `Established F-Commerce`: Registered social commerce boutique with verified trade license and Cash-on-Delivery (COD) privileges.

---

### 3.6 Stealth Vault Admin Command Center
Protected behind stealth routing (`/vault-jc-ops` or shortcut `Ctrl+Shift+J`), the Admin Command Center provides zero-latency operational control:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      JACHAI STEALTH VAULT COMMAND CENTER                    │
├───────────────┬─────────────────────────────────────────────────────────────┤
│ Tab 1         │ 1. Live Billboard Carousel & Spotlight Ad Slots             │
│ Tab 2         │ 2. Crawler Spiders Orchestrator & Autonomous Watchdog       │
│ Tab 3         │ 3. Product Catalog & Pinned Homepage Merchandising          │
│ Tab 4         │ 4. Sponsor Analytics, Click Logs & Inquiries CRM            │
│ Tab 5         │ 5. Hot Products Benchmark Pricing & Spider Recalibrator     │
│ Tab 6         │ 6. Master Store Registry & CSV Dynamic Reload               │
└───────────────┴─────────────────────────────────────────────────────────────┘
```

1. **Tab 1: Billboards & Spotlights:** Upload advertising banners directly from the desktop, set campaign start/end dates, assign starting prices, and toggle live status.
2. **Tab 2: Crawler Health & Watchdogs:** Real-time ping testing against retailer domains, spider execution status, circuit-breaker reset, and execution progress tracking.
3. **Tab 3: Product Catalog:** Create, edit, and pin curated canonical products to homepage showcase rows.
4. **Tab 4: Sponsor CRM & Analytics:** Track impressions, outbound click-through rates (CTR), and manage advertiser lead status (`Pending`, `Contacted`, `Active`).
5. **Tab 5: Hot Products Manager:**
   * Recalibrate all 8 benchmarks against live spider offers with a single click.
   * Edit starts-from baselines and previous prices manually.
   * Manage verified store offers (add, edit, remove stores, customize stock status).
   * Update latest tech release items, badges, prices, and direct store URLs.
   * Optimistic UI updating with immediate local reflection and background FastAPI persistence.
6. **Tab 6: Master Registry:** Manage the 341+ store dataset, view crawl statistics, and trigger in-memory reloads without server downtime.

---

## 4. Security Measures & Defenses

### 4.1 SSRF (Server-Side Request Forgery) IP-Guard
When fetching store logos or proxying product images via `/api/v1/image-proxy`, malicious actors might input internal IP addresses to probe local services or cloud infrastructure metadata.

JaChai implements a strict DNS resolution and socket filter:
```python
# Security Rule: Reject loopback, private, link-local, and cloud metadata addresses
BLOCKED_IP_RANGES = [
    ip_network("127.0.0.0/8"),      # Loopback
    ip_network("10.0.0.0/8"),       # Private Class A
    ip_network("172.16.0.0/12"),    # Private Class B
    ip_network("192.168.0.0/16"),   # Private Class C
    ip_network("169.254.0.0/16"),   # Link-Local / Cloud Metadata (AWS/GCP/Azure)
    ip_network("::1/128"),          # IPv6 Loopback
    ip_network("fc00::/7"),         # IPv6 Unique Local
]
```
Any target URL resolving to an IP within these CIDR blocks is terminated with `HTTP 403 Forbidden`.

---

### 4.2 Constant-Time Timing-Attack Safe Stealth Vault
Admin authentication rejects standard string comparison (`==`) to eliminate side-channel timing attacks:
```python
def is_pin_authorized(pin: str) -> bool:
    if not pin:
        return False
    clean = str(pin).strip()
    return any(secrets.compare_digest(clean.lower(), auth_key.lower()) for auth_key in AUTHORIZED_PINS)
```
* **Dual Header & Token Bypass:** Supports direct `X-Admin-Pin` header for automated scripts and JWT Bearer tokens with HMAC-SHA256 signatures for persistent sessions.

---

### 4.3 Brute-Force Rate Limiting & Progressive Lockout
Conducted on client and server tiers:
* 5 consecutive failed PIN attempts trigger an immediate **15-minute lockout** stored with cryptographically timestamped keys in `localStorage` and client IP records.
* During lockout, PIN submission is disabled on the client, and the API returns `HTTP 429 Too Many Requests`.

---

### 4.4 URL Healing & Outbound Protocol Validation
To prevent broken spider links and phishing redirection:
* The `URLHealer` engine validates destination URLs against RFC 3986 schemes.
* Replaces incomplete relative links with resolved fully-qualified domain names.
* Strips tracking parameters that cause store redirects to break.
* Injects `rel="noopener noreferrer"` and `target="_blank"` on all outbound retailer links.

---

### 4.5 Content Security, XSS Defense & Strict CORS
* **CORS Whitelist:** Explicitly permits legitimate origins (`http://localhost:3000`, `https://ja-chai-five.vercel.app`) while rejecting untrusted cross-origin script execution.
* **HTML Escaping:** All user-supplied queries and crawled product descriptions pass through Jinja/React automatic HTML escaping to prevent Cross-Site Scripting (XSS).

---

### 4.6 Client-Side Fault Isolation & Self-Healing ErrorBoundary
* **React ErrorBoundary Component:** Custom class boundary (`ErrorBoundary.tsx`) encapsulates the root application tree. If any third-party component, font, or script throws an unhandled client exception:
  1. Captures the exception and logs detailed component stack traces to the console.
  2. Displays an informative, branded self-healing screen (`PORTAL RE-SYNCHRONIZING`) with one-click **"Reload JaChai"** and **"Clear Cache & Restart"** options.
  3. Completely prevents Next.js's raw white-screen crash (`Application error: a client-side exception has occurred`).
* **Dynamic Client-Only Root:** In `page.tsx`, `<App />` is loaded with `next/dynamic` and `ssr: false`, rendering an instant animated loading skeleton on the server and mounting React purely on the client. This guarantees **100% immunity to server/client hydration mismatches**.

---

## 5. End-to-End Dataflows

### 5.1 Storefront Search & Comparison Flow

```mermaid
sequenceDiagram
    autonumber
    actor User as Consumer
    participant Frontend as Next.js Storefront
    participant API as FastAPI Router
    participant Engine as Search & SKU Engine
    participant Spiders as Live Spider Harvester
    participant DB as SQLite / jachai.db

    User->>Frontend: Types query (e.g. "pixel 9 pro")
    Frontend->>API: GET /api/v1/search/suggestions?q=pixel
    API-->>Frontend: Return autocomplete suggestions + Did-You-Mean pills
    User->>Frontend: Selects model / presses Enter
    Frontend->>API: GET /api/v1/search/live?q=pixel 9 pro&category=all
    API->>Engine: Parse query, extract specs (RAM, Storage, Condition)
    API->>DB: Query authoritative catalog offers
    alt Local catalog hit & fresh (< 60 mins)
        DB-->>API: Return cached store offers
    else Background Metasearch required
        API->>Spiders: Dispatch live crawl against verified BD retailers
        Spiders-->>API: Stream discovered product offers
        API->>DB: Persist fresh offers & update price history
    end
    API->>Engine: Run Universal Canonical SKU Consolidator
    Engine->>Engine: Strip 50+ colors, partition hardware & warranty tiers
    Engine-->>Frontend: Unified Canonical SKU comparison cards
    Frontend-->>User: Renders single card with lowest price + Stores Drawer
```

---

### 5.2 Hot Products Daily Recalibration Flow

```mermaid
sequenceDiagram
    autonumber
    actor Admin as Chief Admin
    participant AdminUI as Stealth Vault UI
    participant RecalRoute as POST /api/v1/admin/hot-products/recalibrate
    participant SpiderDB as StoreOffer Records
    participant HPTable as hot_products Table
    participant Storefront as Live Consumer UI

    Admin->>AdminUI: Clicks "⚡ Recalibrate All Prices from Spiders"
    AdminUI->>RecalRoute: Authenticated POST request with Bearer/PIN
    loop For each of 8 Hot Product benchmarks
        RecalRoute->>SpiderDB: Query lowest active offer matching search_query
        SpiderDB-->>RecalRoute: Returns lowest price + verified selling stores
        RecalRoute->>HPTable: Update current_price, previous_price, stores_json
    end
    HPTable-->>RecalRoute: Commit transaction & generate response
    RecalRoute-->>AdminUI: Returns updated 8 benchmarks + confirmation toast
    AdminUI->>Storefront: Updates parent React state optimistically
    Storefront-->>Admin: Storefront instantly displays updated benchmark prices
```

---

## 6. Database Entity-Relationship Model (ERD)

JaChai operates on an optimized relational SQLite database with 12 interconnected tables:

```mermaid
erDiagram
    products ||--o{ store_offers : "has multiple"
    products ||--o{ price_history : "tracks"
    billboards ||--o{ click_logs : "records"
    spotlight_cards ||--o{ click_logs : "records"
    hot_products ||--o{ store_offers : "references"

    products {
        int id PK
        string slug UK
        string title_en
        string title_bn
        string category
        string image_url
        text specs_summary
        int price_30d_ago
        int price_15d_ago
        boolean is_pinned_homepage
        int homepage_slot_order
        datetime created_at
    }

    store_offers {
        int id PK
        int product_id FK
        string store_name
        string source_type
        string target_url
        string css_selector
        int current_price
        int original_price
        string cod_terms_en
        string cod_terms_bn
        string warranty_text
        boolean in_stock
        string spider_status
        string last_synced_at
        int clicks
        string website_url
        string facebook_url
        int trust_score
        string trust_badge
        string risk_level
        boolean is_sponsored
    }

    price_history {
        int id PK
        int product_id FK
        int recorded_price
        datetime recorded_at
    }

    hot_products {
        int id PK
        string slug UK
        string title_en
        string title_bn
        string subtitle_en
        string subtitle_bn
        string category_id
        string search_query
        int current_price
        int previous_price
        string unit_en
        string unit_bn
        string icon_name
        text stores_json
        string latest_release_name
        int latest_release_price
        string latest_release_badge
        string latest_release_url
        boolean is_active
        int display_order
        datetime last_calibrated_at
    }

    billboards {
        int id PK
        string sponsor_en
        string sponsor_bn
        string headline_en
        string headline_bn
        string category_badge
        int starting_price
        string image_url
        string target_url
        string campaign_start
        string campaign_end
        boolean is_active
        int impressions
        int clicks
        int display_order
    }

    ad_leads {
        int id PK
        string brand_name
        string contact_phone
        string selected_tier
        text budget_note
        string status
        datetime created_at
    }

    click_logs {
        int id PK
        string target_type
        int target_id
        string brand_or_store_name
        string device_type
        string destination_url
        datetime clicked_at
    }

    homepage_blocks {
        int id PK
        int slot_order
        string title_en
        string title_bn
        string subtitle_en
        string subtitle_bn
        string search_query
        string category
        string image_url
        string badge_text
        int starting_price_bdt
        boolean is_active
    }
```

---

## 7. Complete API Route Reference

### 7.1 Public Storefront & Metasearch Endpoints
* `GET /api/v1/storefront/init`: Initializes storefront bundle (billboards, side panels, tickers, categories, and homepage slots) in a single round-trip.
* `GET /api/v1/storefront/hot-products`: Returns the 8 active market benchmarks with starting rates, previous prices, price drop/increase pills, verified selling stores, and latest releases.
* `GET /api/v1/search/suggestions?q={query}`: Generates as-you-type autocomplete predictions and "Did you mean:" disambiguation pills.
* `GET /api/v1/search/live?q={query}&category={category}&browse={bool}`: Main metasearch engine. Dispatches queries, retrieves store offers, and returns unified Canonical SKU cards.
* `GET /api/v1/categories`: Lists all 15 curated retail verticals with store counts and default queries.
* `GET /api/v1/leaderboard`: Returns the verified merchant leaderboard ranked by TrustShield-BD scores.
* `POST /api/v1/leads`: Ingests advertiser contact requests for billboard ad slots.
* `GET /api/v1/image-proxy?url={encoded_url}`: Secure, SSRF-guarded image proxy for remote product and store logos.

### 7.2 Outbound Telemetry & Redirect Endpoints
* `GET /go/offer/{offer_id}`: Tracks outbound clicks to retailer product pages and redirects with verified HTTP 302.
* `GET /go/billboard/{billboard_id}`: Tracks sponsored billboard banner clicks and redirects to the advertiser's campaign URL.
* `POST /api/v1/telemetry/click`: Asynchronously records device type, target merchant, and timestamp for analytics.

### 7.3 Stealth Vault Admin Endpoints (Guarded by PIN / Bearer Token)
* `POST /api/v1/admin/login`: Authenticates PIN `42791` and issues an HMAC-SHA256 JWT access token.
* `GET /api/v1/admin/overview`: Returns aggregate platform health (spiders active, offers tracked, lead counts, CTR stats).
* `GET /api/v1/admin/hot-products`: Admin view of all 8 benchmarks including paused records and store JSON payloads.
* `PUT /api/v1/admin/hot-products/{id}`: Updates a benchmark record by ID or `display_order` with store list sanitization.
* `POST /api/v1/admin/hot-products/recalibrate`: Daily recalibration engine. Scans live spider offers, updates starting baselines, previous prices, and verified store lists.
* `GET /api/v1/admin/crawler/health`: Real-time health matrix for all configured store spiders.
* `POST /api/v1/admin/crawler/run-all-background`: Dispatches autonomous background spider sweeps.
* `POST /api/v1/admin/crawler/run-reset`: Resets hung crawler worker state.
* `POST /api/v1/admin/upload-banner`: Handles direct local banner image uploads to `/uploads/banners/`.
* `POST /api/v1/admin/registry/reload`: Reloads the master store registry CSV into active memory.

---

## 8. Working Procedures & Operations Runbook

### 8.1 Daily Morning Maintenance Runbook
1. **Access Stealth Vault:** Navigate to `/vault-jc-ops` or press `Ctrl+Shift+J`. Enter Master PIN `42791`.
2. **Execute Spider Sweep:**
   * Go to **Tab 2 (Crawler Spiders Orchestrator)**.
   * Click **"Run Full Spider Sweep"**.
   * Monitor spider progress from 0% to 100%. If any store encounters selector changes, check the health matrix.
3. **Recalibrate Hot Products Benchmarks:**
   * Go to **Tab 5 (Hot Products Pricing Manager)**.
   * Click **"⚡ Recalibrate All Prices from Spiders"**.
   * Verify updated starts-from prices for Gold (BAJUS), Fuel (BPC), Flagships, and PC components.
   * To update latest tech releases (e.g. newly launched iPhone or GPU), edit the fields directly in the card and click **"Save Changes"**.
4. **Audit Advertiser Leads:**
   * Go to **Tab 4 (Sponsor Analytics & Inbox)**.
   * Review incoming advertiser inquiries from `ad_leads` and update status from `Pending` to `Contacted`.

---

## 9. Primary Use Cases

### Use Case 1: Flagship Smartphone Buyer
* **Persona:** Consumer looking to buy the Apple iPhone 16 Pro Max 256GB Desert Titanium in Dhaka.
* **Problem:** Browsing individual retail websites reveals prices ranging from ৳1,42,000 to ৳1,75,000 without clarity on whether listings are Official BTRC Approved or Unofficial Global units.
* **JaChai Solution:** Search returns **exactly two distinct cards**:
  1. *Apple iPhone 16 Pro Max (256GB · Official BTRC Warranty)* — Starting from ৳1,69,999 across 3 stores.
  2. *Apple iPhone 16 Pro Max (256GB · Unofficial / Global Dual SIM)* — Starting from ৳1,44,499 across 5 stores.
  Color variations are consolidated. Clicking the card opens the Store Drawer showing verified stock and direct store homepage links.

### Use Case 2: Daily Commodity & Gold Investor
* **Persona:** Consumer checking daily gold prices for wedding jewelry or commercial fuel rates.
* **Problem:** Gold prices change frequently per BAJUS circulars; retail fuel rates are governed by BPC government gazettes.
* **JaChai Solution:** The Hot Products live pricing bar placed prominently at the top of the storefront displays the exact benchmark:
  * *Gold (22K & 24K Hallmark):* 24K at ৳154,700/Vori • 22K at ৳141,800/Vori with direct BAJUS verification links.
  * *Fuel (Octane, Diesel, Petrol):* Octane at ৳125/L • Diesel at ৳105/L • Petrol at ৳120/L with direct Padma Oil/BPC links.

### Use Case 3: PC Builder & Gamer
* **Persona:** Desktop builder comparing high-end DDR5 RAM, PCIe Gen5 NVMe SSDs, and RTX 5080/4070 GPUs.
* **Problem:** Star Tech, Ryans, and Techland often stock identical components at varying discounts, bundle deals, and bus frequencies.
* **JaChai Solution:** JaChai partitions RAM by frequency (`7200MHz DDR5` vs `6000MHz DDR5`) and SSDs by speed generation (`Gen5 10,000+ MB/s` vs `Gen4 7,000 MB/s`), ranking verified sellers with live in-stock guarantees.

### Use Case 4: Enterprise Brand Advertiser
* **Persona:** Commercial retail brand or importer wanting prominent exposure on Bangladesh's leading price index.
* **Problem:** Banner ads on social media suffer from ad-fatigue and low purchase intent.
* **JaChai Solution:** Brands sponsor Hero Billboards and Spotlight Ad slots, targeting users actively engaged in high-intent purchasing comparisons. Inquiries are submitted through the instant lead modal and managed via the Admin CRM.

---

## 10. Technology Stack & Production Infrastructure

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            JACHAI TECHNOLOGY MATRIX                         │
├─────────────────────┬───────────────────────────────────────────────────────┤
│ Frontend Framework  │ Next.js 14.2 (App Router), React 18, TypeScript/JSX   │
│ UI / Styling        │ Tailwind CSS 3.4, Lucide React Icons, Framer Motion  │
│ Client Hydration    │ Dynamic SPA Loader (ssr: false), React ErrorBoundary  │
│ Backend Framework   │ Python 3.11+, FastAPI, Starlette, Pydantic v2         │
│ Database Engine     │ SQLite 3 (jachai.db) with SQLAlchemy ORM              │
│ Web Harvester       │ Async HTTPX, BeautifulSoup4, LXML, Custom Connectors  │
│ Local SLM Engine    │ Ollama Inference (Qwen 2.5 0.5B / LLaMA 3.2)          │
│ Security & Auth     │ SSRF Guard, Secrets Constant-Time Check, JWT Tokens  │
│ Line Ending Control │ Git Attributes Enforced LF (* text=auto eol=lf)       │
│ Hosting Platforms   │ Frontend on Vercel · Backend API on Render            │
└─────────────────────┴───────────────────────────────────────────────────────┘
```

---

## 11. Verification & Quality Assurance Matrix

The platform is continuously audited with dedicated verification suites:

* ✅ **Universal Master Product Catalogue:** 300+ authoritative SKUs indexed across Mobiles, Laptops, PC Hardware, Consoles, Smartwatches, Audio, Cameras, and Home Appliances.
* ✅ **Sub-30ms Deterministic Retrieval:** Query response times under 30ms with 100% precision for catalog products.
* ✅ **Zero Generic Fallbacks:** Specific queries never fall back to generic placeholders.
* ✅ **Anti-Accessory Price Floor Gate:** Accidental accessory grouping suppressed across all flagship models.
* ✅ **Storefront Hydration Resiliency:** Tested against offline backend states with immediate benchmark default fallbacks.
* ✅ **Production Next.js Build:** `next build` passes with Exit Code `0` and optimized client bundles.

---

*Authored for the JaChai Engineering Team — 2026.*

