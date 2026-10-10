import re
import json

with open('.reference_bundle/index.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Look for routes or router setup
routes = set(re.findall(r'path:\s*["\']([^"\']+)["\']', content))
print("Found routes:", sorted(list(routes)))

# Look for roles
roles = set(re.findall(r'role:\s*["\']([^"\']+)["\']', content, re.IGNORECASE))
print("Found roles:", sorted(list(roles)))

# Look for keywords like Doctor, Nurse, Patient, Receptionist, Admin
for kw in ['Receptionist', 'Nurse', 'Clinician', 'Doctor', 'Patient', 'Facility', 'Admin', 'Triage', 'Workbench', 'Referral']:
    matches = len(re.findall(re.escape(kw), content, re.IGNORECASE))
    print(f"Keyword '{kw}': {matches} occurrences")

# Look for top-level component or page names / titles
titles = set(re.findall(r'title:\s*["\']([^"\']+)["\']', content))
print("Sample titles:", list(titles)[:20])
