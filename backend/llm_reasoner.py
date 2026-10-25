import json
import logging
import os
import re
import time
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import httpx

try:
    from .bd_stores_registry import (
        BANNED_FOREIGN_CURRENCIES,
        BANNED_INTERNATIONAL_DOMAINS,
        RETAIL_VERTICALS,
        extract_budget_and_clean_query,
    )
except ImportError:
    from bd_stores_registry import (
        BANNED_FOREIGN_CURRENCIES,
        BANNED_INTERNATIONAL_DOMAINS,
        RETAIL_VERTICALS,
        extract_budget_and_clean_query,
    )

logger = logging.getLogger("jachai.llm_reasoner")

OLLAMA_API_URL = os.environ.get("OLLAMA_API_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:1.5b")
OLLAMA_TIMEOUT = httpx.Timeout(connect=0.5, read=1.5, write=1.0, pool=1.0)
_OLLAMA_CIRCUIT_OPEN_UNTIL: float = 0.0

STOP_WORDS = {
    "price", "in", "bd", "bangladesh", "best", "buy", "online",
    "original", "authentic", "official", "unofficial", "shop", "store",
    "for", "with", "at", "the", "a", "an", "of", "and", "to", "deals",
    "deal", "discount", "cheap", "দাম", "কত", "টাকা", "বাংলাদেশ",
}

ACCESSORY_KEYWORDS = [
    "case", "cases", "cover", "covers", "back cover", "silicone case",
    "leather case", "clear case", "protector", "screen protector", "tempered glass",
    "matte protector", "privacy glass", "lens protector",
    "camera lens protector", "cable", "cables", "cord", "adapter", "charger",
    "strap", "straps", "watch strap", "band", "bands", "watch band", "loop band", "trail loop", "ocean band", "alpine loop", "magnetic link", "sport loop", "sport band", "bumper", "pouch", "bag", "camera bag", "dslr bag", "backpack", "laptop bag",
    "sleeve", "cooling pad", "laptop stand", "phone holder", "skin", "sticker", "dummy", "box only",
    "keyboard protector", "lens cap",
]

CORE_ACCESSORY_TOKENS = ACCESSORY_KEYWORDS

BANNED_ENTITY_TOKENS = [
    "savarkar", "gandhi", "nehru", "politician", "political", "statue",
    "monument", "historical", "flag", "parliament", "protest", "memorial",
    "leader", "freedom_fighter", "swami", "vivekananda",
]

PHONE_BRANDS = [
    "iphone", "apple", "samsung", "xiaomi", "redmi", "realme", "vivo",
    "oppo", "pixel", "oneplus", "motorola", "infinix", "tecno", "honor", "nothing",
]

# Bilingual & Banglish dictionary so Bengali/Banglish queries match English store catalogs
BENGALI_BANGLISH_TO_ENGLISH_MAP = {
    "আইফোন": "iphone",
    "স্যামসাং": "samsung",
    "গ্যালাক্সি": "galaxy",
    "শাওমি": "xiaomi",
    "রেডমি": "redmi",
    "রিয়েলমি": "realme",
    "ওয়ানপ্লাস": "oneplus",
    "ভিভো": "vivo",
    "অপ্পো": "oppo",
    "ইনফিনিক্স": "infinix",
    "টেকনো": "tecno",
    "মোবাইল": "smartphone",
    "স্মার্টফোন": "smartphone",
    "ফোন": "phone",
    "ল্যাপটপ": "laptop",
    "ম্যাকবুক": "macbook",
    "কম্পিউটার": "desktop pc",
    "মনিটর": "monitor",
    "প্রসেসর": "processor",
    "গ্রাফিক্স কার্ড": "graphics card",
    "মাদারবোর্ড": "motherboard",
    "র্যাম": "ram",
    "এসএসডি": "ssd",
    "পাঞ্জাবি": "panjabi",
    "টিশার্ট": "t-shirt",
    "গেঞ্জি": "t-shirt",
    "শার্ট": "shirt",
    "থ্রি পিস": "three piece",
    "সালোয়ার কামিজ": "salwar kameez",
    "জামদানি": "jamdani",
    "শাড়ি": "saree",
    "শাড়ি": "saree",
    "কাতান": "katan saree",
    "বেনারসি": "benaroshi saree",
    "জুতা": "shoes",
    "স্নিকার্স": "sneakers",
    "স্যান্ডেল": "sandal",
    "ঘড়ি": "watch",
    "ঘড়ি": "watch",
    "স্মার্টওয়াচ": "smartwatch",
    "সাইকেল": "bicycle",
    "ই-বাইক": "electric bike",
    "ইলেকট্রিক বাইক": "electric bike",
    "ব্যাটারি বাইক": "electric bike",
    "ব্যাটারি সাইকেল": "electric bike",
    "স্কুটার": "electric scooter",
    "স্কুটি": "electric scooter",
    "ফ্রিজ": "refrigerator",
    "রেফ্রিজারেটর": "refrigerator",
    "এসি": "air conditioner",
    "টিভি": "smart tv",
    "ওয়াশিং মেশিন": "washing machine",
    "ওভেন": "microwave oven",
    "ব্লেন্ডার": "blender",
    "সানস্ক্রিন": "sunscreen",
    "ফেসওয়াশ": "face wash",
    "ময়েশ্চারাইজার": "moisturizer",
    "সিরাম": "serum",
    "লিপস্টিক": "lipstick",
    "সরিষার তেল": "mustard oil",
    "ঘি": "ghee",
    "মধু": "honey",
    "চাল": "rice",
    "সোনার আংটি": "gold ring",
    "সোনার গহনা": "gold jewellery",
    "সোনা": "gold",
    "ঝুমকা": "jhumka earrings",
    "চোকার": "choker necklace",
    "কানের দুল": "earrings",
    "নেকলেস": "necklace",
    "চুড়ি": "bangles",
    "জার্সি": "jersey",
    "যোগা ম্যাট": "yoga mat",
    # Common Banglish phonetics
    "tekyon": "walton takyon",
    "takyon": "walton takyon",
    "volton": "walton",
    "voltoni": "walton",
    "ডিএসএলআর": "dslr camera",
    "ক্যামেরা": "camera",
    "betari saikel": "electric bike",
    "battery saikel": "electric bike",
    "saikel": "bicycle",
    "samsang": "samsung",
    "sumsung": "samsung",
    "iphon": "iphone",
    "ifone": "iphone",
    "aifon": "iphone",
    "leptop": "laptop",
    "labtop": "laptop",
    "panzabi": "panjabi",
    "punjabi": "panjabi",
    "shari": "saree",
    "sharee": "saree",
    "jamdhani": "jamdani",
    "ghori": "watch",
    "juta": "shoes",
    "snikars": "sneakers",
    "frij": "refrigerator",
    "shorishar tel": "mustard oil",
    "khati ghi": "ghee",
    "modhu": "honey",
}

_BN_DIGIT_TRANS = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")

# Broad category head nouns (when searched alone without a model number, triggers Mode B Price-Range comparison)
BROAD_CATEGORY_QUERIES = {
    "mobile", "mobiles", "mobile phone", "mobile phones", "smartphone", "smartphones", "phone", "phones",
    "android phone", "gaming phone", "camera phone", "budget phone",
    "laptop", "laptops", "computer", "computers", "pc", "desktop", "desktop pc", "gaming pc", "monitor",
    "cycle", "cycles", "bicycle", "bicycles", "electric bike", "electronic bike", "electronic bikes",
    "e-bike", "ebike", "ev", "electric vehicle", "scooter", "electric scooter",
    "panjabi", "shirt", "t-shirt", "polo", "jeans", "kurti", "three piece", "salwar kameez", "clothing", "fashion", "apparel",
    "saree", "jamdani saree", "katan saree", "silk saree", "handloom saree",
    "jewelry", "jewellery", "gold", "gold jewellery", "fashion jewellery", "imitation jewellery", "minimal jewelry",
    "jhumka", "earrings", "necklace", "choker", "ring", "bangles",
    "sneakers", "shoes", "footwear", "sandal", "loafers",
    "watch", "watches", "smartwatch", "luxury watch", "casio watch",
    "refrigerator", "fridge", "ac", "air conditioner", "smart tv", "tv", "washing machine", "oven", "home appliances",
    "skincare", "sunscreen", "face wash", "serum", "cosmetics", "beauty",
    "sportswear", "gym", "jersey", "yoga mat",
    "grocery", "organic food", "honey", "ghee", "mustard oil", "snacks",
}

# Categories that inherently compare by Shop Starting Price Range (Engine B) unless an exact SKU is given
ENGINE_B_CATEGORIES = {
    "fine-jewelry",
    "budget-jewelry", "sportswear-gym",
}


def translate_bengali_and_banglish_for_store(query: str) -> str:
    """Delegates to the 4-Stage Universal Translator & Phonetic Aligner in translator.py and expands 2-letter acronyms."""
    try:
        from .translator import translate_and_align_query
    except ImportError:
        from translator import translate_and_align_query
    res = translate_and_align_query(query)
    r_low = (res or "").strip().lower()
    if r_low == "ac":
        return "air conditioner"
    if r_low == "tv":
        return "smart led tv"
    if r_low == "pc":
        return "desktop pc"
    return res


def classify_comparison_mode(raw_query: str, category_id: str) -> str:
    """
    Determines whether a search should run in:
      - 'exact_sku' (Mode A: Specific model comparison e.g. 'iPhone 15 Pro Max', 'Samsung S24', 'Ryzen 5 5600G')
      - 'price_range' (Mode B: Broad category or style/boutique comparison e.g. 'mobile phone', 'saree', 'jewelry')
    """
    translated = translate_bengali_and_banglish_for_store(raw_query).lower().strip()
    cleaned, _ = extract_budget_and_clean_query(translated)
    cleaned = " ".join(w for w in cleaned.split() if w not in STOP_WORDS).strip()

    # 1. If query is a broad category term (e.g. 'mobile phone', 'laptop', 'electric bike', 'saree'), use Mode B
    if cleaned in BROAD_CATEGORY_QUERIES:
        return "price_range"

    # 2. If query contains an alphanumeric model number (e.g. '15', 's24', 'a55', 'm2', '5600g', 'rtx 4060', 'v200'), use Mode A
    has_model_number = bool(re.search(r"\b(?:[a-z]*\d+[a-z]*)\b", cleaned))
    if has_model_number and True:
        return "exact_sku"

    # 3. If category is inherently non-SKU fashion/saree/jewelry, use Mode B
    if category_id in ENGINE_B_CATEGORIES:
        return "price_range"

    # 4. If query has >= 2 specific tokens (e.g., Brand + Line like 'MacBook Air', 'OnePlus Nord'), use Mode A
    tokens = cleaned.split()
    if len(tokens) >= 2:
        return "exact_sku"

    return "price_range"


class AccessoryList(list):
    def __bool__(self) -> bool:
        return len(self) > 0

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, bool):
            return bool(self) == other
        return super().__eq__(other)


NEGATED_ACCESSORY_REGEX = re.compile(
    r"(?i)\b(?:without|no|except|not|excluding|chara|bade|বাদে|ছাড়া)\s+(?:any\s+|original\s+)?(?:charger|adapter|cable|case|cover|back cover|glass|screen protector|protector|box|strap|earphone|headphone)\b"
)
NEGATED_ACCESSORY_SUFFIX_REGEX = re.compile(
    r"(?i)\b(?:charger|adapter|cable|case|cover|back cover|glass|screen protector|protector|box|strap|earphone|headphone)\s+(?:chara|bade|ছাড়া|বাদে)\b"
)


def extract_mandatory_anchor_tokens(raw_query: str) -> List[str]:
    if not raw_query:
        return []

    cleaned, _ = extract_budget_and_clean_query(raw_query)
    cleaned = NEGATED_ACCESSORY_REGEX.sub(" ", cleaned)
    cleaned = NEGATED_ACCESSORY_SUFFIX_REGEX.sub(" ", cleaned)

    # Translate any Bengali/Banglish words so anchors match English store product titles
    cleaned = translate_bengali_and_banglish_for_store(cleaned)

    cleaned = re.sub(r"[^\w\s\u0980-\u09FF-]", " ", cleaned.lower())
    tokens = [t.strip() for t in cleaned.split() if (len(t.strip()) >= 2 or t.strip().isdigit()) and t.strip() not in STOP_WORDS]
    tokens = [t for t in tokens if not re.match(r"^f\d+$", t)]
    return tokens or [raw_query.strip().lower()]


def user_requested_accessory(raw_query: str) -> AccessoryList:
    q_low = (raw_query or "").lower()
    q_cleaned = NEGATED_ACCESSORY_REGEX.sub(" ", q_low)
    q_cleaned = NEGATED_ACCESSORY_SUFFIX_REGEX.sub(" ", q_cleaned)

    matches = []
    for acc in ACCESSORY_KEYWORDS:
        if re.search(r"\b" + re.escape(acc) + r"\b", q_cleaned):
            matches.append(acc)

    return AccessoryList(matches)


def matches_anchor_tokens(title: str, anchor_tokens: List[str], *args: Any, **kwargs: Any) -> bool:
    if not title:
        return False
    # Normalize commas inside numbers so '10,000mAh' matches '10000'
    t_low = re.sub(r"(\d),(\d)", r"\1\2", title.lower())

    raw_query = kwargs.get("raw_query", "")
    if args and isinstance(args[0], str):
        raw_query = args[0]

    q_low = translate_bengali_and_banglish_for_store(raw_query or "").lower()

    # 1. Brand Collision Gate
    for pb in PHONE_BRANDS:
        if pb in anchor_tokens or pb in q_low.split():
            other_brands = [b for b in PHONE_BRANDS if b != pb and b != "apple"]
            for ob in other_brands:
                if re.search(r"\b" + re.escape(ob) + r"\b", t_low) and not re.search(r"\b" + re.escape(pb) + r"\b", t_low):
                    return False
            if pb == "iphone" and "iphone" not in t_low:
                return False
            elif pb == "samsung" and ("samsung" in t_low or "galaxy" in t_low):
                pass
            elif pb != "iphone" and not re.search(r"\b" + re.escape(pb) + r"\b", t_low):
                return False

    # 2. Model Variant Hard Gate (e.g. 'iPhone 15' must not match 'iPhone 15 Pro' unless 'pro' is in query;
    # and 'iPhone 15 Pro' MUST contain 'pro')
    strict_modifiers = ["pro", "max", "ultra", "plus", "fe", "mini", "lite"]
    q_tokens_set = set(q_low.split()) | set(anchor_tokens)
    for mod in strict_modifiers:
        if mod in q_tokens_set and not re.search(r"\b" + re.escape(mod) + r"\b", t_low):
            return False
    # Reverse guard: if user searched a specific numbered model like 'iPhone 15 Pro' (without 'max'), do not mix 'Pro Max'
    has_num = any(any(ch.isdigit() for ch in tok) for tok in q_tokens_set)
    if has_num and ("iphone" in q_tokens_set or "samsung" in q_tokens_set or "galaxy" in q_tokens_set or "redmi" in q_tokens_set or "pixel" in q_tokens_set):
        for rev_mod in ("max", "ultra", "plus"):
            if rev_mod not in q_tokens_set and re.search(r"\b" + re.escape(rev_mod) + r"\b", t_low):
                return False

    # 2.5 Hardware Generation Invariant Gate (Google Search Architecture entity alignment)
    # When user asks for a specific generation (e.g. Pixel 9, iPhone 16, Note 13, Galaxy S24),
    # conflicting generations (e.g. Pixel 10, Pixel 8, Note 30, iPhone 15) MUST be immediately rejected.
    GEN_SERIES_PATTERNS = [
        (r"\bpixel\s*(\d+[a-z]?)\b", r"\bpixel\s*(\d+[a-z]?)\b"),
        (r"\biphone\s*(\d+[a-z]?)\b", r"\biphone\s*(\d+[a-z]?)\b"),
        (r"\b(?:galaxy\s*)?s(\d+[a-z]?)\b", r"\b(?:galaxy\s*)?s(\d+[a-z]?)\b"),
        (r"\b(?:redmi\s*)?note\s*(\d+[a-z]?)\b", r"\b(?:redmi\s*)?note\s*(\d+[a-z]?)\b"),
        (r"\b(?:oneplus|nord)\s*(\d+[a-z]?)\b", r"\b(?:oneplus|nord)\s*(\d+[a-z]?)\b"),
        (r"\b(?:gopro\s*(?:hero)?|hero)\s*(\d+)\b", r"\b(?:gopro\s*(?:hero)?|hero)\s*(\d+)\b"),
        (r"\bwatch\s*(?:series\s*)?(\d+)\b", r"\bwatch\s*(?:series\s*)?(\d+)\b"),
    ]
    for q_pattern, t_pattern in GEN_SERIES_PATTERNS:
        q_gen_m = re.search(q_pattern, q_low)
        if q_gen_m:
            q_gen = q_gen_m.group(1).lower()
            t_gen_m = re.search(t_pattern, t_low)
            if t_gen_m:
                t_gen = t_gen_m.group(1).lower()
                if q_gen != t_gen:
                    return False

    # 3. Partition Anchor Tokens into Core Hardware Anchors and Accessory Anchors
    acc_set = set(ACCESSORY_KEYWORDS) | {
        "case", "cases", "cover", "covers", "protector", "glass", "tempered",
        "charger", "adapter", "cable", "cables", "cord", "strap", "straps",
        "pouch", "bag", "stand", "screen",
    }

    core_anchors = []
    accessory_anchors = []
    for tok in anchor_tokens:
        tok_low = tok.lower().strip()
        if tok_low in acc_set:
            accessory_anchors.append(tok_low)
        else:
            core_anchors.append(tok_low)

    # Broad category synonyms (so 'smartphone' matches 'iPhone 15' or 'Samsung Galaxy' in store titles)
    SYNONYM_GROUPS = {
        "smartphone": ("smartphone", "phone", "iphone", "galaxy", "redmi", "xiaomi", "realme", "oppo", "vivo", "oneplus", "pixel", "infinix", "tecno"),
        "phone": ("phone", "smartphone", "iphone", "galaxy", "redmi", "xiaomi", "realme", "oppo", "vivo", "oneplus", "pixel"),
        "laptop": ("laptop", "notebook", "macbook", "ultrabook", "thinkpad", "ideapad", "vivobook", "zenbook", "pavilion", "victus", "inspiron", "loq"),
        "bicycle": ("bicycle", "cycle", "bike", "mtb", "veloce", "duranta", "phoenix", "trinx"),
        "shoes": ("shoe", "shoes", "sneaker", "sneakers", "loafer", "boot", "sandal", "footwear"),
        "watch": ("watch", "watches", "smartwatch", "smart-watch", "ghori", "timepiece"),
        "smartwatch": ("smartwatch", "smart-watch", "smart watch", "watch", "smart ghori"),
        "cream": ("cream", "crem", "krim", "barrier cream", "cica", "relief cream"),
        "sneakers": ("sneaker", "sneakers", "shoe", "shoes", "kicks"),
    }

    SYNONYM_GROUPS.update({
                "jhumka": ("jhumka", "jhumko", "earring", "earrings", "dul", "kaner dul", "studs", "amethyst", "flower", "cler"),
        "jhumko": ("jhumka", "jhumko", "earring", "earrings", "dul"),
        "choker": ("choker", "necklace", "har", "chokers", "pendant"),
        "necklace": ("necklace", "choker", "har", "pendant", "chain", "set"),
        "earrings": ("earring", "earrings", "jhumka", "jhumko", "dul", "stud", "studs", "tops"),
        "earring": ("earring", "earrings", "jhumka", "jhumko", "dul", "stud", "studs"),
        "churi": ("churi", "chudi", "bangle", "bangles", "bala", "reshmi"),
        "bangles": ("churi", "chudi", "bangle", "bangles", "bala", "reshmi"),
        "payel": ("payel", "paiel", "anklet", "nupur", "chain"),
        "anklet": ("payel", "paiel", "anklet", "nupur"),
        "ring": ("ring", "angti", "band", "rings"),
        "oil": ("oil", "tel", "hair oil", "serum"),
        "jersey": ("jersey", "kit", "tshirt", "t-shirt", "shirt"),
        "kit": ("kit", "jersey", "tshirt", "t-shirt"),
        "denim": ("denim", "jeans", "pant", "trousers"),
        "jeans": ("jeans", "denim", "pant", "trousers"),
        "dslr": ("dslr", "dsl", "camera", "eos", "alpha", "nikon", "canon", "mirrorless"),
        "camera": ("camera", "dslr", "dsl", "mirrorless", "eos", "alpha", "nikon", "canon", "gopro", "osmo", "instax"),
        "heels": ("heel", "heels", "shoe", "shoes", "sandal"),
        "bicycle": ("bicycle", "cycle", "bike", "mtb", "veloce", "duranta", "phoenix", "trinx", "foxter", "upland", "core", "bmx"),
        "cycle": ("cycle", "bicycle", "bike", "mtb", "veloce", "duranta", "phoenix", "trinx", "foxter", "upland", "core", "bmx"),
        "bike": ("bike", "bicycle", "cycle", "mtb", "ebike", "e-bike", "takyon", "revoo", "veloce", "duranta", "phoenix", "trinx"),
        "mtb": ("mtb", "mountain", "bicycle", "cycle", "bike", "veloce", "duranta", "phoenix", "trinx", "foxter"),
        "dslr": ("dslr", "eos", "alpha", "nikon", "canon", "mirrorless", "camera"),
        "camera": ("camera", "dslr", "mirrorless", "eos", "alpha", "nikon", "canon", "gopro", "osmo", "instax"),
        "ac": ("ac", "air conditioner", "split", "inverter", "ton", "gree", "haier", "midea", "singer", "walton"),
        "tv": ("tv", "television", "bravia", "qled", "oled", "led", "android tv", "smart tv", "inch"),
        "refrigerator": ("refrigerator", "fridge", "freezer", "frost", "liter", "ltr"),
        "fridge": ("fridge", "refrigerator", "freezer", "frost", "liter", "ltr"),
        "samsung": ("samsung", "galaxy"),
        "galaxy": ("galaxy", "samsung"),
    })

    soft_modifiers = {'fc', 'club', 'home', 'away', 'third', 'kit', 'innerwear', 'boxer', 'briefs', 'galaxy', 'eos', 'alpha', 'inspiron', 'pavilion', 'ideapad', 'vivobook', 'vostro', 'modern', 'aspires', 'aspire', 'pure', 'cow', 'sundarban', 'chinigura', 'dhakai', 'tangail', 'mens', 'womens', 'ladies', 'girls', '5g', 'aero', 'hybrid', 'boys', 'racing', 'global', 'men', 'business', 'full', 'non', 'unofficial', 'series', 'portable', 'luxury', 'manual', 'mens', 'bangladesh', 'kids', 'digital', 'auto', 'commuter', 'road', 'student', '4k', 'premium', 'automatic', 'womens', 'pedal', 'official', 'smart', 'hd', 'office', 'waterproof', 'budget', 'intact', 'gear', 'touch', 'wireless', 'gents', 'edition', 'fhd', 'non-gear', 'women', 'original', 'ladies', 'mountain', 'screen', 'authentic', 'double', 'door', 'doors', 'single', 'triple', 'side', 'french', 'frost', 'non-frost', 'inverter', 'direct', 'cool', 'split', 'window', 'front', 'top', 'load', 'liter', 'ltr', 'ton', 'inch', 'oled', 'qled', 'curved', 'fast', 'speed', 'alloy', 'disc'}
    # When searching for a watch, band, or ghori, 'smart' is a critical non-negotiable technology anchor
    if any(w in (raw_query or "").lower() for w in ("watch", "ghori", "band")):
        soft_modifiers = soft_modifiers - {"smart"}
    # Separate hard brand/model/noun anchors from soft descriptive modifiers
    hard_anchors = [t for t in core_anchors if t not in soft_modifiers]
    if not hard_anchors:
        hard_anchors = core_anchors[:1]


    # Compound pairs: if either half matches, consider the pair satisfied!
    COMPOUND_EQUIVALENTS = [
                {"oxidized", "jhumka"},
        {"choker", "necklace"},
        {"imitation", "earrings"},
        {"artificial", "necklace"},
        {"silver", "ring"},
        {"reshmi", "churi"},
        {"payel", "anklet"},
        {"bridal", "set"},
        {"kundan", "earrings"},
        {"hair", "oil"},
        {"onion", "oil"},
        {"face", "wash"},
        {"moisturizer", "cream"},
        {"matte", "lipstick"},
        {"dslr", "camera"},
        {"denim", "jeans"},
        {"argentina", "jersey"},
        {"brazil", "jersey"},
        {"womens", "heels"},
        {"party", "heels"},
        {"mountain", "bike"},
        {"manual", "bicycle"},
        {"aero", "bike"},
        {"gear", "cycle"},
        {"double", "door"},
        {"single", "door"},
        {"triple", "door"},
        {"side", "door"},
        {"direct", "cool"},
        {"non", "frost"},
        {"smart", "tv"},
        {"microwave", "oven"},
        {"washing", "machine"},
        {"water", "purifier"},
        {"electric", "kettle"},
        {"cotton", "panjabi"},
        {"formal", "shirt"},
        {"polo", "shirt"},
        {"samsung", "galaxy"},
        {"asus", "vivobook"},
        {"asus", "zenbook"},
        {"apple", "macbook"},
        {"apple", "iphone"},
        {"apple", "ipad"},
    ]
    for pair in COMPOUND_EQUIVALENTS:
        if pair.issubset(set(hard_anchors)):
            # Check if at least one token from the pair matches the title
            if any(
                re.search(r"\b" + re.escape(p_tok) + r"\b", t_low)
                or any(re.search(r"\b" + re.escape(syn) + r"\b", t_low) is not None for syn in SYNONYM_GROUPS.get(p_tok, ()))
                for p_tok in pair
            ):
                # Remove the remaining unsatisfied token of this pair from hard_anchors so it won't drop the product!
                hard_anchors = [t for t in hard_anchors if t not in pair]
                if not hard_anchors:
                    return True

    for tok in hard_anchors:
        tok_root = tok[:-1] if (tok.endswith("s") and len(tok) > 3) else tok
        tok_plural = tok + "s" if not tok.endswith("s") else tok

        matched = (
            re.search(r"\b" + re.escape(tok) + r"\b", t_low) is not None
            or re.search(r"\b" + re.escape(tok_root) + r"\b", t_low) is not None
            or re.search(r"\b" + re.escape(tok_plural) + r"\b", t_low) is not None
            or tok in t_low
        )

        if not matched and tok in SYNONYM_GROUPS:
            matched = any(re.search(r"\b" + re.escape(syn) + r"\b", t_low) is not None for syn in SYNONYM_GROUPS[tok])

        if not matched:
            # Primary device nouns (watch, tv, monitor, camera, console, tablet, ac, fridge) are NON-NEGOTIABLE!
            # e.g., 'apple watch' MUST contain 'watch', 'samsung tv' MUST contain 'tv'
            if tok in ("watch", "smartwatch", "tv", "monitor", "camera", "tablet", "pad", "console", "refrigerator", "fridge", "ac"):
                return False

            # If the unmatched token is a flexible category noun ('laptop', 'phone', 'saree', etc.)
            # and we already have other specific brand/model tokens in hard_anchors, do not reject the product!
            if len(hard_anchors) >= 2 and tok in ("laptop", "phone", "smartphone", "mobile", "shoe", "shoes", "sneakers", "cycle", "bicycle", "saree", "shirt", "panjabi", "ssd", "ram", "processor", "graphics", "card", "earbuds", "power", "bank"):
                continue
            return False

    if accessory_anchors:
        matched_any_acc = False
        for tok in accessory_anchors:
            tok_root = tok[:-1] if (tok.endswith("s") and len(tok) > 3) else tok
            if (
                re.search(r"\b" + re.escape(tok) + r"\b", t_low) is not None
                or re.search(r"\b" + re.escape(tok_root) + r"\b", t_low) is not None
                or tok in t_low
            ):
                matched_any_acc = True
                break
        if not matched_any_acc:
            return False

    return True


def deterministic_intent_fallback(raw_query: str, selected_category: Optional[str] = None) -> Dict[str, Any]:
    q_clean = raw_query.strip()
    translated_q = translate_bengali_and_banglish_for_store(q_clean)
    q_lower = translated_q.lower()

    vertical = "MOBILE_GADGET"
    min_price = 500
    max_price = 350000

    if any(re.search(r"\b" + re.escape(k) + r"\b", q_lower) for k in ["bicycle", "cycle", "mtb", "mountain bike", "aero bike", "road bike", "duranta", "veloce", "phoenix", "trinx", "foxter"]) and not any(e in q_lower for e in ["electric", "e-bike", "ebike", "battery", "takyon", "scooter"]):
        vertical = "BICYCLES_MTB"
        min_price = 4500
        max_price = 65000
    elif any(re.search(r"\b" + re.escape(k) + r"\b", q_lower) for k in ["electric bike", "e-bike", "ebike", "electric scooter", "takyon", "revoo", "reevo", "yadea", "tailg"]):
        vertical = "CYCLES_EV"
        min_price = 25000
        max_price = 220000
    elif any(re.search(r"\b" + re.escape(k) + r"\b", q_lower) for k in ["camera", "dslr", "mirrorless", "gopro", "canon", "nikon", "sony a6400", "action camera"]):
        vertical = "CAMERAS_PHOTOGRAPHY"
        min_price = 14000
        max_price = 350000
    elif any(re.search(r"\b" + re.escape(k) + r"\b", q_lower) for k in ["iphone", "phone", "smartphone", "samsung", "redmi", "pixel", "oneplus", "xiaomi", "realme", "vivo", "oppo", "ipad"]):
        vertical = "MOBILE_GADGET"
        min_price = 12000
        max_price = 350000
    elif any(re.search(r"\b" + re.escape(k) + r"\b", q_lower) for k in ["earbuds", "airpods", "tws", "power bank", "powerbank", "smartwatch", "gadget"]):
        vertical = "MOBILE_GADGET"
        min_price = 800
        max_price = 120000
    elif any(re.search(r"\b" + re.escape(k) + r"\b", q_lower) for k in ["laptop", "notebook", "macbook", "ultrabook", "thinkpad", "elitebook", "ideapad", "vivobook", "zenbook", "victus", "pavilion", "inspiron", "latitude"]):
        vertical = "LAPTOP_PC"
        min_price = 32000
        max_price = 600000
    elif any(re.search(r"\b" + re.escape(k) + r"\b", q_lower) for k in ["desktop", "pc", "ssd", "ram", "gpu", "processor", "intel", "ryzen", "motherboard", "monitor", "keyboard", "mouse"]):
        vertical = "LAPTOP_PC"
        min_price = 1800
        max_price = 500000
    elif any(re.search(r"\b" + re.escape(k) + r"\b", q_lower) for k in ["panjabi", "punjabi", "saree", "shari", "kurti", "shirt", "linen", "dress", "clothing", "abaya", "hoodie", "polo", "jeans", "pant", "fabrilife", "aarong", "sailor"]):
        vertical = "FASHION_APPAREL"
        min_price = 300
        max_price = 60000
    elif any(re.search(r"\b" + re.escape(k) + r"\b", q_lower) for k in ["watch", "watches", "chronograph", "automatic watch", "casio", "tissot", "rolex", "seiko"]):
        vertical = "WATCHES_HOROLOGY"
        min_price = 500
        max_price = 600000
    elif any(re.search(r"\b" + re.escape(k) + r"\b", q_lower) for k in ["sneaker", "sneakers", "shoe", "shoes", "kicks", "loafer", "sandal", "bata", "apex"]):
        vertical = "SNEAKERS_FOOTWEAR"
        min_price = 500
        max_price = 60000
    elif any(re.search(r"\b" + re.escape(k) + r"\b", q_lower) for k in ["gold", "diamond", "necklace", "ring", "bracelet", "earring", "earrings", "jhumka", "choker", "silver", "jewelry", "jewellery", "bhori"]):
        vertical = "JEWELRY"
        min_price = 150
        max_price = 1500000
    elif any(re.search(r"\b" + re.escape(k) + r"\b", q_lower) for k in ["honey", "ghee", "mustard oil", "soybean oil", "cooking oil", "snack", "chips", "biscuit", "chaal", "basmati rice", "rice", "organic food", "dates", "groceries", "grocery"]):
        vertical = "GROCERY_SNACKS"
        min_price = 60
        max_price = 25000

    if selected_category and selected_category != "all":
        cat_lower = selected_category.strip().lower()
        from bd_stores_registry import CATEGORY_VERTICAL_MAP
        if cat_lower in CATEGORY_VERTICAL_MAP:
            vertical = CATEGORY_VERTICAL_MAP[cat_lower]

    noise_pattern = r"(?i)\b(price\s+in\s+bangladesh|price\s+in\s+bd|bd\s+price|best\s+price|in\s+bangladesh|in\s+bd|online|buy|best|cheap|authentic|original|official|offer|deal|discount)\b"
    simplified = re.sub(noise_pattern, "", translated_q).strip()
    simplified = " ".join(simplified.split()) or translated_q

    is_acc = bool(user_requested_accessory(q_clean))

    return {
        "vertical": vertical,
        "store_search_keyword": simplified,
        "raw_query": q_clean,
        "min_sanity_price_bdt": min_price if not is_acc else 100,
        "max_sanity_price_bdt": max_price,
        "is_accessory_query": is_acc,
        "exclude_accessory_tokens": [] if is_acc else CORE_ACCESSORY_TOKENS,
        "reasoner": "deterministic_fallback",
    }


async def analyze_search_intent(raw_query: str, selected_category: Optional[str] = None) -> Dict[str, Any]:
    global _OLLAMA_CIRCUIT_OPEN_UNTIL

    clean_q = raw_query.strip()
    if not clean_q:
        return deterministic_intent_fallback("", selected_category)

    now = time.time()
    if now < _OLLAMA_CIRCUIT_OPEN_UNTIL:
        return deterministic_intent_fallback(clean_q, selected_category)

    prompt = f"""You are a specialized Bangladeshi e-commerce search intent classifier for JaChai (যা চাই).
Analyze the user's shopping search query and respond STRICTLY in JSON format with these exact keys:
- "vertical": Choose exactly one from ["MOBILE_GADGET", "LAPTOP_PC", "FASHION_APPAREL", "SNEAKERS_FOOTWEAR", "WATCHES_HOROLOGY", "JEWELRY", "GROCERY_SNACKS"]
- "store_search_keyword": Distilled, concise English product name (translate Bengali/Banglish to English and strip fluff like 'price in bd', 'buy', 'best') so store search endpoints find exact items.
- "min_sanity_price_bdt": Integer estimated minimum reasonable price in BDT.
- "max_sanity_price_bdt": Integer estimated maximum reasonable price in BDT.
- "is_accessory_query": Boolean, true ONLY if the user is explicitly searching for a case, cover, glass, cable, or accessory.

User query: "{clean_q}"
Category context: "{selected_category or 'all'}"
JSON Response:"""

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "format": "json",
        "stream": False,
        "options": {"temperature": 0.0, "num_ctx": 2048},
    }

    try:
        async with httpx.AsyncClient(timeout=OLLAMA_TIMEOUT) as client:
            resp = await client.post(OLLAMA_API_URL, json=payload)
            if resp.status_code == 200:
                body = resp.json()
                parsed = json.loads(body.get("response", "").strip())
                base_fallback = deterministic_intent_fallback(clean_q, selected_category)
                v = parsed.get("vertical", "").upper()
                if v not in ["MOBILE_GADGET", "LAPTOP_PC", "FASHION_APPAREL", "SNEAKERS_FOOTWEAR", "WATCHES_HOROLOGY", "JEWELRY", "GROCERY_SNACKS"]:
                    v = base_fallback["vertical"]

                kw = parsed.get("store_search_keyword", "").strip() or base_fallback["store_search_keyword"]
                is_acc = base_fallback["is_accessory_query"]

                return {
                    "vertical": v,
                    "store_search_keyword": kw,
                    "raw_query": clean_q,
                    "min_sanity_price_bdt": base_fallback["min_sanity_price_bdt"],
                    "max_sanity_price_bdt": base_fallback["max_sanity_price_bdt"],
                    "is_accessory_query": is_acc,
                    "exclude_accessory_tokens": [] if is_acc else CORE_ACCESSORY_TOKENS,
                    "reasoner": f"ollama_{OLLAMA_MODEL}",
                }
    except Exception:
        _OLLAMA_CIRCUIT_OPEN_UNTIL = time.time() + 60.0

    return deterministic_intent_fallback(clean_q, selected_category)


def is_bangladesh_store_url(url: str) -> bool:
    if not url or not isinstance(url, str):
        return False
    url_lower = url.lower()
    for banned in BANNED_INTERNATIONAL_DOMAINS:
        if banned in url_lower:
            return False
    return True


def verify_and_filter_candidates(
    query_intent: Any, candidates: Any = None
) -> List[Dict[str, Any]]:
    if isinstance(query_intent, list) and isinstance(candidates, (str, dict)):
        candidates_list = query_intent
        intent_dict = {"raw_query": candidates, "vertical": "MOBILE_GADGET"} if isinstance(candidates, str) else candidates
    elif isinstance(query_intent, str) and isinstance(candidates, list):
        intent_dict = {"raw_query": query_intent, "vertical": "MOBILE_GADGET"}
        candidates_list = candidates
    elif isinstance(query_intent, dict) and isinstance(candidates, list):
        intent_dict = query_intent
        candidates_list = candidates
    else:
        candidates_list = candidates if isinstance(candidates, list) else (query_intent if isinstance(query_intent, list) else [])
        intent_dict = query_intent if isinstance(query_intent, dict) else {}

    if not candidates_list:
        return []

    vertical = intent_dict.get("vertical", "MOBILE_GADGET")
    min_p = intent_dict.get("min_sanity_price_bdt", 50)
    max_p = intent_dict.get("max_sanity_price_bdt", 2000000)
    raw_q = intent_dict.get("raw_query", "").lower()
    anchor_tokens = extract_mandatory_anchor_tokens(raw_q)
    requested_acc = user_requested_accessory(raw_q)

    verified = []

    for item in candidates_list:
        title = item.get("title", "")
        t_lower = title.lower()
        url = item.get("product_url") or item.get("target_url") or ""
        price = item.get("price") or item.get("current_price") or 0

        if anchor_tokens and not matches_anchor_tokens(title, anchor_tokens, raw_q):
            continue

        if url and not is_bangladesh_store_url(url):
            continue

        if any(curr in t_lower for curr in ["$", "usd", "₹", "inr", "cad", "£", "gbp"]):
            continue

        if any(banned in t_lower for banned in BANNED_ENTITY_TOKENS):
            continue

        if not requested_acc:
            if any(re.search(r"(?i)\b" + re.escape(tok) + r"\b", t_lower) for tok in ACCESSORY_KEYWORDS):
                continue
        else:
            if not any(re.search(r"(?i)\b" + re.escape(tok) + r"\b", t_lower) for tok in requested_acc):
                continue

        if vertical in ("FASHION_APPAREL", "JEWELRY"):
            if any(ew in t_lower for ew in ["phone", "laptop", "macbook", "ssd", "ram", "intel", "ryzen", "earbuds", "headphone"]):
                continue
        elif vertical in ("MOBILE_GADGET", "LAPTOP_PC"):
            if any(cw in t_lower for cw in ["panjabi", "punjabi", "saree", "shari", "kurti", "shirt", "dress", "bra", "lingerie"]):
                continue

        if price > 0:
            if price < 100 or price > int(max_p * 2.5):
                continue

        verified.append(item)

    return verified
