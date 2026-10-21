"""Security and bug audit for main.py"""
import re

src = open('main.py', encoding='utf-8').read()
lines = src.splitlines()
issues = []

for i, line in enumerate(lines, 1):
    s = line.strip()
    # f-string SQL injection risk
    if re.search(r'\bf["\']', s) and any(k in s.upper() for k in ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'WHERE']):
        issues.append(f'main.py:{i}: POTENTIAL SQL INJECTION via f-string: {s[:100]}')
    # JSONResponse without explicit status_code
    if 'JSONResponse' in s and 'status_code' not in s:
        issues.append(f'main.py:{i}: JSONResponse without explicit status_code: {s[:80]}')
    # background task scheduling
    if 'background_tasks.add_task' in s or 'asyncio.create_task' in s:
        issues.append(f'main.py:{i}: background task call: {s[:80]}')
    # Hardcoded secrets/passwords
    low = s.lower()
    if any(k in low for k in ['secret_key =', 'password =', 'api_key =', 'token =']) and not s.startswith('#'):
        issues.append(f'main.py:{i}: HARDCODED SECRET? {s[:80]}')
    # Missing db.rollback in except that has db.commit
    if 'db.commit()' in s:
        context = '\n'.join(lines[max(0,i-10):i+5])
        if 'except' in context and 'db.rollback()' not in context:
            issues.append(f'main.py:{i}: db.commit() in try block without db.rollback() in except')

for iss in issues[:60]:
    print(iss)
print(f'\n--- Total: {len(issues)} issues ---')
