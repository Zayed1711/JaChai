import json
import urllib.request
import re
from typing import Dict, Any, List, Optional

OLLAMA_API_URL = "http://127.0.0.1:11434/api/generate"
OLLAMA_MODEL = "jachai-router"

def call_ollama_linguistic_router(raw_query: str) -> Dict[str, Any]:
    """
    Invokes the local Ollama SLM (jachai-router) for linguistic routing,
    Banglish translation, and query decomposition.
    """
    clean_q = raw_query.strip()
    if not clean_q:
        return {"clean_query": "", "category_hint": "mobile-gadgets", "attributes": {}}

    try:
        req = urllib.request.Request(
            OLLAMA_API_URL,
            data=json.dumps({
                "model": OLLAMA_MODEL,
                "prompt": clean_q,
                "stream": False,
                "format": "json"
            }).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=3.5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            parsed = json.loads(data.get("response", "{}"))
            return {
                "clean_query": parsed.get("clean_query", clean_q),
                "category_hint": parsed.get("category_hint", "mobile-gadgets"),
                "attributes": parsed.get("attributes", {})
            }
    except Exception:
        # Fast local fallback
        return {
            "clean_query": clean_q,
            "category_hint": "mobile-gadgets",
            "attributes": {}
        }


def slm_verify_candidate(candidate_title: str, query: str, anchor_tokens: List[str]) -> bool:
    """
    SLM Verification Gate:
    1. Verifies that candidate physically matches the searched product entity.
    2. Blocks accessory traps (cases, covers, cables) when device was searched.
    3. Blocks cross-brand bleed (Apple TV for Walton query).
    """
    if not candidate_title or not query:
        return False
        
    t_low = candidate_title.lower()
    q_low = query.lower()

    # Accessory trap check
    is_acc_query = any(a in q_low for a in ("case", "cover", "protector", "glass", "charger", "cable", "strap"))
    if not is_acc_query:
        if re.search(r"\b(case|cover|back cover|silicone case|screen protector|tempered glass|camera protector|cable|charger|power adapter|skin)\b", t_low):
            return False

    # Check mandatory anchor tokens
    for tok in anchor_tokens:
        tok_low = tok.lower()
        if tok_low in ("phone", "mobile", "smart", "laptop", "watch", "tv", "camera"):
            continue
        if tok_low not in t_low:
            return False

    return True
