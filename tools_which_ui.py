# -*- coding: utf-8 -*-
import asyncio
import importlib
import inspect

def check(modpath: str):
    try:
        m = importlib.import_module(modpath)
        print(f"[OK] import {modpath} -> {getattr(m, '__file__', '?')}")
        App = getattr(m, "StreamlitApp", None)
        if App is None:
            print("  ! StreamlitApp não encontrado nesse módulo")
            return
        print("  class file:", inspect.getsourcefile(App))

        app = App()

        # initialize
        init = asyncio.run(app.initialize())
        print("  initialize() ->", init)

        # authenticate
        auth = asyncio.run(app.authenticate_user("user", "pass"))
        print("  authenticate_user() ->", auth)

        # session_state exists?
        print("  has session_state attr:", hasattr(app, "session_state"))
        if hasattr(app, "session_state"):
            print("  session_state:", app.session_state)

        # render pages usando rótulos SEM emoji (mapeados internamente)
        dash = asyncio.run(app.render_page("Dashboard"))
        print("  render 'Dashboard' ->", dash)

        # navegar para outra página
        nav = asyncio.run(app.handle_widget_interaction("page_selector", "Analytics", "change"))
        print("  nav to 'Analytics' ->", nav)

        ana = asyncio.run(app.render_page("Analytics"))
        print("  render 'Analytics' ->", ana)

    except Exception as e:
        print(f"[FAIL] import {modpath} -> {e}")

for path in [
    "src.ui.streamlit_app",
    "src.ui.streamlit_interface",
    "src.ui",
]:
    check(path)
