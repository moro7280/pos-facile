# -*- coding: utf-8 -*-
"""
POS FACILE - Auth Manager v5 (DEFINITIVO)

SOLUZIONE: Supabase manda token nel #hash che Streamlit non legge.
Invece di JS bridge (non funziona su Streamlit Cloud), modifichiamo
il template email Supabase per usare {{ .TokenHash }} nei ?query params.
Python li legge, chiama verify_otp(), e ottiene la sessione.
"""

import streamlit as st
import time

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False


# ==============================================================================
# CONFIG
# ==============================================================================

def get_supabase_client():
    if not SUPABASE_AVAILABLE:
        return None
    try:
        return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_ANON_KEY"])
    except Exception:
        return None

def get_app_url():
    try:
        return st.secrets.get("APP_URL", "https://pos-facile.streamlit.app").rstrip("/")
    except Exception:
        return "https://pos-facile.streamlit.app"


# ==============================================================================
# STATE
# ==============================================================================

def init_auth_state():
    defaults = {
        'authenticated': False,
        'user': None,
        'show_auth': False,
        'auth_mode': 'login',
        'auth_message': None,
        '_rcv_access': None,
        '_rcv_refresh': None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def is_authenticated():
    return st.session_state.get('authenticated', False)

def get_current_user_email():
    u = st.session_state.get('user')
    return u.email if u and hasattr(u, 'email') else None


# ==============================================================================
# TRADUZIONE ERRORI
# ==============================================================================

def _tr(msg):
    m = msg.lower()
    if "invalid login" in m:          return "Email o password non corretti."
    if "email not confirmed" in m:    return "Email non ancora confermata. Controlla la posta."
    if "already registered" in m:     return "Email gia registrata. Prova ad accedere."
    if "rate limit" in m:             return "Troppe richieste. Attendi qualche minuto."
    if "password should" in m:        return "La password deve essere di almeno 6 caratteri."
    if "same_password" in m or "same password" in m:
        return "La nuova password deve essere diversa dalla precedente."
    if "otp_expired" in m or "expired" in m or "otp" in m:
        return "Link scaduto. Richiedi un nuovo link."
    if "session" in m and "missing" in m:
        return "Sessione scaduta. Richiedi un nuovo link."
    return "Si e verificato un errore. Riprova tra qualche minuto."


# ==============================================================================
# AUTH ACTIONS
# ==============================================================================

def login_user(email, password):
    client = get_supabase_client()
    if not client: return False, "Servizio non disponibile."
    try:
        res = client.auth.sign_in_with_password({"email": email, "password": password})
        if res.user and res.session:
            st.session_state.authenticated = True
            st.session_state.user = res.user
            return True, "Login effettuato!"
        return False, "Email o password non corretti."
    except Exception as e:
        return False, _tr(str(e))

def register_user(email, password):
    client = get_supabase_client()
    if not client: return False, "Servizio non disponibile."
    try:
        base_url = get_app_url()
        res = client.auth.sign_up({
            "email": email,
            "password": password,
            "options": {"email_redirect_to": f"{base_url}/?nav=login"}
        })
        if res.user:
            return True, "Registrazione completata! Controlla la tua email."
        return False, "Errore durante la registrazione."
    except Exception as e:
        return False, _tr(str(e))

def reset_password(email):
    client = get_supabase_client()
    if not client: return False, "Servizio non disponibile."
    try:
        client.auth.reset_password_email(email)
        return True, "Email inviata! Controlla la posta e clicca il link."
    except Exception as e:
        return False, _tr(str(e))


def verify_recovery_token(token_hash):
    """Verifica token_hash da URL, ritorna (True, session) o (False, errore)."""
    client = get_supabase_client()
    if not client:
        return False, "Servizio non disponibile."
    try:
        res = client.auth.verify_otp({
            "token_hash": token_hash,
            "type": "recovery"
        })
        if res and res.session:
            return True, res.session
        return False, "Link non valido o scaduto."
    except Exception as e:
        return False, _tr(str(e))


def update_user_password(new_password):
    """Aggiorna password con token recovery salvato in session_state."""
    access_token = st.session_state.get('_rcv_access')
    refresh_token = st.session_state.get('_rcv_refresh')
    if not access_token:
        return False, "Sessione di recupero scaduta. Richiedi un nuovo link."

    client = get_supabase_client()
    if not client:
        return False, "Servizio non disponibile."

    # TENTATIVO 1: set_session + update_user
    try:
        if refresh_token:
            client.auth.set_session(access_token, refresh_token)
        client.auth.update_user({"password": new_password})
        _clear_recovery()
        return True, "Password aggiornata!"
    except Exception:
        pass

    # TENTATIVO 2: Header forzato
    try:
        client.options.headers["Authorization"] = f"Bearer {access_token}"
        client.postgrest.auth(access_token)
        client.auth.update_user({"password": new_password})
        _clear_recovery()
        return True, "Password aggiornata!"
    except Exception:
        pass

    # TENTATIVO 3: REST API diretta
    try:
        import requests as req
        resp = req.put(
            f"{st.secrets['SUPABASE_URL']}/auth/v1/user",
            headers={
                "Authorization": f"Bearer {access_token}",
                "apikey": st.secrets["SUPABASE_ANON_KEY"],
                "Content-Type": "application/json"
            },
            json={"password": new_password},
            timeout=10
        )
        if resp.status_code == 200:
            _clear_recovery()
            return True, "Password aggiornata!"
        err = resp.json().get("msg", resp.json().get("message", ""))
        return False, _tr(err) if err else "Errore aggiornamento password."
    except Exception as e:
        return False, _tr(str(e))


def _clear_recovery():
    st.session_state._rcv_access = None
    st.session_state._rcv_refresh = None


def logout_user():
    client = get_supabase_client()
    if client:
        try: client.auth.sign_out()
        except: pass
    for k in ['authenticated', 'user', '_rcv_access', '_rcv_refresh',
              'ditta', 'cantiere', 'lavoratori', 'attrezzature', 'sostanze', 'step']:
        if k in st.session_state:
            del st.session_state[k]


# ==============================================================================
# CALLBACK HANDLER
# ==============================================================================

def handle_auth_callback():
    """
    Gestisce redirect da email Supabase. Tutto via query params, zero hash.

    RECOVERY: ?token_hash=XXX&type=recovery
      -> verify_otp() -> sessione -> form nuova password
    CONFERMA: ?nav=login oppure ?code=XXX
      -> mostra login con successo
    """
    params = st.query_params

    # --- ERRORI ---
    if "error" in params:
        desc = str(params.get("error_description", "")).replace("+", " ")
        st.session_state.show_auth = True
        st.session_state.auth_mode = 'login'
        st.session_state.auth_message = ("error", _tr(desc) if desc else "Si e verificato un errore.")
        _safe_clear()
        return True

    # --- RECOVERY: token_hash nei query params ---
    token_hash = params.get("token_hash")
    if token_hash:
        ok, result = verify_recovery_token(token_hash)
        if ok:
            session = result
            st.session_state._rcv_access = session.access_token
            st.session_state._rcv_refresh = session.refresh_token if hasattr(session, 'refresh_token') else None
            st.session_state.show_auth = True
            st.session_state.auth_mode = 'update_password'
            st.session_state.authenticated = True
            st.session_state.auth_message = ("info", "Imposta la tua nuova password.")
        else:
            st.session_state.show_auth = True
            st.session_state.auth_mode = 'login'
            st.session_state.auth_message = ("error", result)
        _safe_clear()
        return True

    # --- PKCE code (conferma email) ---
    code = params.get("code")
    if code:
        client = get_supabase_client()
        st.session_state.show_auth = True
        st.session_state.auth_mode = 'login'
        if client:
            try:
                res = client.auth.exchange_code_for_session({"auth_code": str(code)})
                if res and res.user:
                    st.session_state.auth_message = ("success", "Email confermata! Ora puoi accedere.")
                else:
                    st.session_state.auth_message = ("error", "Link non valido o scaduto.")
            except Exception:
                st.session_state.auth_message = ("warning",
                    "Link gia utilizzato. Se hai confermato, prova ad accedere.")
        _safe_clear()
        return True

    # --- NAV parameter ---
    nav = params.get("nav")
    if nav == "login":
        st.session_state.show_auth = True
        st.session_state.auth_mode = 'login'
        st.session_state.auth_message = ("success", "Email confermata! Ora puoi accedere.")
        _safe_clear()
        return True

    if nav == "update_password":
        if st.session_state.get('_rcv_access'):
            st.session_state.show_auth = True
            st.session_state.auth_mode = 'update_password'
            st.session_state.authenticated = True
            _safe_clear()
            return True
        st.session_state.show_auth = True
        st.session_state.auth_mode = 'reset'
        st.session_state.auth_message = ("error", "Link non valido. Richiedi un nuovo link di recupero.")
        _safe_clear()
        return True

    return False


def _safe_clear():
    try: st.query_params.clear()
    except: pass


# ==============================================================================
# UI
# ==============================================================================

def render_auth_page(default_mode='login'):
    st.markdown("""<style>
        .auth-header{text-align:center;margin-bottom:2rem}
        .auth-header h1{color:#FF6600;font-size:2.5rem}
    </style>""", unsafe_allow_html=True)
    st.markdown("""<div class="auth-header"><h1>🏗️ POS FACILE</h1>
        <p style="color:#666">Generatore POS per professionisti della sicurezza</p>
    </div>""", unsafe_allow_html=True)

    msg = st.session_state.get('auth_message')
    if msg:
        tipo, testo = msg
        fn = getattr(st, tipo, None) if tipo in ('success','error','warning','info') else None
        (fn or st.info)(testo)
        st.session_state.auth_message = None

    mode = st.session_state.get('auth_mode', default_mode)
    if mode == 'update_password':   _render_update_password()
    elif mode == 'register':        _render_register()
    elif mode == 'reset':           _render_reset()
    else:                           _render_login()


def _render_login():
    with st.form("login_form"):
        st.markdown("### Accedi")
        email = st.text_input("📧 Email", placeholder="email@esempio.com")
        pwd = st.text_input("🔒 Password", type="password")
        if st.form_submit_button("Accedi →", use_container_width=True, type="primary"):
            if email and pwd:
                ok, msg = login_user(email, pwd)
                if ok: st.success(msg); st.rerun()
                else: st.error(msg)
            else: st.warning("Inserisci email e password.")
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📝 Non hai un account? **Registrati**", key="sw_reg", use_container_width=True):
            st.session_state.auth_mode = 'register'; st.rerun()
    with c2:
        if st.button("🔑 Password dimenticata?", key="sw_rst", use_container_width=True):
            st.session_state.auth_mode = 'reset'; st.rerun()


def _render_register():
    with st.form("register_form"):
        st.markdown("### Crea il tuo Account")
        st.markdown("*Il primo POS e gratuito!*")
        email = st.text_input("📧 Email *", placeholder="email@esempio.com")
        p1 = st.text_input("🔒 Password *", type="password", placeholder="Min 6 caratteri")
        p2 = st.text_input("🔒 Conferma Password *", type="password")
        if st.form_submit_button("🚀 Registrati Gratis →", use_container_width=True, type="primary"):
            if not email: st.error("Inserisci la tua email.")
            elif p1 != p2: st.error("Le password non coincidono.")
            elif len(p1) < 6: st.error("Password troppo corta (minimo 6 caratteri).")
            else:
                ok, msg = register_user(email, p1)
                if ok: st.success(msg)
                else: st.error(msg)
    st.markdown("---")
    if st.button("🔐 Hai gia un account? **Accedi**", key="sw_log", use_container_width=True):
        st.session_state.auth_mode = 'login'; st.rerun()


def _render_reset():
    with st.form("reset_form"):
        st.markdown("### Recupero Password")
        st.markdown("*Inserisci la tua email per ricevere il link di reset.*")
        email = st.text_input("📧 Email")
        if st.form_submit_button("Invia Link di Reset", use_container_width=True):
            if email:
                ok, msg = reset_password(email)
                if ok: st.success(msg)
                else: st.error(msg)
            else: st.warning("Inserisci la tua email.")
    st.markdown("---")
    if st.button("🔐 Torna al Login", key="sw_log2", use_container_width=True):
        st.session_state.auth_mode = 'login'; st.rerun()


def _render_update_password():
    if not st.session_state.get('_rcv_access'):
        st.error("Sessione di recupero scaduta. Richiedi un nuovo link.")
        st.markdown("---")
        if st.button("🔑 Richiedi nuovo link", key="new_rst"):
            st.session_state.auth_mode = 'reset'; st.rerun()
        return

    st.markdown("### 🔐 Imposta Nuova Password")
    with st.form("update_pwd_form"):
        p1 = st.text_input("🔒 Nuova Password *", type="password", placeholder="Min 6 caratteri")
        p2 = st.text_input("🔒 Conferma *", type="password")
        if st.form_submit_button("✅ Aggiorna Password", use_container_width=True, type="primary"):
            if not p1: st.error("Inserisci la nuova password.")
            elif p1 != p2: st.error("Le password non coincidono.")
            elif len(p1) < 6: st.error("Password troppo corta (minimo 6 caratteri).")
            else:
                with st.spinner("Aggiornamento..."):
                    ok, msg = update_user_password(p1)
                if ok:
                    st.success("✅ Password aggiornata! Ora puoi accedere.")
                    time.sleep(2)
                    logout_user()
                    st.session_state.show_auth = True
                    st.session_state.auth_mode = 'login'
                    st.session_state.auth_message = ("success", "Password aggiornata! Accedi con la nuova password.")
                    st.rerun()
                else:
                    st.error(msg)
    st.markdown("---")
    if st.button("🔐 Torna al Login", key="sw_log3", use_container_width=True):
        _clear_recovery()
        logout_user()
        st.session_state.show_auth = True
        st.session_state.auth_mode = 'login'
        st.rerun()


def render_user_menu():
    if is_authenticated():
        st.sidebar.markdown("---")
        email = get_current_user_email()
        if email: st.sidebar.write(f"👤 **{email}**")
        if st.sidebar.button("🚪 Logout", use_container_width=True):
            logout_user()
            st.rerun()
