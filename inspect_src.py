import argparse
import sys
from pathlib import Path
import re
from typing import List, Tuple

# -------- util --------
def read_text_safe(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        return f"<<ERRO AO LER {p.name}: {e}>>"

def is_pkg(d: Path) -> bool:
    return (d / "__init__.py").exists()

def list_tree(base: Path) -> str:
    lines = []
    for p in sorted(base.rglob("*")):
        rel = p.relative_to(base)
        depth = len(rel.parts) - 1
        indent = "  " * depth
        if p.is_dir():
            tag = "[pkg]" if is_pkg(p) else "[dir]"
            lines.append(f"{indent}{rel.name}/ {tag}")
        elif p.suffix == ".py":
            lines.append(f"{indent}{rel.name}")
    return "\n".join(lines)

def missing_init_pkgs(base: Path) -> List[Path]:
    dirs = [d for d in base.rglob("*") if d.is_dir()]
    return [d for d in dirs if not (d / "__init__.py").exists()]

def find_regex(txt: str, pat: str) -> bool:
    return re.search(pat, txt, re.MULTILINE | re.DOTALL) is not None

def check_contains(txt: str, needles: List[str]) -> List[str]:
    missing = []
    for n in needles:
        if not re.search(rf"\b{re.escape(n)}\b", txt):
            missing.append(n)
    return missing

def section(title: str) -> str:
    return f"\n{'='*80}\n{title}\n{'='*80}\n"

# -------- checks --------
def check_database(db_path: Path) -> Tuple[bool, List[str]]:
    issues = []
    ok = True
    if not db_path.exists():
        return False, [f"{db_path} não existe."]
    txt = read_text_safe(db_path)
    if not find_regex(txt, r"from\s+sqlalchemy\.orm\s+import\s+declarative_base"):
        ok = False; issues.append("Falta import: from sqlalchemy.orm import declarative_base")
    if not find_regex(txt, r"\bBase\s*=\s*declarative_base\("):
        ok = False; issues.append("Falta definição: Base = declarative_base()")
    if not find_regex(txt, r"\bdef\s+init_engine\s*\("):
        ok = False; issues.append("Falta função: init_engine(...)")
    if not find_regex(txt, r"\bdef\s+get_session\s*\("):
        ok = False; issues.append("Falta função: get_session()")
    return ok, issues

def check_client_imports(client_path: Path) -> Tuple[bool, List[str]]:
    issues = []
    ok = True
    if not client_path.exists():
        return False, [f"{client_path} não existe."]
    txt = read_text_safe(client_path)
    if not find_regex(txt, r"from\s+\.\s*database\s+import\s+Base"):
        ok = False; issues.append("client.py deveria importar Base: from .database import Base")
    return ok, issues

def check_strategies(strategies_path: Path) -> Tuple[bool, List[str]]:
    issues = []
    ok = True
    if not strategies_path.exists():
        return False, [f"{strategies_path} não existe."]
    txt = read_text_safe(strategies_path)
    need = [
        "MarketData",
        "get_strategy",
        "get_strategy_info",
        "get_available_strategies",
        "SMAStrategy",
        "RSIStrategy",
        "PPPVishvaStrategy",
    ]
    missing = check_contains(txt, need)
    if missing:
        ok = False; issues.append("Ausentes em src/strategies.py: " + ", ".join(missing))
    return ok, issues

def check_indicators(indicators_path: Path) -> Tuple[bool, List[str]]:
    issues = []
    ok = True
    if not indicators_path.exists():
        return False, [f"{indicators_path} não existe."]
    txt = read_text_safe(indicators_path)
    need = [
        "BaseIndicator",
        "EMAIndicator",
        "RSIIndicator",
        "ATRIndicator",
        "UTBotIndicator",
        "EWOIndicator",
        "StochRSIIndicator",
        "HeikinAshiIndicator",
    ]
    missing = check_contains(txt, need)
    if missing:
        ok = False; issues.append("Ausentes em src/indicators.py: " + ", ".join(missing))
    # checks rápidos de métodos comuns
    if not find_regex(txt, r"\bclass\s+BaseIndicator\b") or not find_regex(txt, r"\bdef\s+is_ready\s*\("):
        issues.append("BaseIndicator/is_ready não encontrado (ou nome diferente).")
    return ok, issues

def check_shim_bot_strategies(shim_path: Path) -> Tuple[bool, List[str]]:
    issues = []
    ok = True
    if not shim_path.exists():
        return False, [f"{shim_path} não existe."]
    txt = read_text_safe(shim_path)
    # precisa reexportar MarketData e helpers
    required_exports = ["MarketData", "get_strategy", "get_available_strategies", "get_strategy_info"]
    for name in required_exports:
        if name not in txt:
            ok = False; issues.append(f"{name} não encontrado em {shim_path}")
    if "from src.strategies import" not in txt:
        ok = False; issues.append("Esperado reexport de src.strategies (from src.strategies import ...).")
    return ok, issues

def check_shim_bot_indicators(shim_path: Path) -> Tuple[bool, List[str]]:
    issues = []
    ok = True
    if not shim_path.exists():
        return False, [f"{shim_path} não existe."]
    txt = read_text_safe(shim_path)
    if "from src.indicators import *" not in txt.replace("  ", " "):
        ok = False; issues.append("Esperado: from src.indicators import *")
    return ok, issues

def check_shim_bot_risk(shim_path: Path) -> Tuple[bool, List[str]]:
    issues = []
    ok = True
    if not shim_path.exists():
        return False, [f"{shim_path} não existe."]
    txt = read_text_safe(shim_path)
    if "RiskManager" not in txt:
        ok = False; issues.append("RiskManager não aparece em src/bot/risk.py")
    if "from src.risk_manager import RiskManager" not in txt and "class RiskManager" not in txt:
        ok = False; issues.append("Esperado reexport de src.risk_manager.RiskManager (ou classe fallback).")
    return ok, issues

def check_trading_bot(tb_path: Path) -> Tuple[bool, List[str]]:
    issues = []
    ok = True
    if not tb_path.exists():
        return False, [f"{tb_path} não existe."]
    txt = read_text_safe(tb_path)
    if "from .risk import RiskManager" not in txt:
        ok = False; issues.append("Falta import local: from .risk import RiskManager")
    if "from .strategies import MarketData" not in txt:
        # pode estar junto de outros imports do mesmo módulo
        if not re.search(r"from\s+\.strategies\s+import\s+.*\bMarketData\b", txt):
            ok = False; issues.append("Falta import local: from .strategies import MarketData")
    if not find_regex(txt, r"\bclass\s+TradingBot\b"):
        ok = False; issues.append("Classe TradingBot não encontrada.")
    if not find_regex(txt, r"\bdef\s+_trading_cycle\s*\("):
        ok = False; issues.append("Método _trading_cycle não encontrado em TradingBot.")
    return ok, issues

def main():
    parser = argparse.ArgumentParser(description="Scanner/diagnóstico da pasta src.")
    parser.add_argument("--base", default="src", help="Diretório base (default: src)")
    parser.add_argument("--out", default="src_diagnostics_report.txt", help="Arquivo de saída do relatório")
    args = parser.parse_args()

    base = Path(args.base).resolve()
    if not base.exists():
        print(f"ERRO: pasta base não existe: {base}")
        sys.exit(1)

    report_lines = []
    report_lines.append(section("ÁRVORE DE ARQUIVOS (src)"))
    report_lines.append(str(base))
    report_lines.append(list_tree(base))

    # Pacotes sem __init__.py
    missing = missing_init_pkgs(base)
    report_lines.append(section("PASTAS SEM __init__.py"))
    if missing:
        for d in missing:
            report_lines.append(str(d.relative_to(base)))
    else:
        report_lines.append("OK: todas as pastas possuem __init__.py")

    # Checagens focadas
    report_lines.append(section("CHECAGENS FOCADAS (imports/estruturas)"))

    checks = []

    # database.py
    dbp = base / "models" / "database.py"
    ok, issues = check_database(dbp)
    checks.append(("models/database.py", ok, issues))

    # client.py
    clp = base / "models" / "client.py"
    ok, issues = check_client_imports(clp)
    checks.append(("models/client.py", ok, issues))

    # strategies.py
    stp = base / "strategies.py"
    ok, issues = check_strategies(stp)
    checks.append(("strategies.py", ok, issues))

    # indicators.py
    indp = base / "indicators.py"
    ok, issues = check_indicators(indp)
    checks.append(("indicators.py", ok, issues))

    # shims
    bs_init = base / "bot" / "strategies" / "__init__.py"
    ok, issues = check_shim_bot_strategies(bs_init)
    checks.append(("bot/strategies/__init__.py (shim)", ok, issues))

    bi_py = base / "bot" / "indicators.py"
    ok, issues = check_shim_bot_indicators(bi_py)
    checks.append(("bot/indicators.py (shim)", ok, issues))

    br_py = base / "bot" / "risk.py"
    ok, issues = check_shim_bot_risk(br_py)
    checks.append(("bot/risk.py (shim)", ok, issues))

    # trading_bot.py
    tbp = base / "bot" / "trading_bot.py"
    ok, issues = check_trading_bot(tbp)
    checks.append(("bot/trading_bot.py", ok, issues))

    # risk_manager real
    rmp = base / "risk_manager.py"
    if not rmp.exists():
        checks.append(("risk_manager.py", False, [f"{rmp} não existe (você disse que possui um)."]))
    else:
        txt = read_text_safe(rmp)
        if "class RiskManager" not in txt:
            checks.append(("risk_manager.py", False, ["Classe RiskManager não encontrada."]))
        else:
            checks.append(("risk_manager.py", True, []))

    # imprimir checks
    for name, ok, issues in checks:
        report_lines.append(f"\n[{name}] => {'OK' if ok else 'PROBLEMAS ENCONTRADOS'}")
        if issues:
            for it in issues:
                report_lines.append(f" - {it}")

    # snippets úteis
    report_lines.append(section("SNIPPETS (primeiras linhas de arquivos-chave)"))
    for p in [dbp, clp, stp, indp, bs_init, bi_py, br_py, tbp, rmp]:
        if p.exists():
            content = read_text_safe(p)
            head = "\n".join(content.splitlines()[:60])
            report_lines.append(f"\n--- {p.relative_to(base)} ---\n{head}")

    # salvar
    out = Path(args.out).resolve()
    out.write_text("\n".join(report_lines), encoding="utf-8")

    # resumo no console
    total_bad = sum(1 for _, ok, _ in checks if not ok)
    print("Diagnóstico salvo em:", out)
    print("Resumo:")
    for name, ok, issues in checks:
        print(f" - {name}: {'OK' if ok else 'PROBLEMAS'}")
    if total_bad == 0:
        print("Tudo certo do ponto de vista estrutural/imports. ✅")
    else:
        print(f"Foram encontrados {total_bad} ponto(s) a verificar. Veja o relatório para detalhes.")

if __name__ == "__main__":
    main()
