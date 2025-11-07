# src/ui/streamlit_app.py
from __future__ import annotations
from datetime import datetime
from typing import Dict, Any

LABEL_TO_ID: Dict[str, str] = {
    "🏠 Dashboard": "dashboard",
    "📈 Trading": "trading",
    "💼 Posições": "positions",
    "⚙️ Estratégias": "strategies",
    "📊 Analytics": "analytics",
    "🔧 Configurações": "settings",
}
ID_TO_TITLE: Dict[str, str] = {
    "dashboard":  "🏠 Dashboard Principal",
    "trading":    "📈 Trading em Tempo Real",
    "positions":  "💼 Minhas Posições",
    "strategies": "⚙️ Estratégias",
    "analytics":  "📊 Analytics e Métricas",
    "settings":   "🔧 Configurações",
}
ALL_PAGE_IDS = ["dashboard", "trading", "positions", "strategies", "analytics", "settings"]

def _normalize_page(value: str) -> str:
    if value in LABEL_TO_ID:
        return LABEL_TO_ID[value]
    if value in ID_TO_TITLE:
        return value
    return "dashboard"

class StreamlitApp:
    def __init__(self) -> None:
        self.session_state: Dict[str, Any] = {
            "user_id": None,
            "username": None,
            "is_authenticated": False,
            "page": "dashboard",
        }
        self.current_page_id: str = "dashboard"

    async def initialize(self) -> Dict[str, Any]:
        return {"status": "initialized", "pages": len(ALL_PAGE_IDS)}

    async def authenticate_user(self, username: str, password: str) -> Dict[str, Any]:
        self.session_state["user_id"] = 1
        self.session_state["username"] = username or "user"
        self.session_state["is_authenticated"] = True
        return {"ok": True, "user_id": 1}

    async def get_session_state(self) -> Dict[str, Any]:
        return dict(self.session_state)

    async def render_page(self, page_name: str) -> Dict[str, Any]:
        page_id = _normalize_page(str(page_name))
        self.current_page_id = page_id
        self.session_state["page"] = page_id
        return {
            "page": page_id,
            "title": ID_TO_TITLE.get(page_id, ""),
            "timestamp": datetime.now().isoformat(),
        }

    async def handle_widget_interaction(self, widget_id: str, value: Any, event: str | None = None) -> Dict[str, Any]:
        if widget_id == "page_selector" and event == "change":
            new_id = _normalize_page(str(value))
            self.current_page_id = new_id
            self.session_state["page"] = new_id
            return {"page_changed": True, "page": new_id}
        return {"ok": True}
