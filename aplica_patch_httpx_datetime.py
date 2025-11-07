#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Patch automático:
1) httpx: data= (bytes/str) -> content=
2) datetime.utcnow() -> datetime.now(UTC)  (com import do UTC)
   e datetime.datetime.utcnow() -> datetime.datetime.now(datetime.UTC)
"""

from __future__ import annotations
import os
import re
from typing import List, Tuple

EXCLUDE_DIRS = {".git", ".hg", ".svn", ".venv", "venv", "env", "__pycache__", "node_modules", "dist", "build", ".mypy_cache"}
TARGET_DIRS = ["src", "tests"]  # ajuste se quiser varrer outros diretórios também
BACKUP_SUFFIX = ".bak_httpx_datetime"

# -------- util --------
def iter_py_files() -> List[str]:
    roots = [d for d in TARGET_DIRS if os.path.isdir(d)]
    if not roots:
        roots = ["."]
    results: List[str] = []
    for root in roots:
        for dp, dn, fl in os.walk(root):
            dn[:] = [d for d in dn if d not in EXCLUDE_DIRS]
            for f in fl:
                if f.endswith(".py"):
                    results.append(os.path.join(dp, f))
    return results

def add_import_UTC_if_needed(text: str) -> str:
    """Se usamos datetime.now(UTC) e não há UTC importado, adiciona 'from datetime import UTC'."""
    if "datetime.now(UTC)" not in text:
        return text

    # Já importou o UTC?
    if re.search(r"from\s+datetime\s+import\s+([^#\n]*\bUTC\b)", text):
        return text

    # Tente anexar , UTC em 'from datetime import datetime ...'
    def _add_utc_in_from(m: re.Match) -> str:
        items = m.group(1)
        if "UTC" in items:
            return m.group(0)
        # preserva espaços
        items2 = items.rstrip() + ", UTC"
        return f"from datetime import {items2}"

    new_text, n = re.subn(r"(?m)^from\s+datetime\s+import\s+([^\n#]+)$", _add_utc_in_from, text)
    if n > 0:
        return new_text

    # Se não tinha nenhum 'from datetime import ...', só injeta uma linha de import no topo (após shebang/encoding/docstring).
    lines = text.splitlines()
    insert_at = 0
    # pula shebang/encoding e docstring inicial
    while insert_at < len(lines) and (
        lines[insert_at].startswith("#!") or
        "coding" in lines[insert_at] or
        lines[insert_at].strip() == "" or
        lines[insert_at].lstrip().startswith("#")
    ):
        insert_at += 1
    lines.insert(insert_at, "from datetime import UTC")
    return "\n".join(lines)

# -------- patches --------
def patch_httpx(text: str) -> Tuple[str, int]:
    """
    Troca .<method>(..., data=<literal bytes/str> ...) por content=...
    Não mexe em json=, files=, data=dict/variável.
    """
    pattern = re.compile(
        r"""(\.(?:get|post|put|patch|delete)\s*\(
             [^)]*?)                # grupo 1: tudo até data=
             \bdata\s*=\s*
             (b?['"][\s\S]*?['"])   # grupo 2: literal bytes/str
        """,
        re.IGNORECASE | re.VERBOSE | re.DOTALL,
    )

    changed = 0
    while True:
        new_text, n = pattern.subn(r"\1content=\2", text, count=1)
        changed += n
        if n == 0:
            break
        text = new_text
    return text, changed

def patch_utcnow(text: str) -> Tuple[str, int]:
    """
    - datetime.utcnow() -> datetime.now(UTC)
    - datetime.datetime.utcnow() -> datetime.datetime.now(datetime.UTC)
    + garante import UTC quando necessário
    """
    count = 0

    # Caso 'from datetime import datetime' ou equivalente: datetime.utcnow()
    text, n1 = re.subn(r"\bdatetime\.utcnow\(\)", "datetime.now(UTC)", text)
    count += n1

    # Caso 'import datetime': datetime.datetime.utcnow()
    text, n2 = re.subn(r"\bdatetime\.datetime\.utcnow\(\)", "datetime.datetime.now(datetime.UTC)", text)
    count += n2

    if n1 > 0:
        text = add_import_UTC_if_needed(text)

    return text, count

def process_file(path: str) -> Tuple[int, int]:
    with open(path, "r", encoding="utf-8") as f:
        original = f.read()

    patched = original
    total_changes = 0

    # datetime patches
    patched, c_dt = patch_utcnow(patched)
    total_changes += c_dt

    # httpx patches
    patched, c_httpx = patch_httpx(patched)
    total_changes += c_httpx

    if total_changes > 0 and patched != original:
        # backup
        with open(path + BACKUP_SUFFIX, "w", encoding="utf-8") as f:
            f.write(original)
        with open(path, "w", encoding="utf-8") as f:
            f.write(patched)

    return total_changes, (1 if total_changes > 0 else 0)

def main():
    files = iter_py_files()
    changed_files = 0
    total_edits = 0
    for p in files:
        edits, touched = process_file(p)
        total_edits += edits
        changed_files += touched
        if edits:
            print(f"[OK] {p}: {edits} mudanças")
    if changed_files == 0:
        print("Nenhuma alteração necessária.")
    else:
        print(f"\nResumo: {total_edits} mudanças em {changed_files} arquivo(s).")
        print(f"Backups criados com sufixo {BACKUP_SUFFIX}")

if __name__ == "__main__":
    main()
