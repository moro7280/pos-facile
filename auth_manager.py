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
    
    CONFIGURAZIONE NECESSARIA in .streamlit/secrets.toml:
        APP_URL = "https://posfacile.streamlit.app"
    
    E in Supabase Dashboard > Authentication > URL Configuration:
        - Site URL: https://posfacile.streamlit.app
        - Redirect URLs: https://posfacile.streamlit.app
    """
    try:
        url = st.secrets.get("APP_URL", "")
        if url:
            return url.rstrip("/")
    except Exception:
        pass
    return ""


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
    """Registra un nuovo utente con redirect URL per conferma email."""
    client = get_supabase_client()
    if not client:
        return False, "⚠️ Servizio temporaneamente non disponibile. Riprova tra qualche minuto."
    
    try:
        app_url = get_app_url()
        sign_up_params = {"email": email, "password": password}
        
        if app_url:
            sign_up_params["options"] = {"email_redirect_to": app_url}
        
        response = client.auth.sign_up(sign_up_params)
        
        if response.user:
            return True, "Registrazione completata! Controlla la tua email e clicca il link di conferma."
        else:
            return False, "❌ Errore durante la registrazione. Riprova."
            
    except Exception as e:
        error_msg = str(e)
        if "User already registered" in error_msg:
            return False, "📧 Email gia registrata. Prova ad accedere."
        elif "Password should be at least" in error_msg:
            return False, "🔒 La password deve essere di almeno 6 caratteri."
        elif "rate limit" in error_msg.lower():
            return False, "⏳ Troppe richieste. Attendi qualche minuto e riprova."
        elif "already been registered" in error_msg.lower() or "already registered" in error_msg.lower():
            return False, "📧 Email gia registrata. Prova ad accedere."
        elif "invalid" in error_msg.lower() and "email" in error_msg.lower():
            return False, "📧 Indirizzo email non valido."
        elif "signup" in error_msg.lower() and "disabled" in error_msg.lower():
            return False, "🚫 Le registrazioni sono temporaneamente sospese. Riprova piu tardi."
        else:
            return False, f"❌ Si e verificato un errore. Riprova tra qualche minuto."


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
            return False, "📧 Email non ancora confermata. Controlla la tua casella di posta e clicca il link di conferma."
        elif "rate limit" in error_msg.lower():
            return False, "⏳ Troppi tentativi. Attendi qualche minuto e riprova."
        elif "invalid" in error_msg.lower() and "email" in error_msg.lower():
            return False, "📧 Indirizzo email non valido."
        else:
            return False, "❌ Si e verificato un errore. Riprova tra qualche minuto."


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
    
    keys_to_clear = ['ditta', 'cantiere', 'lavoratori', 'attrezzature', 'sostanze', 'step']
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]


def reset_password(email: str) -> tuple:
    """Invia email per reset password con redirect URL."""
    client = get_supabase_client()
    if not client:
        return False, "⚠️ Servizio temporaneamente non disponibile. Riprova tra qualche minuto."
    
    try:
        app_url = get_app_url()
        
        if app_url:
            client.auth.reset_password_email(email, {"redirect_to": app_url})
        else:
            client.auth.reset_password_email(email)
        
        return True, "📧 Email inviata! Controlla la posta e clicca il link per reimpostare la password."
    except Exception as e:
        error_msg = str(e).lower()
        if "rate limit" in error_msg:
            return False, "⏳ Troppe richieste. Attendi qualche minuto e riprova."
        elif "user not found" in error_msg:
            return False, "📧 Nessun account trovato con questa email."
        else:
            return False, "❌ Si e verificato un errore. Riprova tra qualche minuto."


def update_user_password(new_password: str) -> tuple:
    """Aggiorna la password dell'utente (durante il flusso di recovery)."""
    client = get_supabase_client()
    if not client:
        return False, "⚠️ Servizio temporaneamente non disponibile. Riprova tra qualche minuto."
    
    try:
        response = client.auth.update_user({"password": new_password})
        if response and response.user:
            return True, "Password aggiornata con successo! Ora puoi accedere."
        else:
            return False, "❌ Errore durante l'aggiornamento della password. Riprova."
    except Exception as e:
        error_msg = str(e)
        if "same_password" in error_msg.lower() or "same password" in error_msg.lower():
            return False, "🔒 La nuova password deve essere diversa dalla precedente."
        elif "Password should be at least" in error_msg:
            return False, "🔒 La password deve essere di almeno 6 caratteri."
        elif "rate limit" in error_msg.lower():
            return False, "⏳ Troppe richieste. Attendi qualche minuto e riprova."
        else:
            return False, "❌ Si e verificato un errore. Riprova tra qualche minuto."


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
    
    Flusso PKCE (default Supabase):
      1. Utente clicca link email
      2. Supabase redirige a: https://app.url/?code=XXXX
      3. L'app scambia il codice per una sessione
    
    Flusso legacy/implicit:
      - ?type=signup&access_token=...  -> Conferma email
      - ?type=recovery&access_token=... -> Reset password
    
    Ritorna True se ha gestito un callback, False altrimenti.
    """
    params = st.query_params
    
    # --- Errori Supabase ---
    error = params.get("error")
    error_desc = params.get("error_description")
    if error:
        desc = str(error_desc or error).replace("+", " ")
        st.session_state.show_auth = True
        st.session_state.auth_mode = 'login'
        st.session_state.auth_message = ('error', f"❌ Si e verificato un errore: {desc}")
        _clear_auth_params()
        return True
    
    # --- PKCE Code Exchange (flusso principale) ---
    code = params.get("code")
    if code:
        return _handle_code_exchange(str(code))
    
    # --- Token diretto (flusso implicit/legacy) ---
    auth_type = params.get("type")
    access_token = params.get("access_token")
    refresh_token = params.get("refresh_token")
    
    if auth_type == "signup":
        st.session_state.show_auth = True
        st.session_state.auth_mode = 'login'
        st.session_state.auth_message = ('success', "✅ Email confermata! Ora puoi accedere.")
        _clear_auth_params()
        return True
    
    if auth_type == "recovery":
        if access_token:
            _set_session_from_token(str(access_token), str(refresh_token) if refresh_token else None)
        st.session_state.show_auth = True
        st.session_state.auth_mode = 'new_password'
        st.session_state.auth_message = ('info', "Imposta la tua nuova password.")
        _clear_auth_params()
        return True
    
    if auth_type == "magiclink" and access_token:
        _set_session_from_token(str(access_token), str(refresh_token) if refresh_token else None)
        st.session_state.show_auth = True
        st.session_state.auth_mode = 'login'
        st.session_state.auth_message = ('success', "✅ Accesso confermato!")
        _clear_auth_params()
        return True
    
    return False


def _handle_code_exchange(code: str) -> bool:
    """Scambia il codice PKCE per una sessione e determina il tipo di flusso."""
    client = get_supabase_client()
    if not client:
        st.session_state.show_auth = True
        st.session_state.auth_mode = 'login'
        st.session_state.auth_message = ('error', "Servizio di autenticazione non disponibile. Riprova tra qualche minuto.")
        _clear_auth_params()
        return True
    
    try:
        response = client.auth.exchange_code_for_session({"auth_code": code})
        
        if response and response.user:
            user = response.user
            
            # Determina se e un recovery:
            # Supabase include recovery_sent_at nel profilo utente se il flusso e recovery
            is_recovery = False
            try:
                if hasattr(user, 'recovery_sent_at') and user.recovery_sent_at:
                    is_recovery = True
            except Exception:
                pass
            
            # Altro indicatore: appMetadata o il fatto che l'utente abbia aal1
            # In pratica controlliamo se abbiamo session con aal
            if not is_recovery:
                try:
                    if hasattr(response, 'session') and response.session:
                        # Se ha un session token ma l'email e gia confermata da prima,
                        # potrebbe essere recovery. Controlliamo user.email_confirmed_at
                        # vs last_sign_in_at
                        pass
                except Exception:
                    pass
            
            if is_recovery:
                # Recovery: imposta sessione per permettere update_user
                st.session_state.authenticated = True
                st.session_state.user = user
                st.session_state.user_id = user.id
                st.session_state.user_email = user.email
                st.session_state.show_auth = True
                st.session_state.auth_mode = 'new_password'
                st.session_state.auth_message = ('info', "Imposta la tua nuova password.")
            else:
                # Conferma email: rimanda al login
                st.session_state.show_auth = True
                st.session_state.auth_mode = 'login'
                st.session_state.auth_message = ('success', "✅ Email confermata con successo! Ora puoi accedere.")
            
            _clear_auth_params()
            return True
        else:
            st.session_state.show_auth = True
            st.session_state.auth_mode = 'login'
            st.session_state.auth_message = ('error', "❌ Link non valido o scaduto. Riprova la registrazione o il recupero password.")
            _clear_auth_params()
            return True
            
    except Exception as e:
        error_msg = str(e).lower()
        
        # Codice gia usato o scaduto - probabilmente l'email e gia confermata
        st.session_state.show_auth = True
        st.session_state.auth_mode = 'login'
        
        if "already" in error_msg or "expired" in error_msg or "invalid" in error_msg or "used" in error_msg or "redeemed" in error_msg:
            st.session_state.auth_message = ('warning', 
                "⚠️ Questo link e gia stato utilizzato o e scaduto. "
                "Se hai gia confermato l'email, puoi accedere normalmente.")
        else:
            st.session_state.auth_message = ('warning', 
                "⚠️ Link gia utilizzato o scaduto. Se hai confermato l'email, prova ad accedere.")
        
        _clear_auth_params()
        return True


def _set_session_from_token(access_token: str, refresh_token: str = None):
    """Imposta la sessione da un token (flusso legacy/implicit)."""
    client = get_supabase_client()
    if not client:
        return
    
    try:
        if refresh_token:
            client.auth.set_session(access_token, refresh_token)
        
        user_response = client.auth.get_user(access_token)
        if user_response and user_response.user:
            st.session_state.authenticated = True
            st.session_state.user = user_response.user
            st.session_state.user_id = user_response.user.id
            st.session_state.user_email = user_response.user.email
    except Exception as e:
        print(f"Errore set session from token: {e}")


def _clear_auth_params():
    """Pulisce i parametri URL di autenticazione."""
    try:
        auth_keys = ['code', 'type', 'access_token', 'refresh_token', 
                     'error', 'error_description', 'error_code']
        for key in auth_keys:
            if key in st.query_params:
                del st.query_params[key]
    except Exception:
        try:
            st.query_params.clear()
        except Exception:
            pass


# ==============================================================================
# UI RENDERING
# ==============================================================================

def render_auth_page(default_mode='login'):
    """Pagina di autenticazione con navigazione via session state."""
    
    if 'auth_mode' not in st.session_state:
        st.session_state.auth_mode = default_mode
    
    st.markdown("""<style>
        .auth-header {text-align: center; margin-bottom: 2rem;}
        .auth-header h1 {color: #FF6600; font-size: 2.5rem;}
    </style>""", unsafe_allow_html=True)
    
    st.markdown("""<div class="auth-header"><h1>🏗️ POS FACILE</h1><p style="color: #666; font-size: 18px;">Generatore POS per professionisti della sicurezza</p></div>""", unsafe_allow_html=True)
    
    # Mostra messaggi dal callback
    _show_auth_message()
    
    mode = st.session_state.get('auth_mode', default_mode)
    
    if mode == 'new_password':
        render_new_password_form()
    elif mode == 'register':
        render_register_form()
    elif mode == 'reset':
        render_reset_password_form()
    else:
        render_login_form()


def _show_auth_message():
    """Mostra e pulisce i messaggi pendenti."""
    msg = st.session_state.get('auth_message')
    if msg:
        msg_type, msg_text = msg
        if msg_type == 'success':
            st.success(msg_text)
        elif msg_type == 'error':
            st.error(msg_text)
        elif msg_type == 'warning':
            st.warning(msg_text)
        elif msg_type == 'info':
            st.info(msg_text)
        st.session_state.auth_message = None


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
            else: st.warning("⚠️ Inserisci email e password")
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝 Non hai un account? **Registrati**", key="switch_to_register", use_container_width=True):
            st.session_state.auth_mode = 'register'
            st.rerun()
    with col2:
        if st.button("🔑 Password dimenticata?", key="switch_to_reset", use_container_width=True):
            st.session_state.auth_mode = 'reset'
            st.rerun()


def render_register_form():
    with st.form("register_form"):
        st.markdown("### Crea il tuo Account")
        st.markdown("*Il primo POS e gratuito!*")
        email = st.text_input("📧 Email *", placeholder="email@esempio.com")
        password = st.text_input("🔒 Password *", type="password", placeholder="Min 6 caratteri")
        confirm = st.text_input("🔒 Conferma Password *", type="password")
        if st.form_submit_button("🚀 Registrati Gratis →", use_container_width=True, type="primary"):
            if not email:
                st.error("⚠️ Inserisci la tua email")
            elif password != confirm:
                st.error("🔒 Le password non coincidono")
            elif len(password) < 6:
                st.error("🔒 Password troppo corta (minimo 6 caratteri)")
            else:
                with st.spinner("Registrazione..."):
                    success, msg = register_user(email, password)
                    if success: st.success(msg)
                    else: st.error(msg)
    
    st.markdown("---")
    if st.button("🔐 Hai gia un account? **Accedi**", key="switch_to_login", use_container_width=True):
        st.session_state.auth_mode = 'login'
        st.rerun()


def render_new_password_form():
    """Form per impostare una nuova password (dopo click su link recovery)."""
    st.markdown("### 🔐 Imposta Nuova Password")
    st.markdown("Scegli una nuova password per il tuo account.")
    
    with st.form("new_password_form"):
        new_password = st.text_input("🔒 Nuova Password *", type="password", placeholder="Min 6 caratteri")
        confirm_password = st.text_input("🔒 Conferma Nuova Password *", type="password")
        
        if st.form_submit_button("✅ Aggiorna Password", use_container_width=True, type="primary"):
            if not new_password:
                st.error("⚠️ Inserisci la nuova password")
            elif new_password != confirm_password:
                st.error("🔒 Le password non coincidono")
            elif len(new_password) < 6:
                st.error("🔒 Password troppo corta (minimo 6 caratteri)")
            else:
                with st.spinner("Aggiornamento password..."):
                    success, msg = update_user_password(new_password)
                    if success:
                        st.success(msg)
                        logout_user()
                        st.session_state.show_auth = True
                        st.session_state.auth_mode = 'login'
                        st.session_state.auth_message = ('success', "✅ Password aggiornata! Accedi con la nuova password.")
                        st.rerun()
                    else:
                        st.error(msg)
    
    st.markdown("---")
    if st.button("🔐 Torna al Login", key="switch_to_login_from_newpw", use_container_width=True):
        logout_user()
        st.session_state.auth_mode = 'login'
        st.rerun()


def render_reset_password_form():
    with st.form("reset_form"):
        st.markdown("### Recupero Password")
        st.markdown("*Inserisci la tua email per ricevere il link di reset.*")
        email = st.text_input("📧 Email")
        if st.form_submit_button("Invia Link di Reset", use_container_width=True):
            if email:
                with st.spinner("Invio..."):
                    success, msg = reset_password(email)
                    if success: st.success(msg)
                    else: st.error(msg)
            else:
                st.warning("⚠️ Inserisci la tua email")
    
    st.markdown("---")
    if st.button("🔐 Torna al Login", key="switch_to_login_from_reset", use_container_width=True):
        st.session_state.auth_mode = 'login'
        st.rerun()


def render_user_menu():
    """Renderizza il menu utente nella sidebar"""
    if is_authenticated():
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 👤 Account")
        st.sidebar.write(f"**{get_current_user_email()}**")
        
        if st.sidebar.button("🚪 Logout", use_container_width=True):
            logout_user()
            st.rerun()
