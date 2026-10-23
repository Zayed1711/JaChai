import re
from bd_stores_registry import extract_budget_and_clean_query

q = "50mm f1.8 lens"
cleaned, _ = extract_budget_and_clean_query(q)
print("cleaned 1:", cleaned)
c2 = re.sub(r"f/(\d+(?:\.\d+)?)", r"f\1", cleaned, flags=re.IGNORECASE)
c2 = re.sub(r"\b([a-zA-Z]*\d+)\.(\d+)\b", r"\1_\2", c2)
print("cleaned 2:", c2)
tokens = [t.strip() for t in re.sub(r"[^\w\s\u0980-\u09FF-]", " ", c2.lower()).split() if len(t.strip()) >= 2]
print("tokens before filter:", tokens)
tokens = [t for t in tokens if not re.match(r"^f\d+$", t)]
print("tokens after filter:", tokens)
