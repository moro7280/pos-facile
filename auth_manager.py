# -*- coding: utf-8 -*-
"""
POS FACILE - Auth Manager (Supabase Auth)
Gestisce login, registrazione, sessioni utente e callback email.
Fix: Hash Fragment Detection (JS Injection) per Supabase Implicit Flow
"""

import streamlit as st
import streamlit.components.v1 as components
import time

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False


# ==============================================================================
# SUPABASE CLIENT
# ==============================================================================

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


def get_app_url() -> str:
    """Restituisce l'URL base dell'app."""
    try:
        url = st.secrets.get("APP_URL", "")
        if url: return url.rstrip("/")
        return "https://pos-facile.streamlit.app"
    except Exception:
        return "https://pos-facile.streamlit.app"


# ==============================================================================
# AUTH STATE
# ==============================================================================

def init_auth_state():
    """Inizializza lo stato di autenticazione"""
    defaults = {
        'authenticated': False,
        'user': None,
        'user_id': None,
        'user_email': None,
        'show_auth': False,
        'auth_mode': 'register',
        'auth_message': None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


# ==============================================================================
# AUTH FUNCTIONS
# ==============================================================================

def register_user(email: str, password: str) -> tuple:
    client = get_supabase_client()
    if not client: return False, "⚠️ Servizio non disponibile."
    
    try:
        base_url = get_app_url()
        redirect_url = f"{base_url}/?nav=login"
        
        response = client.auth.sign_up({
            "email": email, 
            "password": password,
            "options": {"email_redirect_to": redirect_url}
        })
        
        if response.user:
            return True, "Registrazione completata! Controlla la tua email."
        else:
            return False, "❌ Errore durante la registrazione."
            
    except Exception as e:
        return False, f"❌ Errore: {str(e)}"


def login_user(email: str, password: str) -> tuple:
    client = get_supabase_client()
    if not client: return False, "⚠️ Servizio non disponibile."
    
    try:
        response = client.auth.sign_in_with_password({"email": email, "password": password})
        if response.user:
            _set_local_session(response.user)
            return True, "Login effettuato!"
        return False, "❌ Credenziali non valide."
    except Exception as e:
        return False, f"❌ Errore: {str(e)}"


def logout_user():
    client = get_supabase_client()
    if client:
        try: client.auth.sign_out()
        except: pass
    
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.user_id = None
    
    # Clean POS session
    for key in ['ditta', 'cantiere', 'lavoratori', 'attrezzature', 'sostanze', 'step']:
        if key in st.session_state: del st.session_state[key]


def reset_password(email: str) -> tuple:
    client = get_supabase_client()
    if not client: return False, "⚠️ Servizio non disponibile."
    
    try:
        base_url = get_app_url()
        # Redirect specifico per la pagina di update
        redirect_url = f"{base_url}/?nav=update_password"
        
        client.auth.reset_password_email(email, options={"redirect_to": redirect_url})
        return True, "📧 Email inviata! Controlla la posta."
    except Exception as e:
        return False, f"❌ Errore: {str(e)}"


def update_user_password(new_password: str) -> tuple:
    client = get_supabase_client()
    if not client: return False, "⚠️ Servizio non disponibile."
    
    # Check di sicurezza: siamo davvero loggati?
    if not st.session_state.authenticated:
        return False, "⚠️ Sessione scaduta o non valida. Riprova il link dalla email."

    try:
        response = client.auth.update_user({"password": new_password})
        if response and response.user:
            return True, "Password aggiornata con successo!"
        else:
            return False, "❌ Errore aggiornamento."
    except Exception as e:
        return False, f"❌ Errore: {str(e)}"


def _set_local_session(user):
    st.session_state.authenticated = True
    st.session_state.user = user
    st.session_state.user_id = user.id
    st.session_state.user_email = user.email


# ==============================================================================
# GESTIONE CALLBACK & HASH FIX (CORE FIX)
# ==============================================================================

def handle_auth_callback():
    """Gestisce il login da link email, incluso il fix per l'hash fragment."""
    
    # 1. FIX JAVASCRIPT: Se c'è un hash con access_token, ricarica la pagina spostandolo in query
    # Questo è invisibile all'utente ma fondamentale per Streamlit
    _inject_hash_fixer()
    
    params = st.query_params
    
    # 2. Gestione Errori Supabase
    if params.get("error"):
        st.session_state.show_auth = True
        st.session_state.auth_mode = 'login'
        st.session_state.auth_message = ('error', f"❌ {params.get('error_description')}")
        _clear_auth_params()
        return True

    # 3. PKCE Flow (code)
    if params.get("code"):
        return _handle_code_exchange(params.get("code"))
    
    # 4. Implicit/Legacy Flow (access_token in query grazie al fix JS)
    if params.get("access_token"):
        return _handle_implicit_token(params.get("access_token"), params.get("refresh_token"), params.get("type"))

    return False


def _inject_hash_fixer():
    """
    Inserisce JS per rilevare se i token sono finiti nell'hash URL (#) 
    invece che nella query (?), cosa che accade spesso con Supabase Auth.
    """
    js_code = """
    <script>
    // Controlla se l'URL ha un hash con access_token (Implicit Flow standard)
    if (window.location.hash && window.location.hash.includes('access_token')) {
        
        // Prendi l'hash togliendo il # iniziale
        const hash = window.location.hash.substring(1);
        const params = new URLSearchParams(hash);
        
        // Costruisci il nuovo URL mantenendo i parametri esistenti (es. ?nav=...)
        const newUrl = new URL(window.location.href);
        
        // Sposta tutti i parametri dall'hash alla query string
        params.forEach((value, key) => {
            newUrl.searchParams.set(key, value);
        });
        
        // Pulisci l'hash per evitare loop
        newUrl.hash = '';
        
        // Ricarica la pagina con il nuovo URL leggibile da Python
        window.location.href = newUrl.toString();
    }
    </script>
    """
    components.html(js_code, height=0, width=0)


def _handle_code_exchange(code: str) -> bool:
    client = get_supabase_client()
    if not client: return False
    
    try:
        res = client.auth.exchange_code_for_session({"auth_code": code})
        if res.user:
            _finalize_login(res.user)
            return True
    except Exception as e:
        st.error(f"Link scaduto o invalido: {e}")
    return False


def _handle_implicit_token(access_token, refresh_token, auth_type):
    client = get_supabase_client()
    if not client: return False
    
    try:
        # Imposta sessione manualmente
        if refresh_token:
            client.auth.set_session(access_token, refresh_token)
        else:
            # Fallback se manca refresh token (raro)
            client.auth.get_user(access_token)
            
        # Recupera utente per confermare che siamo loggati
        user = client.auth.get_user().user
        
        if user:
            _finalize_login(user)
            
            # Se è un recovery, forziamo la schermata password
            # O se l'URL aveva nav=update_password (gestito in finalize o main)
            if auth_type == "recovery":
                st.session_state.auth_mode = 'update_password'
                
            return True
            
    except Exception:
        pass
    return False


def _finalize_login(user):
    """Imposta lo stato sessione e decide la route in base a 'nav'."""
    _set_local_session(user)
    
    nav = st.query_params.get("nav")
    
    if nav == "update_password":
        st.session_state.show_auth = True
        st.session_state.auth_mode = 'update_password'
        st.session_state.auth_message = ('info', "🔐 Inserisci la tua nuova password.")
    elif nav == "login":
        st.session_state.show_auth = True
        st.session_state.auth_mode = 'login'
        st.session_state.auth_message = ('success', "✅ Email confermata! Accedi.")
    else:
        # Login standard
        pass
        
    _clear_auth_params()


def _clear_auth_params():
    keys = ['code', 'access_token', 'refresh_token', 'type', 'error', 'error_description']
    for k in keys:
        if k in st.query_params: del st.query_params[k]


# ==============================================================================
# UI RENDERING
# ==============================================================================

def render_auth_page(default_mode='login'):
    if 'auth_mode' not in st.session_state:
        st.session_state.auth_mode = default_mode
        
    st.markdown("""<div style="text-align: center; margin-bottom: 2rem;">
        <h1 style="color: #FF6600;">🏗️ POS FACILE</h1>
        <p style="color: #666;">Generatore POS per professionisti</p>
    </div>""", unsafe_allow_html=True)
    
    _show_auth_message()
    
    mode = st.session_state.auth_mode
    if mode == 'update_password' or mode == 'new_password':
        render_new_password_form()
    elif mode == 'reset':
        render_reset_password_form()
    elif mode == 'register':
        render_register_form()
    else:
        render_login_form()


def _show_auth_message():
    msg = st.session_state.get('auth_message')
    if msg:
        t, m = msg
        if t == 'success': st.success(m)
        elif t == 'error': st.error(m)
        elif t == 'warning': st.warning(m)
        else: st.info(m)
        st.session_state.auth_message = None


def render_login_form():
    with st.form("login_"):
        email = st.text_input("📧 Email")
        password = st.text_input("🔒 Password", type="password")
        if st.form_submit_button("Accedi", type="primary", use_container_width=True):
            s, m = login_user(email, password)
            if s: st.rerun()
            else: st.error(m)
    c1, c2 = st.columns(2)
    if c1.button("Registrati", use_container_width=True):
        st.session_state.auth_mode = 'register'; st.rerun()
    if c2.button("Recupera Password", use_container_width=True):
        st.session_state.auth_mode = 'reset'; st.rerun()


def render_register_form():
    with st.form("reg_"):
        email = st.text_input("📧 Email")
        p1 = st.text_input("🔒 Password", type="password")
        p2 = st.text_input("🔒 Conferma", type="password")
        if st.form_submit_button("Crea Account", type="primary", use_container_width=True):
            if p1==p2 and len(p1)>=6:
                s, m = register_user(email, p1)
                if s: st.success(m)
                else: st.error(m)
            else: st.error("Password non valide.")
    if st.button("Torna al Login", use_container_width=True):
        st.session_state.auth_mode = 'login'; st.rerun()


def render_reset_password_form():
    with st.form("reset_"):
        email = st.text_input("📧 Email")
        if st.form_submit_button("Invia Link", use_container_width=True):
            s, m = reset_password(email)
            if s: st.success(m)
            else: st.error(m)
    if st.button("Indietro", use_container_width=True):
        st.session_state.auth_mode = 'login'; st.rerun()


def render_new_password_form():
    st.info("🔐 Imposta la tua nuova password.")
    with st.form("new_pass_"):
        p1 = st.text_input("Nuova Password", type="password")
        p2 = st.text_input("Conferma Password", type="password")
        if st.form_submit_button("Aggiorna Password", type="primary", use_container_width=True):
            if p1==p2 and len(p1)>=6:
                s, m = update_user_password(p1)
                if s:
                    st.success(m)
                    time.sleep(2)
                    logout_user()
                    st.session_state.auth_mode = 'login'
                    st.rerun()
                else: st.error(m)
            else: st.error("Password non valide.")


def render_user_menu():
    if st.session_state.get('authenticated'):
        st.sidebar.write(f"👤 {st.session_state.get('user_email')}")
        if st.sidebar.button("Esci"): logout_user(); st.rerun()
