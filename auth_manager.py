# -*- coding: utf-8 -*-
"""
POS FACILE - Auth Manager (Supabase Auth)
Gestisce login, registrazione, sessioni utente e callback email.
Fix: Gestione redirect email conferma + recupero password via query params
"""

import streamlit as st

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
    """
    Restituisce l'URL base dell'app per i redirect Supabase.
    Prende il valore da secrets.toml o usa un default hardcoded se manca.
    """
    try:
        # Prima cerca nei secrets
        url = st.secrets.get("APP_URL", "")
        if url:
            return url.rstrip("/")
            
        # Fallback se non è impostato nei secrets (utile per evitare errori)
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
    """Registra un nuovo utente con redirect URL esplicito al login."""
    client = get_supabase_client()
    if not client:
        return False, "⚠️ Servizio temporaneamente non disponibile. Riprova tra qualche minuto."
    
    try:
        base_url = get_app_url()
        sign_up_params = {"email": email, "password": password}
        
        # FIX: Forziamo il redirect alla pagina di login dopo la conferma
        redirect_url = f"{base_url}/?nav=login"
        sign_up_params["options"] = {"email_redirect_to": redirect_url}
        
        response = client.auth.sign_up(sign_up_params)
        
        if response.user:
            return True, "Registrazione completata! Controlla la tua email e clicca il link di conferma."
        else:
            return False, "❌ Errore durante la registrazione. Riprova."
            
    except Exception as e:
        error_msg = str(e)
        if "User already registered" in error_msg:
            return False, "📧 Email già registrata. Prova ad accedere."
        elif "Password should be at least" in error_msg:
            return False, "🔒 La password deve essere di almeno 6 caratteri."
        elif "rate limit" in error_msg.lower():
            return False, "⏳ Troppe richieste. Attendi qualche minuto e riprova."
        else:
            return False, f"❌ Si è verificato un errore: {error_msg}"


def login_user(email: str, password: str) -> tuple:
    """Effettua il login."""
    client = get_supabase_client()
    if not client:
        return False, "⚠️ Servizio temporaneamente non disponibile. Riprova tra qualche minuto."
    
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
            return False, "❌ Email o password non corretti."
            
    except Exception as e:
        error_msg = str(e)
        if "Invalid login credentials" in error_msg:
            return False, "❌ Email o password non corretti."
        elif "Email not confirmed" in error_msg:
            return False, "📧 Email non ancora confermata. Controlla la posta."
        else:
            return False, "❌ Errore di accesso. Riprova."


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
    
    # Pulisce i dati di sessione del POS
    keys_to_clear = ['ditta', 'cantiere', 'lavoratori', 'attrezzature', 'sostanze', 'step']
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]


def reset_password(email: str) -> tuple:
    """
    Invia email per reset password con redirect URL SPECIFICO.
    Questo è il punto critico per far funzionare il main.py.
    """
    client = get_supabase_client()
    if not client:
        return False, "⚠️ Servizio temporaneamente non disponibile."
    
    try:
        base_url = get_app_url()
        
        # --- FIX PUNTO 1: Redirect forzato a ?nav=update_password ---
        # Questo dice a Supabase: "Dopo il click, manda l'utente alla pagina di update"
        redirect_url = f"{base_url}/?nav=update_password"
        
        client.auth.reset_password_email(
            email, 
            options={"redirect_to": redirect_url}
        )
        
        return True, "📧 Email inviata! Controlla la posta e clicca il link per reimpostare la password."
    except Exception as e:
        error_msg = str(e).lower()
        if "rate limit" in error_msg:
            return False, "⏳ Troppe richieste. Attendi qualche minuto."
        elif "user not found" in error_msg:
            return False, "📧 Nessun account trovato con questa email."
        else:
            return False, f"❌ Errore invio email: {str(e)}"


def update_user_password(new_password: str) -> tuple:
    """Aggiorna la password dell'utente (durante il flusso di recovery)."""
    client = get_supabase_client()
    if not client:
        return False, "⚠️ Servizio temporaneamente non disponibile."
    
    try:
        response = client.auth.update_user({"password": new_password})
        if response and response.user:
            return True, "Password aggiornata con successo! Ora puoi accedere."
        else:
            return False, "❌ Errore durante l'aggiornamento."
    except Exception as e:
        error_msg = str(e)
        if "same_password" in error_msg.lower():
            return False, "🔒 La nuova password deve essere diversa dalla precedente."
        elif "Password should be at least" in error_msg:
            return False, "🔒 La password deve essere di almeno 6 caratteri."
        else:
            return False, "❌ Errore generico. Riprova."


def is_authenticated() -> bool:
    return st.session_state.get('authenticated', False) and st.session_state.get('user_id') is not None


def get_current_user_id() -> str:
    return st.session_state.get('user_id')


def get_current_user_email() -> str:
    return st.session_state.get('user_email')


# ==============================================================================
# GESTIONE CALLBACK EMAIL SUPABASE
# ==============================================================================

def handle_auth_callback():
    """
    Gestisce i redirect da Supabase dopo click su link email.
    """
    params = st.query_params
    
    # --- Errori Supabase ---
    error = params.get("error")
    if error:
        desc = params.get("error_description", str(error))
        st.session_state.show_auth = True
        st.session_state.auth_mode = 'login'
        st.session_state.auth_message = ('error', f"❌ Errore: {desc}")
        _clear_auth_params()
        return True
    
    # --- PKCE Code Exchange (flusso principale) ---
    code = params.get("code")
    if code:
        return _handle_code_exchange(str(code))
    
    # --- Token diretto (flusso legacy) ---
    access_token = params.get("access_token")
    if access_token:
        # Se arriva un token diretto, è un caso raro o legacy, ma lo gestiamo
        _set_session_from_token(str(access_token), params.get("refresh_token"))
        # Decidiamo dove andare in base al tipo (se presente) o allo stato
        auth_type = params.get("type", "")
        
        st.session_state.show_auth = True
        if auth_type == "recovery":
            st.session_state.auth_mode = 'new_password' # Vecchio nome per update_password
        else:
            st.session_state.auth_mode = 'login'
            
        _clear_auth_params()
        return True
    
    return False


def _handle_code_exchange(code: str) -> bool:
    """Scambia il codice PKCE per una sessione."""
    client = get_supabase_client()
    if not client:
        return False
    
    try:
        response = client.auth.exchange_code_for_session({"auth_code": code})
        
        if response and response.user:
            user = response.user
            
            # --- INTEGRAZIONE CON MAIN.PY ---
            # main.py controlla 'nav' per decidere cosa mostrare.
            # Qui possiamo settare lo stato auth_mode per coerenza immediata.
            
            nav_param = st.query_params.get("nav")
            
            if nav_param == "update_password":
                # Caso Reset Password
                st.session_state.authenticated = True
                st.session_state.user = user
                st.session_state.user_id = user.id
                st.session_state.user_email = user.email
                
                st.session_state.show_auth = True
                st.session_state.auth_mode = 'update_password' # DEVE coincidere con main.py
                st.session_state.auth_message = ('info', "🔐 Inserisci la tua nuova password.")
                
            elif nav_param == "login":
                # Caso Conferma Registrazione
                st.session_state.show_auth = True
                st.session_state.auth_mode = 'login'
                st.session_state.auth_message = ('success', "✅ Email confermata! Effettua il login.")
                # Non logghiamo automaticamente dopo la conferma per sicurezza, ma si potrebbe fare
                
            else:
                # Fallback generico (es. login magico)
                st.session_state.authenticated = True
                st.session_state.user = user
                st.session_state.user_id = user.id
                
            _clear_auth_params()
            return True
            
    except Exception as e:
        st.session_state.show_auth = True
        st.session_state.auth_mode = 'login'
        st.session_state.auth_message = ('error', f"Link non valido o scaduto: {str(e)}")
        _clear_auth_params()
        return True
    
    return False


def _set_session_from_token(access_token: str, refresh_token: str = None):
    """Imposta la sessione manualmente (flusso implicito)."""
    client = get_supabase_client()
    if not client: return
    try:
        if refresh_token:
            client.auth.set_session(access_token, refresh_token)
        else:
            client.auth.get_user(access_token)
    except:
        pass


def _clear_auth_params():
    """Pulisce l'URL dai parametri sensibili."""
    params_to_remove = ['code', 'error', 'error_description', 'access_token', 'refresh_token', 'type']
    # Nota: Non rimuoviamo 'nav' qui perché serve al main.py
    for key in params_to_remove:
        if key in st.query_params:
            del st.query_params[key]


# ==============================================================================
# UI RENDERING
# ==============================================================================

def render_auth_page(default_mode='login'):
    """Renderizza la pagina di auth corretta."""
    
    if 'auth_mode' not in st.session_state:
        st.session_state.auth_mode = default_mode
    
    st.markdown("""<style>
        .auth-header {text-align: center; margin-bottom: 2rem;}
        .auth-header h1 {color: #FF6600; font-size: 2.5rem;}
    </style>""", unsafe_allow_html=True)
    
    st.markdown("""<div class="auth-header"><h1>🏗️ POS FACILE</h1><p style="color: #666; font-size: 18px;">Generatore POS per professionisti della sicurezza</p></div>""", unsafe_allow_html=True)
    
    _show_auth_message()
    
    mode = st.session_state.get('auth_mode', default_mode)
    
    # Mapping delle modalità (supporta sia vecchi nomi che nuovi)
    if mode == 'new_password' or mode == 'update_password':
        render_new_password_form()
    elif mode == 'register':
        render_register_form()
    elif mode == 'reset':
        render_reset_password_form()
    else:
        render_login_form()


def _show_auth_message():
    """Mostra banner di notifica."""
    msg = st.session_state.get('auth_message')
    if msg:
        m_type, m_text = msg
        if m_type == 'success': st.success(m_text)
        elif m_type == 'error': st.error(m_text)
        elif m_type == 'warning': st.warning(m_text)
        elif m_type == 'info': st.info(m_text)
        st.session_state.auth_message = None


def render_login_form():
    with st.form("login_form"):
        st.markdown("### Accedi")
        email = st.text_input("📧 Email")
        password = st.text_input("🔒 Password", type="password")
        if st.form_submit_button("Accedi →", use_container_width=True, type="primary"):
            if email and password:
                with st.spinner("Accesso..."):
                    success, msg = login_user(email, password)
                    if success: st.rerun()
                    else: st.error(msg)
            else: st.warning("Inserisci credenziali.")
    
    st.markdown("---")
    c1, c2 = st.columns(2)
    if c1.button("📝 Registrati", use_container_width=True):
        st.session_state.auth_mode = 'register'
        st.rerun()
    if c2.button("🔑 Recupera Password", use_container_width=True):
        st.session_state.auth_mode = 'reset'
        st.rerun()


def render_register_form():
    with st.form("register_form"):
        st.markdown("### Registrati")
        email = st.text_input("📧 Email")
        password = st.text_input("🔒 Password", type="password")
        confirm = st.text_input("🔒 Conferma Password", type="password")
        if st.form_submit_button("Crea Account", use_container_width=True, type="primary"):
            if password == confirm and len(password) >= 6:
                with st.spinner("Registrazione..."):
                    success, msg = register_user(email, password)
                    if success: st.success(msg)
                    else: st.error(msg)
            else: st.error("Password non valide (min 6 caratteri).")
            
    st.markdown("---")
    if st.button("Torna al Login", use_container_width=True):
        st.session_state.auth_mode = 'login'
        st.rerun()


def render_reset_password_form():
    with st.form("reset_form"):
        st.markdown("### Reset Password")
        email = st.text_input("📧 La tua Email")
        if st.form_submit_button("Invia Link", use_container_width=True):
            with st.spinner("Invio..."):
                success, msg = reset_password(email)
                if success: st.success(msg)
                else: st.error(msg)
                
    st.markdown("---")
    if st.button("Indietro", use_container_width=True):
        st.session_state.auth_mode = 'login'
        st.rerun()


def render_new_password_form():
    st.info("🔐 Sei in modalità recupero password.")
    with st.form("new_password_form"):
        new_pass = st.text_input("Nuova Password", type="password")
        conf_pass = st.text_input("Conferma Password", type="password")
        if st.form_submit_button("Aggiorna Password", use_container_width=True, type="primary"):
            if new_pass == conf_pass and len(new_pass) >= 6:
                success, msg = update_user_password(new_pass)
                if success:
                    st.success(msg)
                    st.session_state.auth_mode = 'login'
                    logout_user() # Logout per forzare login pulito
                    st.rerun()
                else:
                    st.error(msg)
            else:
                st.error("Le password non coincidono o sono troppo corte.")


def render_user_menu():
    if is_authenticated():
        st.sidebar.markdown("---")
        st.sidebar.write(f"👤 **{get_current_user_email()}**")
        if st.sidebar.button("Esci"):
            logout_user()
            st.rerun()
