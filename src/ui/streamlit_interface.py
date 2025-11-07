# src/ui/streamlit_interface.py
from __future__ import annotations
from .streamlit_app import StreamlitApp as _Impl

class StreamlitApp(_Impl):
    async def initialize(self):
        res = await super().initialize()
        # Blindagem: garante a chave 'pages' mesmo que algum wrapper antigo sobrescreva
        if "pages" not in res:
            res = dict(res)
            res["pages"] = 6
        return res
