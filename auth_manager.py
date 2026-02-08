# -*- coding: utf-8 -*-
import streamlit as st
import streamlit.components.v1 as components
import time

# Tenta l'import di Supabase
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

# --- CONFIGURAZIONE CLIENT ---
def get_supabase_client():
    if not SUPABASE_AVAILABLE: return None
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_ANON_KEY"]
        return create_client(url, key)
    except Exception:
        return None

def get_app_url():
    try:
        url = st.secrets.get("APP_URL", "https://pos-facile.streamlit.app")
        return url.rstrip("/")
    except:
        return "https://pos-facile.streamlit.app"

# --- STATO ---
def init_auth_state():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'auth_mode' not in st.session_state:
        st.session_state.auth_mode = 'login'
    if 'auth_message' not in st.session_state:
        st.session_state.auth_message = None
    # NUOVO: Persistenza Token
    if 'access_token' not in st.session_state:
        st.session_state.access_token = None
    if 'refresh_token' not in st.session_state:
        st.session_state.refresh_token = None

def is_authenticated():
    return st.session_state.get('authenticated', False)

# Helper per salvare la sessione tra i vari refresh di Streamlit
def _persist_session(session):
    if session:
        st.session_state.authenticated = True
        st.session_state.user = session.user
        st.session_state.access_token = session.access_token
        st.session_state.refresh_token = session.refresh_token

# Helper per ripristinare la sessione nel client prima di un'azione
def _restore_session(client):
    token = st.session_state.get('access_token')
    refresh = st.session_state.get('refresh_token')
    if token:
        try:
            client.auth.set_session(token, refresh or "")
            return True
        except Exception:
            return False
    return False

# --- AZIONI ---
def login_user(email, password):
    client = get_supabase_client()
    if not client: return False, "Errore connessione DB"
    try:
        res = client.auth.sign_in_with_password({"email": email, "password": password})
        if res.user and res.session:
            _persist_session(res.session) # Salva sessione
            return True, "Login OK"
        return False, "Credenziali errate"
    except Exception as e:
        return False, str(e)

def register_user(email, password):
    client = get_supabase_client()
    if not client: return False, "Errore connessione DB"
    try:
        base_url = get_app_url()
        res = client.auth.sign_up({
            "email": email,
            "password": password,
            "options": {"email_redirect_to": f"{base_url}/?nav=login"}
        })
        if res.user: return True, "Controlla la tua email!"
        return False, "Errore registrazione"
    except Exception as e:
        return False, str(e)

def reset_password(email):
    client = get_supabase_client()
    if not client: return False, "Errore connessione DB"
    try:
        base_url = get_app_url()
        res = client.auth.reset_password_email(email, options={
            "redirect_to": f"{base_url}/?nav=update_password"
        })
        return True, "Email inviata!"
    except Exception as e:
        return False, str(e)

def update_user_password(new_password):
    client = get_supabase_client()
    if not client: return False, "Errore connessione DB"
    
    # FONDAMENTALE: Ripristina la sessione prima di aggiornare
    if not _restore_session(client):
        return False, "Sessione scaduta. Riprova il login."

    try:
        res = client.auth.update_user({"password": new_password})
        if res.user: 
            # Aggiorna anche la sessione salvata con i nuovi dati se necessario
            if res.session: _persist_session(res.session)
            return True, "Password aggiornata!"
        return False, "Errore aggiornamento"
    except Exception as e:
        return False, str(e)

def logout_user():
    client = get_supabase_client()
    if client: 
        try: client.auth.sign_out()
        except: pass
    
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.access_token = None
    st.session_state.refresh_token = None
    st.rerun()

# --- CALLBACK & JS FIX ---
def handle_auth_callback():
    # 1. FIX JS: Cattura hash (#) dalla finestra PRINCIPALE
    js = """
    <script>
    try {
        var parentLocation = window.parent.location;
        if (parentLocation.hash && (parentLocation.hash.includes('access_token') || parentLocation.hash.includes('error'))) {
            var params = new URLSearchParams(parentLocation.hash.substring(1));
            var newUrl = new URL(parentLocation.href);
            params.forEach((v, k) => newUrl.searchParams.set(k, v));
            newUrl.hash = '';
            parentLocation.href = newUrl.toString();
        }
    } catch (e) {}
    </script>
    """
    components.html(js, height=0, width=0)

    params = st.query_params
    
    # GESTIONE ERRORI
    if "error" in params:
        error_code = params.get("error_code", "")
        desc = params.get("error_description", "Errore sconosciuto")
        st.session_state.show_auth = True
        st.session_state.auth_mode = 'login' 
        if error_code == "otp_expired":
            st.session_state.auth_message = ("error", "⚠️ Link scaduto. Richiedi un nuovo reset.")
        else:
            st.session_state.auth_message = ("error", f"❌ Errore: {desc}")
        st.query_params.clear()
        return True

    # Scambio codice PKCE
    if "code" in params:
        client = get_supabase_client()
        if client:
            try:
                res = client.auth.exchange_code_for_session({"auth_code": params["code"]})
                if res.user and res.session:
                    _persist_session(res.session) # PERSISTENZA
                    
                    nav = params.get("nav")
                    if nav == "update_password": st.session_state.auth_mode = "update_password"
                    elif nav == "login": st.session_state.auth_mode = "login"; st.session_state.auth_message = ("success", "Email confermata!")
                    st.query_params.clear()
                    return True
            except: pass
    
    # Token implicito (Recovery)
    if "access_token" in params:
        client = get_supabase_client()
        if client:
            try:
                client.auth.set_session(params["access_token"], params.get("refresh_token", ""))
                # Recupera la sessione completa per avere anche il refresh token corretto
                session = client.auth.get_session()
                if session:
                    _persist_session(session) # PERSISTENZA
                
                nav = params.get("nav")
                if nav == "update_password" or params.get("type") == "recovery":
                    st.session_state.auth_mode = "update_password"
                
                st.query_params.clear()
                return True
            except: pass
                
    return False

# --- UI ---
def render_auth_page(default_mode='login'):
    st.title("🔐 Accesso Utente")
    
    if st.session_state.auth_message:
        tipo, testo = st.session_state.auth_message
        if tipo == 'success': st.success(testo)
        elif tipo == 'error': st.error(testo)
        else: st.info(testo)
        st.session_state.auth_message = None

    mode = st.session_state.auth_mode
    
    if mode == 'login':
        with st.form("login"):
            email = st.text_input("Email")
            pwd = st.text_input("Password", type="password")
            if st.form_submit_button("Accedi", type="primary"):
                ok, msg = login_user(email, pwd)
                if ok: st.rerun()
                else: st.error(msg)
        if st.button("Password dimenticata?"):
            st.session_state.auth_mode = 'reset'
            st.rerun()
        if st.button("Registrati"):
            st.session_state.auth_mode = 'register'
            st.rerun()

    elif mode == 'register':
        with st.form("reg"):
            email = st.text_input("Email")
            p1 = st.text_input("Password", type="password")
            p2 = st.text_input("Conferma", type="password")
            if st.form_submit_button("Crea Account"):
                if p1==p2 and len(p1)>5:
                    ok, msg = register_user(email, p1)
                    if ok: st.success(msg)
                    else: st.error(msg)
                else: st.error("Password non valide")
        if st.button("Torna al Login"):
            st.session_state.auth_mode = 'login'
            st.rerun()

    elif mode == 'reset':
        with st.form("rst"):
            email = st.text_input("Email per il recupero")
            if st.form_submit_button("Invia Link"):
                ok, msg = reset_password(email)
                if ok: st.success(msg)
                else: st.error(msg)
        if st.button("Annulla"):
            st.session_state.auth_mode = 'login'
            st.rerun()

    elif mode == 'update_password':
        st.warning("🔒 Imposta la tua nuova password")
        with st.form("newpwd"):
            p1 = st.text_input("Nuova Password", type="password")
            p2 = st.text_input("Conferma", type="password")
            if st.form_submit_button("Aggiorna"):
                if p1==p2 and len(p1)>5:
                    ok, msg = update_user_password(p1)
                    if ok:
                        st.success("Fatto! Ora accedi.")
                        time.sleep(2)
                        st.session_state.auth_mode = 'login'
                        logout_user() # Forza logout pulito
                        st.rerun()
                    else: st.error(msg)
                else: st.error("Password non valide")

def render_user_menu():
    if st.sidebar.button("Logout"):
        logout_user()
