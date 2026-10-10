import re
import glob

for fpath in glob.glob("backend/app/api/v1/endpoints/*.py"):
    with open(fpath, "r", encoding="utf-8") as f:
        text = f.read()
    routes = re.findall(r'@router\.(?:post|get|put|delete|patch)\(\s*["\']([^"\']+)["\']', text)
    if routes:
        print(f"{fpath}:")
        for r in routes:
            print(f"  {r}")
