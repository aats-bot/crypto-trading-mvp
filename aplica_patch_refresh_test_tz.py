# salva como: aplica_patch_refresh_test_tz.py
from pathlib import Path
import re

p = Path("tests/unit/test_authentication.py")
src = p.read_text(encoding="utf-8")

backup = p.with_suffix(p.suffix + ".bak_refresh_tz")
backup.write_text(src, encoding="utf-8")

changed = src

# 1) Tornar fromtimestamp(...) timezone-aware (UTC)
changed, n1 = re.subn(
    r"datetime\.fromtimestamp\(\s*payload\[['\"]exp['\"]\]\s*\)",
    "datetime.fromtimestamp(payload['exp'], UTC)",
    changed,
)

# 2) Garantir que UTC esteja importado
if "from datetime import datetime, UTC" not in changed:
    changed = re.sub(
        r"from datetime import datetime(\s*,\s*timedelta)?",
        lambda m: m.group(0) + ", UTC" if "UTC" not in m.group(0) else m.group(0),
        changed,
        count=1,
    )

p.write_text(changed, encoding="utf-8")
print(f"[OK] Patch aplicado em {p} (fromtimestamp->aware: {n1} mudança(s)).")
print(f"Backup: {backup}")
