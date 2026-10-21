import sys
import csv
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(".").resolve()
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

from fastapi.testclient import TestClient
import main as backend_main
from translator import translate_and_align_query
from bd_stores_registry import resolve_category_or_none

client = TestClient(backend_main.app)
csv_file = ROOT / "ja_chai_250_master_test_suite.csv"

if not csv_file.exists():
    print("Error: Test suite CSV not found.")
    sys.exit(1)

print("=" * 105)
print(" EXECUTING 250-QUERY MASTER SQA TEST SUITE")
print("=" * 105)

passed = 0
failed = 0
category_stats = {}

with open(csv_file, mode="r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

start_time = time.perf_counter()

for idx, row in enumerate(rows, 1):
    tc_id = row["Test_ID"]
    grp = row["Category_Group"]
    q = row["Query"]
    exp_cat = row["Expected_Category"]

    if grp not in category_stats:
        category_stats[grp] = {"passed": 0, "failed": 0}

    rewritten = translate_and_align_query(q)
    got_cat, _ = resolve_category_or_none(rewritten)

    if got_cat == exp_cat:
        passed += 1
        category_stats[grp]["passed"] += 1
    else:
        failed += 1
        category_stats[grp]["failed"] += 1

elapsed = time.perf_counter() - start_time

print("=" * 105)
print(f" 250-QUERY TEST EXECUTION FINISHED IN {elapsed:.2f} SECONDS")
print(f" TOTAL PASSED: {passed}/250 | TOTAL FAILED: {failed}/250")
print("=" * 105)
print(" CATEGORY-WISE PERFORMANCE BREAKDOWN:")
print("-" * 105)
for grp, stats in category_stats.items():
    p = stats["passed"]
    f = stats["failed"]
    rate = (p / (p + f)) * 100 if (p + f) > 0 else 0
    print(f"   * {grp:<28} -> Passed: {p:02d}/25 | Failed: {f:02d}/25 | Success Rate: {rate:5.1f}%")
print("=" * 105)
