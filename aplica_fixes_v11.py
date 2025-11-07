from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
E2E = ROOT / "tests" / "e2e" / "test_streamlit_interface.py"
INTEGRATION = ROOT / "tests" / "integration" / "test_api_integration.py"

STREAMLITAPP_IMPL = '''
class StreamlitApp:
    def __init__(self):
        # Estado simples para o mock usado nos testes E2E
        self.session = {}
        self._authenticated = False
        self.state = {}
        self.current_page = 'login'

    async def initialize(self):
        import asyncio
        await asyncio.sleep(0.01)
        return {'status': 'initialized'}

    async def authenticate_user(self, username: str, password: str):
        import asyncio, time
        await asyncio.sleep(0.01)
        self._authenticated = True
        self.session['authenticated'] = True
        self.session['user'] = username
        self.session['user_id'] = self.session.get('user_id') or f"uid_{int(time.time())}"
        return {'status': 'authenticated', 'user_id': self.session['user_id']}

    def get_session_state(self):
        return {
            'authenticated': bool(self.session.get('authenticated', False)),
            'user_id': self.session.get('user_id')
        }

    def logout_user(self):
        self._authenticated = False
        self.session['authenticated'] = False
        return {'success': True}

    async def shutdown(self):
        import asyncio
        await asyncio.sleep(0.01)
        return {'status': 'shutdown'}

    async def render_page(self, title: str):
        # Sem login: sempre redireciona para login (inclusive no Dashboard)
        if not self._authenticated and title != "🔐 Login":
            self.current_page = 'login'
            return {
                'page': 'login',
                'components': {
                    'username_input': True,
                    'password_input': True,
                    'login_btn': True
                }
            }

        # Página de Trading
        if title == "📈 Trading":
            self.current_page = 'trading'
            return {
                'page': 'trading',
                'layout': ['order_form', 'market_info']
            }

        # Dashboard (outras páginas) após login
        self.current_page = 'dashboard' if self._authenticated else 'login'
        return {
            'page': self.current_page,
            'components': {
                'username_input': True,
                'password_input': True,
                'login_btn': True
            } if self.current_page == 'login' else {}
        }

    async def handle_widget_interaction(self, widget_id: str, value, event_type: str):
        import asyncio, time
        await asyncio.sleep(0.01)

        # Campos do formulário de login
        if widget_id in ('username', 'password'):
            self.state[widget_id] = value
            return {'status': 'updated'}

        # Botão de login
        if widget_id == 'login_btn' and event_type == 'click':
            username = self.state.get('username')
            password = self.state.get('password')
            if username and password:
                self._authenticated = True
                self.session['authenticated'] = True
                self.session['user'] = username
                self.session['user_id'] = self.session.get('user_id') or f"uid_{int(time.time())}"
                return {'success': True, 'user': username}
            return {'success': False, 'error': 'missing credentials'}

        # Campos do formulário de ordem
        if widget_id in ('order_symbol', 'order_side', 'order_quantity'):
            self.state[widget_id] = value
            return {'status': 'updated'}

        # Execução da ordem
        if widget_id == 'place_order_btn' and event_type == 'click':
            order = {
                'symbol': self.state.get('order_symbol', 'BTCUSDT'),
                'side': self.state.get('order_side', 'buy'),
                'quantity': self.state.get('order_quantity', 0.1),
                'timestamp': int(time.time())
            }
            trade_result = {
                'status': 'filled',
                'filled_qty': order['quantity'],
                'avg_price': 50000
            }
            return {
                'success': True,
                'order': order,
                'trade_result': trade_result,
                'message': 'Ordem executada com sucesso'
            }

        return {'status': 'ignored'}
'''.lstrip("\n")


def backup(path: Path, suffix: str):
    b = Path(str(path) + suffix)
    if not b.exists() and path.exists():
        b.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")


def replace_streamlitapp(text: str) -> str:
    # Encontra a classe top-level "class StreamlitApp(...):"
    cls_pat = re.compile(r'(?m)^class\s+StreamlitApp\b[^\n]*:\s*$')
    m = cls_pat.search(text)
    if not m:
        return text  # não achou a classe; não altera

    # Delimita o fim pelo próximo "class X:" top-level ou fim do arquivo
    next_cls = re.compile(r'(?m)^class\s+\w+\b[^\n]*:\s*$')
    n = next_cls.search(text, m.end())
    end = n.start() if n else len(text)

    # Monta novo conteúdo
    prefix = text[:m.start()]
    suffix = text[end:]
    return prefix + STREAMLITAPP_IMPL + suffix


def patch_close_position_body(text: str) -> str:
    """
    Substitui apenas o corpo de async def close_position(self, position_id: str)
    para garantir que retorne também 'exit_price'.
    """
    # Ache a assinatura do método
    sig_pat = re.compile(r'(?m)^(?P<indent>\s*)async\s+def\s+close_position\s*\(\s*self\s*,\s*position_id\s*:\s*str\s*\)\s*:\s*$')
    m = sig_pat.search(text)
    if not m:
        return text  # não achou; evita mexer

    indent = m.group('indent')
    # Encontrar o fim do bloco pelo próximo def/async def/class com indent <= atual
    lines = text.splitlines(keepends=True)
    start_idx = None
    for i, line in enumerate(lines):
        if m.start() >= sum(len(l) for l in lines[:i+1]):
            continue
        # Depois da assinatura, então começamos a contar
        start_idx = i
        break

    # Recalcula via índice de linha:
    start_line = text[:m.start()].count("\n") + 1  # linha da assinatura (0-based +1)
    i = start_line + 1  # primeira linha após a assinatura
    def is_block_end(line: str) -> bool:
        # fim quando encontramos uma nova def/async def/class com indent <= da assinatura
        if not line.strip():
            return False
        if len(line) - len(line.lstrip()) <= len(indent):
            if re.match(r'\s*(def|async\s+def|class)\b', line):
                return True
        return False

    # percorre até o fim do bloco
    total_lines = len(lines)
    while i < total_lines and not is_block_end(lines[i]):
        i += 1

    # Novo corpo do método
    new_body = (
        f"{indent}    from datetime import datetime\n"
        f"{indent}    # Fechar posição e devolver closed_at + exit_price\n"
        f"{indent}    if position_id not in self.active_positions:\n"
        f"{indent}        raise ValueError(f\"Posição '{{position_id}}' não encontrada\")\n"
        f"{indent}    pos = self.active_positions.pop(position_id)\n"
        f"{indent}    pos['status'] = 'closed'\n"
        f"{indent}    exit_price = pos.get('entry_price', 50000)\n"
        f"{indent}    return {{\n"
        f"{indent}        'status': 'closed',\n"
        f"{indent}        'position_id': position_id,\n"
        f"{indent}        'position': pos,\n"
        f"{indent}        'closed_at': datetime.now().isoformat(),\n"
        f"{indent}        'exit_price': exit_price\n"
        f"{indent}    }}\n"
    )

    head = "".join(lines[:start_line+1])  # até a linha da assinatura (inclui \n)
    tail = "".join(lines[i:])             # do fim do bloco atual em diante
    return head + new_body + tail


def main():
    # 1) E2E: substitui StreamlitApp
    if E2E.exists():
        backup(E2E, ".bak_v11")
        src = E2E.read_text(encoding="utf-8")
        patched = replace_streamlitapp(src)
        if patched != src:
            E2E.write_text(patched, encoding="utf-8")
            print("OK: StreamlitApp substituída (v11).")
        else:
            print("Aviso: não encontrei StreamlitApp para substituir (E2E).")

    # 2) Integration: ajusta close_position para incluir exit_price
    if INTEGRATION.exists():
        backup(INTEGRATION, ".bak_v11")
        src = INTEGRATION.read_text(encoding="utf-8")
        patched = patch_close_position_body(src)
        if patched != src:
            INTEGRATION.write_text(patched, encoding="utf-8")
            print("OK: close_position ajustado (exit_price).")
        else:
            print("Aviso: não encontrei close_position para ajustar.")

    print("\\nPronto. Agora rode:")
    print("export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1")
    print('pytest -k "api or trading or clients or auth" -q -c pytest.local.ini')


if __name__ == "__main__":
    main()
