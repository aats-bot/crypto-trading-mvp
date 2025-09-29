# 🔐 Componentes de Autenticação - Dashboard
"""
Componentes reutilizáveis para autenticação no dashboard
Localização: /src/dashboard/components/auth_components.py
"""
import streamlit as st
import requests
from typing import Dict, Any, Optional, Tuple
import re


def login_form(api_url: str = "http://localhost:8000") -> Optional[Dict[str, Any]]:
    """
    Componente de formulário de login
    
    Args:
        api_url: URL base da API
        
    Returns:
        Dict com dados de login se bem-sucedido, None caso contrário
    """
    st.subheader("🔑 Login")
    
    with st.form("login_form"):
        email = st.text_input(
            "Email",
            placeholder="seu@email.com",
            help="Digite seu email cadastrado"
        )
        
        password = st.text_input(
            "Senha",
            type="password",
            placeholder="••••••••",
            help="Digite sua senha"
        )
        
        remember_me = st.checkbox("Lembrar de mim")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            submit_button = st.form_submit_button(
                "Entrar",
                type="primary",
                use_container_width=True
            )
        
        with col2:
            forgot_password = st.form_submit_button(
                "Esqueci a senha",
                use_container_width=True
            )
    
    if submit_button:
        if not email or not password:
            st.error("❌ Por favor, preencha todos os campos")
            return None
        
        if not _validate_email(email):
            st.error("❌ Email inválido")
            return None
        
        # Fazer login via API
        try:
            with st.spinner("Fazendo login..."):
                response = requests.post(
                    f"{api_url}/api/auth/login",
                    json={"email": email, "password": password},
                    timeout=10
                )
            
            if response.status_code == 200:
                login_data = response.json()
                
                # Salvar dados de sessão
                st.session_state.authenticated = True
                st.session_state.access_token = login_data["access_token"]
                st.session_state.client_id = login_data["client_id"]
                st.session_state.email = login_data["email"]
                
                if remember_me:
                    st.session_state.remember_login = True
                
                st.success("✅ Login realizado com sucesso!")
                st.rerun()
                
                return login_data
            
            elif response.status_code == 401:
                st.error("❌ Email ou senha incorretos")
            else:
                st.error(f"❌ Erro no login: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Erro de conexão: {str(e)}")
        except Exception as e:
            st.error(f"❌ Erro inesperado: {str(e)}")
    
    if forgot_password:
        st.info("🔄 Funcionalidade de recuperação de senha em desenvolvimento")
    
    return None


def register_form(api_url: str = "http://localhost:8000") -> Optional[Dict[str, Any]]:
    """
    Componente de formulário de registro
    
    Args:
        api_url: URL base da API
        
    Returns:
        Dict com dados de registro se bem-sucedido, None caso contrário
    """
    st.subheader("📝 Criar Conta")
    
    with st.form("register_form"):
        email = st.text_input(
            "Email",
            placeholder="seu@email.com",
            help="Digite um email válido"
        )
        
        password = st.text_input(
            "Senha",
            type="password",
            placeholder="••••••••",
            help="Mínimo 8 caracteres"
        )
        
        confirm_password = st.text_input(
            "Confirmar Senha",
            type="password",
            placeholder="••••••••",
            help="Digite a senha novamente"
        )
        
        st.subheader("🔑 Configuração da API Bybit")
        st.info("ℹ️ Você pode configurar suas chaves API depois do registro")
        
        bybit_api_key = st.text_input(
            "API Key da Bybit (opcional)",
            placeholder="Sua API Key da Bybit",
            help="Deixe em branco para configurar depois"
        )
        
        bybit_api_secret = st.text_input(
            "API Secret da Bybit (opcional)",
            type="password",
            placeholder="Seu API Secret da Bybit",
            help="Deixe em branco para configurar depois"
        )
        
        # Termos e condições
        agree_terms = st.checkbox(
            "Concordo com os termos de uso e política de privacidade",
            help="Você deve concordar para criar uma conta"
        )
        
        submit_button = st.form_submit_button(
            "Criar Conta",
            type="primary",
            use_container_width=True
        )
    
    if submit_button:
        # Validações
        validation_errors = []
        
        if not email:
            validation_errors.append("Email é obrigatório")
        elif not _validate_email(email):
            validation_errors.append("Email inválido")
        
        if not password:
            validation_errors.append("Senha é obrigatória")
        elif len(password) < 8:
            validation_errors.append("Senha deve ter pelo menos 8 caracteres")
        
        if password != confirm_password:
            validation_errors.append("Senhas não coincidem")
        
        if not agree_terms:
            validation_errors.append("Você deve concordar com os termos")
        
        if validation_errors:
            for error in validation_errors:
                st.error(f"❌ {error}")
            return None
        
        # Fazer registro via API
        try:
            register_data = {
                "email": email,
                "password": password,
            }
            
            # Adicionar chaves API se fornecidas
            if bybit_api_key and bybit_api_secret:
                register_data["bybit_api_key"] = bybit_api_key
                register_data["bybit_api_secret"] = bybit_api_secret
            
            with st.spinner("Criando conta..."):
                response = requests.post(
                    f"{api_url}/api/auth/register",
                    json=register_data,
                    timeout=10
                )
            
            if response.status_code == 201:
                result = response.json()
                st.success("✅ Conta criada com sucesso!")
                st.info("🔑 Agora você pode fazer login com suas credenciais")
                return result
            
            elif response.status_code == 400:
                error_data = response.json()
                st.error(f"❌ {error_data.get('detail', 'Erro no registro')}")
            else:
                st.error(f"❌ Erro no registro: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Erro de conexão: {str(e)}")
        except Exception as e:
            st.error(f"❌ Erro inesperado: {str(e)}")
    
    return None


def logout_button(api_url: str = "http://localhost:8000") -> bool:
    """
    Componente de botão de logout
    
    Args:
        api_url: URL base da API
        
    Returns:
        True se logout foi realizado, False caso contrário
    """
    if st.button("🚪 Sair", type="secondary", use_container_width=True):
        try:
            # Fazer logout via API se token disponível
            if hasattr(st.session_state, 'access_token'):
                headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
                requests.post(
                    f"{api_url}/api/auth/logout",
                    headers=headers,
                    timeout=5
                )
        except:
            pass  # Ignorar erros de logout da API
        
        # Limpar sessão local
        _clear_session_data()
        st.success("✅ Logout realizado com sucesso!")
        st.rerun()
        return True
    
    return False


def auth_status_indicator() -> None:
    """
    Componente indicador de status de autenticação
    """
    if _is_authenticated():
        email = st.session_state.get('email', 'Usuário')
        
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.success(f"✅ Conectado como: **{email}**")
            
            with col2:
                logout_button()
    else:
        st.warning("⚠️ Você não está autenticado")


def password_strength_indicator(password: str) -> Tuple[int, str, str]:
    """
    Indica a força da senha
    
    Args:
        password: Senha para avaliar
        
    Returns:
        Tuple com (score, color, message)
    """
    score = 0
    messages = []
    
    if len(password) >= 8:
        score += 1
    else:
        messages.append("Pelo menos 8 caracteres")
    
    if re.search(r'[A-Z]', password):
        score += 1
    else:
        messages.append("Pelo menos uma letra maiúscula")
    
    if re.search(r'[a-z]', password):
        score += 1
    else:
        messages.append("Pelo menos uma letra minúscula")
    
    if re.search(r'[0-9]', password):
        score += 1
    else:
        messages.append("Pelo menos um número")
    
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 1
    else:
        messages.append("Pelo menos um caractere especial")
    
    if score <= 2:
        return score, "🔴", "Fraca: " + ", ".join(messages[:2])
    elif score <= 3:
        return score, "🟡", "Média: " + ", ".join(messages[:1])
    elif score <= 4:
        return score, "🟠", "Boa: " + ", ".join(messages[:1]) if messages else "Boa"
    else:
        return score, "🟢", "Muito forte"


def two_factor_auth_setup() -> None:
    """
    Componente para configuração de autenticação de dois fatores
    (Placeholder para implementação futura)
    """
    st.subheader("🔐 Autenticação de Dois Fatores")
    st.info("🚧 Funcionalidade em desenvolvimento")
    
    enable_2fa = st.checkbox("Habilitar 2FA (em breve)")
    
    if enable_2fa:
        st.warning("⚠️ Esta funcionalidade será implementada em versões futuras")


def session_timeout_warning() -> None:
    """
    Componente de aviso de timeout de sessão
    """
    import time
    
    if not _is_authenticated():
        return
    
    # Verificar se há timestamp de login
    login_time = st.session_state.get('login_timestamp', time.time())
    current_time = time.time()
    session_duration = current_time - login_time
    
    # 8 horas = 28800 segundos
    max_session_duration = 28800
    remaining_time = max_session_duration - session_duration
    
    if remaining_time <= 1800:  # 30 minutos restantes
        minutes_left = int(remaining_time / 60)
        st.warning(f"⏰ Sua sessão expira em {minutes_left} minutos")
    
    if remaining_time <= 0:
        st.error("⏰ Sua sessão expirou. Faça login novamente.")
        _clear_session_data()
        st.rerun()


# Funções auxiliares privadas
def _validate_email(email: str) -> bool:
    """Valida formato do email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def _is_authenticated() -> bool:
    """Verifica se usuário está autenticado"""
    return (
        hasattr(st.session_state, 'authenticated') and
        st.session_state.authenticated and
        hasattr(st.session_state, 'access_token') and
        st.session_state.access_token
    )


def _clear_session_data() -> None:
    """Limpa dados de sessão"""
    session_keys = [
        'authenticated', 'access_token', 'client_id', 'email',
        'remember_login', 'login_timestamp'
    ]
    
    for key in session_keys:
        if key in st.session_state:
            del st.session_state[key]


def _get_auth_headers() -> Dict[str, str]:
    """Retorna headers de autenticação"""
    if _is_authenticated():
        return {"Authorization": f"Bearer {st.session_state.access_token}"}
    return {}


# Exportar funções principais
__all__ = [
    "login_form",
    "register_form",
    "logout_button",
    "auth_status_indicator",
    "password_strength_indicator",
    "two_factor_auth_setup",
    "session_timeout_warning",
]

