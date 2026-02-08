# -*- coding: utf-8 -*-
"""
POS FACILE - Auth Manager v4
Risolve: hash fragment invisibile a Streamlit, perdita sessione tra rerun,
fallback REST API per update password.
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
        # Token di recovery - salvati qui sopravvivono ai rerun
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
    if "otp_expired" in m or "expired" in m:
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
        res = client.auth.sign_up({
            "email": email,
            "password": password,
            "options": {"email_redirect_to": f"{get_app_url()}/?nav=login"}
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
        client.auth.reset_password_email(email, options={
            "redirect_to": f"{get_app_url()}/?nav=update_password"
        })
        return True, "Email inviata! Controlla la posta e clicca il link."
    except Exception as e:
        return False, _tr(str(e))


def update_user_password(new_password):
    """
    Aggiorna password con token di recovery salvato in session_state.
    3 tentativi in cascata:
      1. set_session() + update_user() (standard)
      2. Header forzato + update_user() (fallback SDK)
      3. REST API diretta con requests (fallback nucleare)
    """
    access_token = st.session_state.get('_rcv_access')
    refresh_token = st.session_state.get('_rcv_refresh')

    if not access_token:
        return False, "Sessione di recupero scaduta. Richiedi un nuovo link."

    client = get_supabase_client()
    if not client:
        return False, "Servizio non disponibile."

    # --- TENTATIVO 1: set_session + update_user ---
    try:
        if refresh_token:
            client.auth.set_session(access_token, refresh_token)
        res = client.auth.update_user({"password": new_password})
        _clear_recovery()
        return True, "Password aggiornata!"
    except Exception:
        pass

    # --- TENTATIVO 2: Forza header + update_user ---
    try:
        client.options.headers["Authorization"] = f"Bearer {access_token}"
        client.postgrest.auth(access_token)
        client.auth.update_user({"password": new_password})
        _clear_recovery()
        return True, "Password aggiornata!"
    except Exception:
        pass

    # --- TENTATIVO 3: REST API diretta ---
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

    # Reset SOLO le chiavi di auth (non distruggere tutto session_state)
    for k in ['authenticated', 'user', '_rcv_access', '_rcv_refresh',
              'ditta', 'cantiere', 'lavoratori', 'attrezzature', 'sostanze', 'step']:
        if k in st.session_state:
            del st.session_state[k]


# ==============================================================================
# CALLBACK HANDLER
# ==============================================================================

def handle_auth_callback():
    """
    Gestisce i redirect da email Supabase.

    FLUSSO RECOVERY (il piu complesso):
    1. Utente clicca link -> browser va a:
       pos-facile.streamlit.app/?nav=update_password#access_token=XX&type=recovery
    2. PRIMO caricamento: Python vede ?nav=update_password ma NON il #hash.
       JS bridge (sotto) converte hash -> query params e fa location.replace().
    3. SECONDO caricamento: Python vede ?access_token=XX&type=recovery.
       Salva token in session_state. Mostra form nuova password.
    4. Utente compila form -> update_user_password usa i token salvati.

    FLUSSO CONFERMA EMAIL:
       pos-facile.streamlit.app/?nav=login  ->  mostra login + messaggio successo
    """

    # STEP 1: JS bridge - converte #hash in ?query
    _inject_hash_bridge()

    params = st.query_params

    # STEP 2: Errori
    if "error" in params:
        desc = str(params.get("error_description", params.get("error", ""))).replace("+", " ")
        st.session_state.show_auth = True
        st.session_state.auth_mode = 'login'
        st.session_state.auth_message = ("error", _tr(desc))
        _safe_clear_params()
        return True

    # STEP 3: Token dal hash (dopo JS bridge)
    access_token = params.get("access_token")
    if access_token:
        refresh_token = params.get("refresh_token")
        token_type = params.get("type", "")
        nav = params.get("nav", "")

        # PERSISTERE i token in session_state
        st.session_state._rcv_access = access_token
        st.session_state._rcv_refresh = refresh_token

        if token_type == "recovery" or nav == "update_password":
            st.session_state.show_auth = True
            st.session_state.auth_mode = 'update_password'
            st.session_state.authenticated = True  # Temporaneo per routing
            st.session_state.auth_message = ("info", "Imposta la tua nuova password.")
        elif token_type == "signup":
            st.session_state.show_auth = True
            st.session_state.auth_mode = 'login'
            st.session_state.auth_message = ("success", "Email confermata! Ora puoi accedere.")
        else:
            st.session_state.show_auth = True
            st.session_state.auth_mode = 'login'
            st.session_state.auth_message = ("success", "Accesso confermato!")

        _safe_clear_params()
        return True

    # STEP 4: PKCE code (conferma email)
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
                    "Link gia utilizzato o scaduto. Se hai confermato, prova ad accedere.")
        _safe_clear_params()
        return True

    # STEP 5: ?nav= senza token (primo caricamento - JS bridge non ha ancora agito)
    nav = params.get("nav")
    if nav == "login":
        st.session_state.show_auth = True
        st.session_state.auth_mode = 'login'
        st.session_state.auth_message = ("success", "Email confermata! Ora puoi accedere.")
        _safe_clear_params()
        return True

    if nav == "update_password":
        # Se abbiamo gia il token (da caricamento precedente)
        if st.session_state.get('_rcv_access'):
            st.session_state.show_auth = True
            st.session_state.auth_mode = 'update_password'
            st.session_state.authenticated = True
            return True
        # Altrimenti: aspettiamo il JS bridge (non fare nulla, non pulire params)
        return False

    return False


def _inject_hash_bridge():
    """
    JS che gira nel browser. Se l'URL parent contiene #access_token,
    lo converte in ?access_token e fa location.replace (no history entry).
    """
    js = """
    <script>
    (function(){
        function convert(w){
            try{
                var h=w.location.hash;
                if(!h||h.length<2||!h.includes('access_token'))return false;
                var hp=new URLSearchParams(h.substring(1));
                var base=w.location.origin+w.location.pathname;
                var ep=new URLSearchParams(w.location.search);
                hp.forEach(function(v,k){ep.set(k,v)});
                w.location.replace(base+'?'+ep.toString());
                return true;
            }catch(e){return false}
        }
        if(!convert(window.parent)){convert(window.top)}
    })();
    </script>
    """
    components.html(js, height=0, width=0)


def _safe_clear_params():
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

    # Messaggi dal callback
    msg = st.session_state.get('auth_message')
    if msg:
        tipo, testo = msg
        getattr(st, tipo if tipo in ('success','error','warning','info') else 'info')(testo)
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
    """Form nuova password dopo recovery."""

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
        st.sidebar.markdown("### 👤 Account")
        email = get_current_user_email()
        if email: st.sidebar.write(f"**{email}**")
        if st.sidebar.button("🚪 Logout", use_container_width=True):
            logout_user()
            st.rerun()
