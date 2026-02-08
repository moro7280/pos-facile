# -*- coding: utf-8 -*-
"""
POS FACILE - Landing Page V10 FINAL
Fix: Accesso risolto & Gestione Prioritaria URL
"""

import streamlit as st
import traceback

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(
    page_title="POS FACILE | Generatore POS con AI",
    page_icon="🏗️",
    layout="wide"
)

# --- IMPORT MODULI CON GESTIONE ERRORI ---
try:
    import auth_manager
    AUTH_AVAILABLE = True
except Exception:
    st.error("❌ ERRORE CRITICO: Impossibile caricare auth_manager.py")
    st.code(traceback.format_exc())
    st.stop()

try:
    from license_manager import render_subscription_sidebar
except ImportError:
    def render_subscription_sidebar(): 
        with st.sidebar:
            st.info("Piano: Free (Modulo licenze non trovato)")


def inject_css():
    """CSS pulito e professionale"""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
        #MainMenu, footer, header {visibility: hidden;}
        .stDeployButton {display: none;}
        .block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; max-width: 1100px !important; }
        
        /* HERO */
        .hero-container { text-align: center; padding-bottom: 2rem; }
        .hero-badge { display: inline-block; background: #FFF7ED; color: #EA580C; padding: 8px 20px; border-radius: 50px; font-size: 0.9rem; font-weight: 600; border: 1px solid #FDBA74; margin-bottom: 1.5rem; }
        .hero-title { font-size: 3.5rem; font-weight: 900; color: #1a1a2e; line-height: 1.0 !important; margin-bottom: 0 !important; text-align: center; letter-spacing: -1px; }
        .hero-title-orange { font-size: 3.5rem; font-weight: 900; color: #FF6600; line-height: 1.0 !important; margin-top: 5px !important; margin-bottom: 1.5rem !important; text-align: center; letter-spacing: -1px; }
        .hero-subtitle { font-size: 1.25rem; color: #64748B; text-align: center !important; max-width: 700px; margin: 0 auto 2.5rem auto !important; line-height: 1.6; display: block; }
        
        /* CARDS & UI */
        .stats-bar { background-color: #1a1a2e; padding: 3rem 1rem; border-radius: 16px; margin: 3rem 0; box-shadow: 0 10px 30px rgba(0,0,0,0.15); }
        .stat-item { text-align: center; padding: 10px; }
        .stat-number { font-size: 3rem; font-weight: 800; color: #FF6600; margin: 0; line-height: 1; }
        .stat-label { font-size: 0.9rem; color: #E2E8F0; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600; margin-top: 10px; }
        
        .feature-card { background: white; border: 1px solid #E2E8F0; border-radius: 16px; padding: 30px 25px; text-align: center; height: 100%; transition: all 0.3s; }
        .feature-card:hover { border-color: #FF6600; box-shadow: 0 10px 30px rgba(0,0,0,0.08); transform: translateY(-3px); }
        
        .price-card { background: white; border: 2px solid #E2E8F0; border-radius: 20px; padding: 30px 25px; text-align: center; height: 100%; }
        .price-card.featured { border-color: #FF6600; background: linear-gradient(180deg, #FFF7ED 0%, white 100%); transform: scale(1.02); box-shadow: 0 10px 40px rgba(255,102,0,0.15); position: relative; z-index: 10; }
        
        .cta-box { background: linear-gradient(135deg, #FF6600, #FF8533); border-radius: 20px; padding: 60px 30px; text-align: center; box-shadow: 0 15px 40px rgba(255,102,0,0.25); }
        .cta-title { font-size: 2.2rem; font-weight: 800; color: white; margin-bottom: 15px; }
        
        .site-footer { background: #1a1a2e; padding: 40px 20px; text-align: center; margin-top: 60px; border-top: 1px solid #334155; }
        .footer-brand { font-size: 1.3rem; font-weight: 800; color: white; margin-bottom: 8px; }
        .footer-text { color: #94A3B8; font-size: 0.9rem; }
        
        .stButton > button { border-radius: 10px !important; font-weight: 600 !important; font-size: 1rem !important; padding: 12px 24px !important; }
        .stButton > button[kind="primary"] { background: linear-gradient(135deg, #FF6600, #FF8533) !important; color: white !important; border: none !important; box-shadow: 0 4px 15px rgba(255,102,0,0.3) !important; }
        
        @media (max-width: 768px) {
            .hero-title, .hero-title-orange { font-size: 2.2rem; line-height: 1.1 !important; }
            .stat-number { font-size: 2rem; }
        }
    </style>
    """, unsafe_allow_html=True)


# ============================================================================
# COMPONENTI UI (Ridotti per brevità, la logica è nel MAIN)
# ============================================================================
def render_navbar():
    c1, c2 = st.columns([3, 1])
    with c1: st.markdown("### 🏗️ **POS FACILE**")
    with c2:
        if st.button("🔐 Accedi", key="nav_login"):
            st.session_state.show_auth = True
            st.session_state.auth_mode = 'login'
            st.rerun()
    st.markdown("---")

def render_hero():
    st.markdown("<div class='hero-container'>", unsafe_allow_html=True)
    st.markdown('<span class="hero-badge">🚀 Provalo Gratis • Il primo POS è Omaggio</span>', unsafe_allow_html=True)
    st.markdown('<h1 class="hero-title">Basta ore su Word.</h1>', unsafe_allow_html=True)
    st.markdown('<h1 class="hero-title-orange">POS conforme in 10 minuti.</h1>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">Genera Piani Operativi di Sicurezza conformi al D.Lgs 81/08 con l\'AI.</p>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        if st.button("🚀 INIZIA GRATIS ORA", type="primary", use_container_width=True, key="hero_cta"):
            st.session_state.show_auth = True
            st.session_state.auth_mode = 'register'
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

def render_stats_bar():
    st.markdown("""
    <div class="stats-bar"><div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 20px;">
        <div class="stat-item"><span class="stat-icon">⏱️</span><p class="stat-number">10 min</p><p class="stat-label">Invece di 4 ore</p></div>
        <div class="stat-item"><span class="stat-icon">📋</span><p class="stat-number">100%</p><p class="stat-label">Conforme 81/08</p></div>
        <div class="stat-item"><span class="stat-icon">🧠</span><p class="stat-number">AI</p><p class="stat-label">Analisi Rischi</p></div>
    </div></div>""", unsafe_allow_html=True)

def render_features():
    st.markdown("<br><h2 style='text-align: center; color: #1a1a2e; font-weight: 800;'>Funzionalità Principali</h2><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown('<div class="feature-card"><div class="feature-icon">🧠</div><div class="feature-title">AI Avanzata</div><div class="feature-text">Analisi rischi specifica per cantiere.</div></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="feature-card"><div class="feature-icon">⚡</div><div class="feature-title">Velocissimo</div><div class="feature-text">Crea POS completi in pochi minuti.</div></div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="feature-card"><div class="feature-icon">✅</div><div class="feature-title">Conforme</div><div class="feature-text">Rispetta D.Lgs 81/08 e Allegato XV.</div></div>', unsafe_allow_html=True)

def render_pricing():
    st.markdown("<br><h2 style='text-align: center; color: #1a1a2e; font-weight: 800;'>Prezzi</h2><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: 
        st.markdown('<div class="price-card"><div class="price-name">FREE</div><div class="price-amount">€0</div><div class="price-feature">✅ 1 POS Gratuito</div></div>', unsafe_allow_html=True)
        st.button("Prova Free", key="p_free", use_container_width=True)
    with c2: 
        st.markdown('<div class="price-card featured"><div class="price-badge">POPOLARE</div><div class="price-name">PROFESSIONAL</div><div class="price-amount">€24<span>,99</span></div><div class="price-feature">✅ 10 POS/mese</div></div>', unsafe_allow_html=True)
        st.button("Scegli Pro", key="p_pro", type="primary", use_container_width=True)
    with c3: 
        st.markdown('<div class="price-card"><div class="price-name">UNLIMITED</div><div class="price-amount">€49<span>,99</span></div><div class="price-feature">✅ Illimitati</div></div>', unsafe_allow_html=True)
        st.button("Scegli Unlimited", key="p_unl", use_container_width=True)

def render_footer():
    st.markdown('<div class="site-footer"><div class="footer-brand">🏗️ POS FACILE</div><div class="footer-text">© 2026 POS FACILE</div></div>', unsafe_allow_html=True)


# ============================================================================
# MAIN - IL CUORE DEL SISTEMA
# ============================================================================
def main():
    inject_css()
    
    # 1. INIZIALIZZA STATO
    auth_manager.init_auth_state()
    
    # 2. CONTROLLA URL (QUESTO È IL FIX FONDAMENTALE)
    # Controlliamo il parametro 'nav' PRIMA di ogni altra cosa.
    # Se è 'update_password', forziamo la modalità auth, INDIPENDENTEMENTE dallo stato del login.
    query_nav = st.query_params.get("nav")
    
    if query_nav == "update_password":
        st.session_state.show_auth = True
        st.session_state.auth_mode = 'update_password'
    elif query_nav == "login":
        st.session_state.show_auth = True
        st.session_state.auth_mode = 'login'
        # Messaggio opzionale solo se non già loggati
        if not auth_manager.is_authenticated():
            st.success("✅ Email confermata! Effettua il login.")
            st.query_params.clear() # Pulisci URL

    # 3. GESTIONE CALLBACK (Recupero sessione da link email)
    if auth_manager.handle_auth_callback():
        st.rerun()
    
    # 4. ROUTING PRINCIPALE
    if auth_manager.is_authenticated():
        # --- UTENTE LOGGATO ---
        # Sidebar fissa
        st.markdown("""<style>[data-testid="stSidebar"] { min-width: 300px; max-width: 300px; }</style>""", unsafe_allow_html=True)
        
        render_subscription_sidebar()
        
        with st.sidebar:
            st.write(f"👤 {st.session_state.user.email}")
            auth_manager.render_user_menu() # Logout button here
        
        try:
            from app import main as run_pos_app
            run_pos_app()
        except ImportError:
            st.error("❌ File app.py non trovato.")
    
    elif st.session_state.get('show_auth', False) or st.session_state.auth_mode == 'update_password':
        # --- PAGINA DI AUTH (Login / Register / Reset / Update Pwd) ---
        # Questo blocco ora scatta SICURAMENTE se nav=update_password
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("← Home", key="back_home"):
                st.session_state.show_auth = False
                st.session_state.auth_mode = 'login'
                st.query_params.clear()
                st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        with col2:
            auth_manager.render_auth_page()
    
    else:
        # --- LANDING PAGE ---
        render_navbar()
        render_hero()
        render_stats_bar() 
        render_mockup()
        render_features()
        render_pricing()
        render_footer()


if __name__ == "__main__":
    main()
