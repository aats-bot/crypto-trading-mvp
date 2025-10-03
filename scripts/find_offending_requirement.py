#!/usr/bin/env python3
"""
find_offending_requirement.py

Testa cada dependência de um requirements*.txt em isolamento (venv temporário),
para descobrir qual pacote falha na instalação (ex.: build isolation com Cython alfa).

Uso:
  python scripts/find_offending_requirement.py --file requirements-test.txt
  python scripts/find_offending_requirement.py --file requirements.txt --continue-all
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

COMMENT_RE = re.compile(r"^\s*(#|;|$)")

def run(cmd, env=None, cwd=None):
    print(f"  $ {' '.join(cmd)}")
    return subprocess.run(cmd, env=env, cwd=cwd, check=False)

def create_venv(base_dir: Path):
    venv_dir = base_dir / ".venv_tmp"
    if venv_dir.exists():
        shutil.rmtree(venv_dir, ignore_errors=True)
    venv_dir.mkdir(parents=True, exist_ok=True)
    subprocess.check_call([sys.executable, "-m", "venv", str(venv_dir)])
    # caminhos executáveis
    if os.name == "nt":
        py = venv_dir / "Scripts" / "python.exe"
        pip = venv_dir / "Scripts" / "pip.exe"
    else:
        py = venv_dir / "bin" / "python"
        pip = venv_dir / "bin" / "pip"
    return venv_dir, str(py), str(pip)

def read_requirements(path: Path):
    lines = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        s = raw.strip()
        if not s or COMMENT_RE.match(s):
            continue
        lines.append(s)
    return lines

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", "-f", default="requirements-test.txt", help="Arquivo de requirements a testar (padrão: requirements-test.txt)")
    ap.add_argument("--continue-all", action="store_true", help="Em vez de parar no primeiro erro, testa todas as linhas e lista as que falham")
    args = ap.parse_args()

    req_path = Path(args.file)
    if not req_path.exists():
        print(f"Arquivo não encontrado: {req_path}")
        sys.exit(2)

    base_dir = Path.cwd()
    venv_dir, py, pip = create_venv(base_dir)
    print(f"[INFO] Venv criado em: {venv_dir}")

    # upgrade toolchain + pré-instalações úteis (ajuda em builds)
    print("[INFO] Atualizando pip/setuptools/wheel…")
    run([py, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"])

    # Dica: pré-instalar Cython e numpy pode evitar build isolation quebrado
    print("[INFO] Pré-instalando Cython e numpy (opcional)…")
    run([pip, "install", "Cython==3.0.12", "numpy"])

    reqs = read_requirements(req_path)
    print(f"[INFO] {len(reqs)} entradas encontradas em {req_path}")

    offenders = []
    for i, req in enumerate(reqs, 1):
        print(f"\n=== [{i}/{len(reqs)}] Testando: {req}")
        # tentar instalar só este pacote (isoladamente dentro do venv)
        code = run([pip, "install", req]).returncode
        if code != 0:
            print(f">>> FALHA: {req}")
            offenders.append(req)
            if not args.continue_all:
                print("\n[RESULTADO] Primeiro pacote problemático encontrado.")
                break
        else:
            print(f"[OK] {req}")

    if offenders:
        print("\n================ RESULTADO ================")
        for off in offenders:
            print(f"- Pacote com falha: {off}")
        print("===========================================")
        print("\nSugestões:")
        print("  1) Atualize esse pacote para uma versão que tenha wheel para Python 3.12 ou que não fixe Cython alfa.")
        print("  2) Se precisar contornar no CI, pré-instale Cython==3.0.12 e use --no-build-isolation.")
        sys.exit(1)
    else:
        print("\n[RESULTADO] Nenhuma falha ao instalar individualmente. O conflito pode estar em combinações entre pacotes.")
        sys.exit(0)

if __name__ == "__main__":
    main()
