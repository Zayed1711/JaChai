#!/usr/bin/env python3
"""Offline routing eval: no API or network. Runs your query->budget->category pipeline from
bd_stores_registry.py against eval/queries.jsonl and reports where it routes each query.

  python eval/route_eval.py backend/          # dir that contains bd_stores_registry.py
"""
import importlib, json, sys
from pathlib import Path

backend = Path(sys.argv[1] if len(sys.argv) > 1 else "backend").resolve()
sys.path.insert(0, str(backend))
reg = importlib.import_module("bd_stores_registry")
queries = [json.loads(l) for l in (Path(__file__).parent / "queries.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]

ok = bad = 0
for q in queries:
    cleaned, budget = reg.extract_budget_and_clean_query(q["q"])
    # Use the no-default resolver when the module has it; the legacy one sends unmatched queries to mobile.
    resolver = getattr(reg, "resolve_category_or_none", reg.resolve_category_from_query)
    cat_id, meta = resolver(cleaned)
    got = meta["csv_category"] if meta else ""
    exp = q.get("expected_category", "")
    garbage = not q.get("expect_results", True)
    route_ok = (exp.lower() in got.lower()) if exp else False
    if garbage and cat_id is None:
        garbage = False
        route_ok = True
        exp = ""
    budget_ok = (budget == q["max_price"]) if q.get("max_price") else (budget is None)
    problems = []
    if garbage:
        problems.append(f"garbage query was routed to [{cat_id}] instead of 'no match'")
    elif not route_ok:
        problems.append(f"routed to [{cat_id}], expected '{exp}'")
    if not budget_ok:
        problems.append(f"budget={budget}, expected {q.get('max_price')}")
    if cleaned.strip() != q["q"].strip() and budget is None:
        problems.append(f"query changed without a budget: {q['q']!r} -> {cleaned!r}")
    if q.get("max_price") and budget_ok and any(str(q['max_price']) in t or t in "২৫০০০" for t in cleaned.split()):
        problems.append(f"budget number still in query: {cleaned!r}")
    if problems:
        bad += 1
        print(f"FAIL {q['id']} {q['q']!r}: " + "; ".join(problems))
    else:
        ok += 1
print(f"\nrouting pass: {ok}/{ok + bad}")
