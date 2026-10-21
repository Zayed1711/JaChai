#!/usr/bin/env python3
"""JaChai eval harness (stdlib only).

  python eval/run_eval.py collect --base http://localhost:8000 --out eval/runs/baseline.json
  python eval/run_eval.py score eval/runs/baseline.json
  python eval/run_eval.py compare eval/runs/baseline.json eval/runs/after_fix.json
  python eval/run_eval.py selftest

Metrics (all computed from queries.jsonl expectations, no manual labels needed yet):
  zero_result_rate        queries that should return results but returned none
  pollution@10            share of top-10 results whose category != expected category
  banned_term_hits        results whose title contains a must_not_contain term
  budget_violations       offers priced above the query's max_price
  garbage_returned        nonsense queries that still returned results
  p95_latency_ms
"""
import argparse, json, sys, time, urllib.parse, urllib.request, statistics
from pathlib import Path

HERE = Path(__file__).parent
SEARCH_PATH = "/api/v1/search/live"   # <- change if your route/param differs
QUERY_PARAM = "q"                      # <- change if your param differs
RESULT_KEYS = ("products", "results", "items", "data")
TITLE_KEYS = ("title_en", "title", "name")
CATEGORY_KEYS = ("category", "category_name")
OFFER_KEYS = ("offers", "store_offers")
PRICE_KEYS = ("current_price", "price_bdt", "price")


def load_queries(path=HERE / "queries.jsonl"):
    return [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]


def first(d, keys, default=None):
    for k in keys:
        if isinstance(d, dict) and d.get(k) is not None:
            return d[k]
    return default


def extract_products(payload):
    if isinstance(payload, list):
        return payload
    got = first(payload, RESULT_KEYS, [])
    if isinstance(got, dict):  # e.g. {"products": {...}} or nested
        got = first(got, RESULT_KEYS, [])
    return got or []


def fetch(base, q, timeout=60):
    url = base.rstrip("/") + SEARCH_PATH + "?" + urllib.parse.urlencode({QUERY_PARAM: q})
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            payload = json.loads(r.read().decode("utf-8"))
        err = None
    except Exception as e:  # keep going; record the failure
        payload, err = {}, repr(e)
    return payload, (time.perf_counter() - t0) * 1000, err


def collect(base, out, fetcher=fetch):
    runs = []
    for item in load_queries():
        payload, ms, err = fetcher(base, item["q"])
        runs.append({"id": item["id"], "q": item["q"], "latency_ms": ms, "error": err,
                     "products": extract_products(payload)})
        print(f"{item['id']} {item['q']!r}: {len(runs[-1]['products'])} products, {ms:.0f} ms"
              + (f"  ERROR {err}" if err else ""))
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(json.dumps(runs, ensure_ascii=False, indent=1), encoding="utf-8")
    print("saved", out)


def score(run_path, verbose=True):
    queries = {q["id"]: q for q in load_queries()}
    runs = json.loads(Path(run_path).read_text(encoding="utf-8"))
    m = dict(n=0, should_return=0, zero_result=0, pollution_num=0, pollution_den=0,
             banned_hits=0, budget_violations=0, garbage_total=0, garbage_returned=0, errors=0)
    lat, fails = [], []
    for r in runs:
        spec = queries[r["id"]]
        prods = r["products"][:10]
        m["n"] += 1
        lat.append(r["latency_ms"])
        if r.get("error"):
            m["errors"] += 1
        if spec.get("expect_results", True):
            m["should_return"] += 1
            if not r["products"]:
                m["zero_result"] += 1
                fails.append((r["id"], r["q"], "zero results"))
        else:
            m["garbage_total"] += 1
            if r["products"]:
                m["garbage_returned"] += 1
                fails.append((r["id"], r["q"], f"garbage query returned {len(r['products'])} results"))
        exp = spec.get("expected_category", "").lower()
        for p in prods:
            title = str(first(p, TITLE_KEYS, "")).lower()
            cat = str(first(p, CATEGORY_KEYS, "")).lower()
            if exp:
                m["pollution_den"] += 1
                if exp not in cat:
                    m["pollution_num"] += 1
                    fails.append((r["id"], r["q"], f"wrong category [{cat}] : {title[:60]}"))
            for bad in spec.get("must_not_contain", []):
                if bad.lower() in title:
                    m["banned_hits"] += 1
                    fails.append((r["id"], r["q"], f"banned term '{bad}' : {title[:60]}"))
            cap = spec.get("max_price")
            if cap:
                for o in first(p, OFFER_KEYS, []) or [p]:
                    price = first(o, PRICE_KEYS)
                    if isinstance(price, (int, float)) and price > cap:
                        m["budget_violations"] += 1
                        fails.append((r["id"], r["q"], f"price {price} > cap {cap} : {title[:50]}"))
    p95 = statistics.quantiles(lat, n=20)[18] if len(lat) >= 20 else max(lat or [0])
    summary = {
        "queries": m["n"],
        "zero_result_rate": round(m["zero_result"] / max(m["should_return"], 1), 3),
        "pollution@10": round(m["pollution_num"] / max(m["pollution_den"], 1), 3),
        "banned_term_hits": m["banned_hits"],
        "budget_violations": m["budget_violations"],
        "garbage_returned": f"{m['garbage_returned']}/{m['garbage_total']}",
        "errors": m["errors"],
        "p95_latency_ms": round(p95),
    }
    if verbose:
        print(json.dumps(summary, indent=1))
        if fails:
            print(f"\n{len(fails)} failures (first 40):")
            for f in fails[:40]:
                print("  ", *f)
    return summary


def compare(a, b):
    sa, sb = score(a, False), score(b, False)
    print(f"{'metric':22}{'before':>12}{'after':>12}")
    for k in sa:
        print(f"{k:22}{str(sa[k]):>12}{str(sb[k]):>12}")


def selftest():
    """Offline check of the scorer using a fake API with known bugs."""
    def fake(base, q, timeout=0):
        ql = q.lower()
        if "bike" in ql or "saikel" in ql:
            prods = [{"title_en": "Duranta E-Bike", "category": "Cycles & Electric Vehicles (EVs)",
                      "offers": [{"current_price": 90000}]},
                     {"title_en": "MSI B550 Motherboard", "category": "Laptops, Desktops & Computer Components",
                      "offers": [{"current_price": 15000}]}]
        elif "under 85000" in ql:
            prods = [{"title_en": "ASUS TUF Gaming Laptop", "category": "Laptops, Desktops & Computer Components",
                      "offers": [{"current_price": 120000}]}]
        elif "asdf" in ql:
            prods = [{"title_en": "Random Thing", "category": "x", "offers": []}]
        else:
            prods = []
        return {"products": prods}, 5.0, None
    out = HERE / "runs" / "_selftest.json"
    collect("mock", out, fetcher=fake)
    s = score(out)
    assert s["banned_term_hits"] >= 1 and s["budget_violations"] >= 1 and s["garbage_returned"] == "1/1", s
    assert s["pollution@10"] > 0 and s["zero_result_rate"] > 0, s
    out.unlink()
    print("\nSELFTEST OK: scorer detects leak, banned term, budget breach, garbage, zero-results")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("collect"); c.add_argument("--base", default="http://localhost:8000"); c.add_argument("--out", required=True)
    s = sub.add_parser("score"); s.add_argument("run")
    k = sub.add_parser("compare"); k.add_argument("a"); k.add_argument("b")
    sub.add_parser("selftest")
    a = ap.parse_args()
    if a.cmd == "collect": collect(a.base, a.out)
    elif a.cmd == "score": score(a.run)
    elif a.cmd == "compare": compare(a.a, a.b)
    else: selftest()
