# -*- coding: utf-8 -*-
"""
POS FACILE - Auth Manager (Supabase Auth)
Gestisce login, registrazione e sessioni utente
Fix: Rimossa chiave statica per evitare crash DuplicateElementKey
"""

import streamlit as st

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False


def get_supabase_client() -> Client:
    """Restituisce il client Supabase"""
    if not SUPABASE_AVAILABLE:
        return None
    
    try:
        url = st.secrets.get("SUPABASE_URL", "")
        key = st.secrets.get("SUPABASE_ANON_KEY", "")
        
        if url and key:
            return create_client(url, key)
    except Exception as e:
        print(f"Errore connessione Supabase: {e}")
    
    return None


def init_auth_state():
    """Inizializza lo stato di autenticazione"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None


def register_user(email: str, password: str) -> tuple:
    """Registra un nuovo utente."""
    client = get_supabase_client()
    if not client:
        return False, "Servizio non disponibile"
    
    try:
        response = client.auth.sign_up({
            "email": email,
            "password": password
        })
        
        if response.user:
            return True, "Registrazione completata! Controlla la tua email."
        else:
            return False, "Errore durante la registrazione"
            
    except Exception as e:
        error_msg = str(e)
        if "User already registered" in error_msg:
            return False, "Email già registrata. Prova ad accedere."
        elif "Password should be at least" in error_msg:
            return False, "La password deve essere di almeno 6 caratteri"
        else:
            return False, f"Errore: {error_msg}"


def login_user(email: str, password: str) -> tuple:
    """Effettua il login."""
    client = get_supabase_client()
    if not client:
        return False, "Servizio non disponibile"
    
    try:
        response = client.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if response.user:
            st.session_state.authenticated = True
            st.session_state.user = response.user
            st.session_state.user_id = response.user.id
            st.session_state.user_email = response.user.email
            return True, "Login effettuato con successo!"
        else:
            return False, "Credenziali non valide"
            
    except Exception as e:
        error_msg = str(e)
        if "Invalid login credentials" in error_msg:
            return False, "Email o password non corretti"
        elif "Email not confirmed" in error_msg:
            return False, "Email non confermata."
        else:
            return False, f"Errore: {error_msg}"


def logout_user():
    """Effettua il logout"""
    client = get_supabase_client()
    if client:
        try:
            client.auth.sign_out()
        except:
            pass
    
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.user_id = None
    st.session_state.user_email = None
    
    # Reset altri stati dell'app
    keys_to_clear = ['ditta', 'cantiere', 'lavoratori', 'attrezzature', 'sostanze', 'step']
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]


def reset_password(email: str) -> tuple:
    """Invia email per reset password."""
    client = get_supabase_client()
    if not client:
        return False, "Servizio non disponibile"
    
    try:
        client.auth.reset_password_email(email)
        return True, "Email inviata! Controlla la posta."
    except Exception as e:
        return False, f"Errore: {str(e)}"


def is_authenticated() -> bool:
    return st.session_state.get('authenticated', False) and st.session_state.get('user_id') is not None


def get_current_user_id() -> str:
    return st.session_state.get('user_id')


def get_current_user_email() -> str:
    return st.session_state.get('user_email')


def render_auth_page(default_mode='login'):
    st.markdown("""<style>.auth-container {max-width: 400px; margin: 0 auto; padding: 2rem;} .auth-header {text-align: center; margin-bottom: 2rem;} .auth-header h1 {color: #FF6600; font-size: 2.5rem;}</style>""", unsafe_allow_html=True)
    
    st.markdown("""<div class="auth-header"><h1>🏗️ POS FACILE</h1><p style="color: #666; font-size: 18px;">Generatore POS per professionisti della sicurezza</p></div>""", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🔐 Accedi", "📝 Registrati", "🔑 Recupero"])
    
    with tab1: render_login_form()
    with tab2: render_register_form()
    with tab3: render_reset_password_form()


def render_login_form():
    with st.form("login_form"):
        st.markdown("### Accedi")
        email = st.text_input("📧 Email", placeholder="email@esempio.com")
        password = st.text_input("🔒 Password", type="password")
        if st.form_submit_button("Accedi →", use_container_width=True, type="primary"):
            if email and password:
                with st.spinner("Accesso..."):
                    success, msg = login_user(email, password)
                    if success: st.success(msg); st.rerun()
                    else: st.error(msg)
            else: st.warning("Inserisci dati")


def render_register_form():
    with st.form("register_form"):
        st.markdown("### Registrati")
        email = st.text_input("📧 Email *")
        password = st.text_input("🔒 Password *", type="password", placeholder="Min 6 caratteri")
        confirm = st.text_input("🔒 Conferma Password *", type="password")
        if st.form_submit_button("Registrati →", use_container_width=True, type="primary"):
            if password != confirm: st.error("Le password non coincidono")
            elif len(password) < 6: st.error("Password troppo corta")
            else:
                with st.spinner("Registrazione..."):
                    success, msg = register_user(email, password)
                    if success: st.success(msg)
                    else: st.error(msg)


def render_reset_password_form():
    with st.form("reset_form"):
        st.markdown("### Recupero Password")
        email = st.text_input("📧 Email")
        if st.form_submit_button("Invia Link", use_container_width=True):
            if email:
                with st.spinner("Invio..."):
                    success, msg = reset_password(email)
                    if success: st.success(msg)
                    else: st.error(msg)


def render_user_menu():
    """Renderizza il menu utente nella sidebar"""
    if is_authenticated():
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 👤 Account")
        st.sidebar.write(f"**{get_current_user_email()}**")
        
        # RIMOSSA LA CHIAVE ESPLICITA PER EVITARE CRASH
        if st.sidebar.button("🚪 Logout", use_container_width=True):
            logout_user()
            st.rerun()
