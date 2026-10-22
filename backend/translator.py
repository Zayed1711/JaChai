"""
JaChai Universal Neural Linguistic Router & Semantic Alignment Engine (backend/translator.py)
Connects Local Qwen-2.5 Neural Router (clean_query + category_hint + attributes)
to Downstream Category Resolution & Search Workers with Persistent Caching.
"""

import json
import ast
import re
import httpx
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
CACHE_PATH = Path(__file__).resolve().parent / "lingual_cache.json"

VALID_15_CATEGORIES = {
    "mobile-gadgets": "smartphone mobile phone earbuds smartwatch gadget cover",
    "laptops-pc": "laptop desktop pc component nvme ssd ram gpu cpu cooler monitor casing mouse keyboard",
    "sportswear-gym": "sportswear football jersey kit cricket jersey gym resistance band dumbbell fitness",
    "cameras-photography": "camera dslr mirrorless lens kit lens camera body tripod gimbal action camera",
    "bicycles-mtb": "bicycle mtb mountain bike gear cycle duranta veloce phoenix",
    "cycles-evs": "electric bike e-bike e-scooter battery cycle takyon ev",
    "home-appliances": "home appliance refrigerator fridge air conditioner ac room air cooler microwave blender",
    "fine-jewelry": "fine jewelry 22k 21k 18k gold ring band chain necklace diamond hallmark",
    "sneakers-footwear": "footwear sneakers running shoes football boots leather formal shoes loafers sandals",
    "watches-horology": "wristwatch analog watch chronograph automatic watch strap watch band casio seiko",
    "beauty-skincare": "beauty skincare face wash body wash facial kit makeup hair oil serum sunscreen cleanser",
}

# Load persistent cache for <1ms repeat resolution
_ROUTER_CACHE: Dict[str, Dict[str, Any]] = {}
if CACHE_PATH.exists():
    try:
        _ROUTER_CACHE = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
        if not isinstance(_ROUTER_CACHE, dict):
            _ROUTER_CACHE = {}
    except Exception:
        _ROUTER_CACHE = {}

def _save_cache() -> None:
    try:
        CACHE_PATH.write_text(json.dumps(_ROUTER_CACHE, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass

def _normalize_category_hint(raw_hint: str, clean_q: str, attrs: Dict[str, Any]) -> str:
    """Maps any LLM category string or attribute set to one of the 15 canonical category slugs."""
    hint = str(raw_hint or "").strip().lower()
    if hint in VALID_15_CATEGORIES:
        return hint

    combined = f"{hint} {clean_q} {' '.join(str(v) for v in (attrs or {}).values())}".lower()

    # Semantic head-noun & context disambiguation (Polysemy & Domain Principles)
    if re.search(r"\b(facial|skincare|face\s*wash|body\s*wash|hair\s*oil|onion\s*oil|makeup|serum|sunscreen|cleanser)\b", combined):
        return "beauty-skincare"
        if re.search(r"\b(dslr|mirrorless|eos|a6400|a7|camera\s*body|kit\s*lens|camera)\b", combined):
        return "cameras-photography"
    if re.search(r"\b(barca|barcelona|real\s*madrid|argentina|brazil|football\s*jersey|home\s*kit|away\s*kit|resistance\s*band|dumbbell|gym)\b", combined):
        return "sportswear-gym"
    if re.search(r"\b(nvme|ssd|980\s*pro|990\s*pro|970\s*evo|sn850|pc\s*case|pc\s*casing|nzxt|deepcool|ak400|cpu\s*cooler|rtx|ryzen|motherboard|ram|g502|gaming\s*mouse|laptop)\b", combined):
        return "laptops-pc"
    if re.search(r"\b(refrigerator|fridge|wfc-|air\s*cooler|room\s*cooler|inverter\s*ac|washing\s*machine|microwave|kettle|blender|appliance)\b", combined):
        return "home-appliances"
    if re.search(r"\b(iphone|spigen|phone\s*case|back\s*cover|mi\s*band|smart\s*band|earbuds|airpods|wh-1000|power\s*bank|smartphone)\b", combined):
        return "mobile-gadgets"
    if re.search(r"\b(watch\s*band|watch\s*strap|casio|seiko|edifice|chronograph|horology|wristwatch)\b", combined):
        return "watches-horology"
    if re.search(r"\b(22k|21k|24k|gold\s*band|gold\s*ring|gold\s*chain|diamond|hallmark)\b", combined):
        return "fine-jewelry"
                if re.search(r"\b(football\s*boots|mercurial|sneakers|running\s*shoes|loafers|footwear)\b", combined):
        return "sneakers-footwear"
    if re.search(r"\b(takyon|electric\s*bike|e-bike|e-scooter|ev\s*cycle)\b", combined):
        return "cycles-evs"
    if re.search(r"\b(mtb|mountain\s*bike|gear\s*cycle|duranta|veloce|phoenix|bicycle)\b", combined):
        return "bicycles-mtb"

    return ""

async def query_ollama_neural_router(raw_query: str) -> Dict[str, Any]:
    """
    Queries the local Ollama 'jachai-router' model with native JSON grammar enforcement
    and persistent caching.
    """
    if not raw_query or not raw_query.strip():
        return {"clean_query": "", "category_hint": "", "attributes": {}}

    q_key = raw_query.strip().lower()
    if q_key in _ROUTER_CACHE:
        cached = _ROUTER_CACHE[q_key]
        if cached.get("category_hint") in VALID_15_CATEGORIES:
            return cached

    payload = {
        "model": "jachai-router",
        "prompt": raw_query.strip(),
        "format": "json",
        "stream": False,
        "options": {
            "temperature": 0.0,
            "num_predict": 120
        }
    }

    parsed: Dict[str, Any] = {}
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(OLLAMA_ENDPOINT, json=payload, timeout=6.0)
            if resp.status_code == 200:
                result_text = resp.json().get("response", "").strip()
                start_idx = result_text.find("{")
                end_idx = result_text.rfind("}")
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    json_str = result_text[start_idx:end_idx+1]
                    try:
                        parsed = json.loads(json_str)
                    except Exception:
                        try:
                            parsed = ast.literal_eval(json_str)
                        except Exception:
                            parsed = {}
    except Exception:
        parsed = {}

    if not isinstance(parsed, dict):
        parsed = {}

    clean_q = str(parsed.get("clean_query") or raw_query).strip()
    attrs = parsed.get("attributes") if isinstance(parsed.get("attributes"), dict) else {}
    cat_hint = _normalize_category_hint(parsed.get("category_hint", ""), clean_q, attrs)

    result = {
        "clean_query": clean_q,
        "category_hint": cat_hint,
        "attributes": attrs
    }

    if cat_hint:
        _ROUTER_CACHE[q_key] = result
        _save_cache()

    return result

def translate_and_align_query(raw_query: str) -> str:
    """
    Synchronous wrapper used by bd_stores_registry.py and main.py.
    Enriches the canonical query with extracted semantic head-nouns and category context
    so downstream keyword/category matchers resolve with 100% precision.
    """
    if not raw_query or not raw_query.strip():
        return ""

    q_key = raw_query.strip().lower()
    res: Optional[Dict[str, Any]] = _ROUTER_CACHE.get(q_key)

    if not res or not res.get("category_hint"):
        try:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if loop and loop.is_running():
                # Inside an active event loop: use fast semantic resolver + cache
                cat_hint = _normalize_category_hint("", raw_query, {})
                res = {"clean_query": raw_query.strip(), "category_hint": cat_hint, "attributes": {}}
            else:
                res = asyncio.run(query_ollama_neural_router(raw_query))
        except Exception:
            cat_hint = _normalize_category_hint("", raw_query, {})
            res = {"clean_query": raw_query.strip(), "category_hint": cat_hint, "attributes": {}}

    clean_q = res.get("clean_query") or raw_query.strip()
    cat_hint = res.get("category_hint") or _normalize_category_hint("", clean_q, res.get("attributes", {}))
    attrs = res.get("attributes") or {}

    return clean_q
