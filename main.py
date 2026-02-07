# -*- coding: utf-8 -*-
"""
POS FACILE - Landing Page V10 FINAL
Fix: Accesso risolto (rimosso menu duplicato)
"""

import streamlit as st

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(
    page_title="POS FACILE | Generatore POS con AI",
    page_icon="🏗️",
    layout="wide"
)

# --- IMPORT MODULI ---
try:
    from auth_manager import init_auth_state, is_authenticated, render_auth_page, render_user_menu
    from license_manager import render_subscription_sidebar
    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False
    def init_auth_state(): 
        if 'show_auth' not in st.session_state:
            st.session_state.show_auth = False
        if 'auth_mode' not in st.session_state:
            st.session_state.auth_mode = 'register'
    def is_authenticated(): return False
    def render_auth_page(): 
        st.warning("⚠️ Modulo Auth non trovato.")
    def render_user_menu(): pass
    def render_subscription_sidebar(): pass


def go_to_register():
    """Naviga alla pagina di registrazione"""
    st.session_state.show_auth = True
    st.session_state.auth_mode = 'register'


def inject_css():
    """CSS pulito e professionale"""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif !important;
        }
        
        #MainMenu, footer, header {visibility: hidden;}
        .stDeployButton {display: none;}
        
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 2rem !important;
            max-width: 1100px !important;
        }

        /* ===== HERO SECTION ===== */
        .hero-container {
            text-align: center;
            padding-bottom: 2rem;
        }

        .hero-badge {
            display: inline-block;
            background: #FFF7ED;
            color: #EA580C;
            padding: 8px 20px;
            border-radius: 50px;
            font-size: 0.9rem;
            font-weight: 600;
            border: 1px solid #FDBA74;
            margin-bottom: 1.5rem;
        }
        
        .hero-title {
            font-size: 3.5rem;
            font-weight: 900;
            color: #1a1a2e;
            line-height: 1.0 !important;
            margin-bottom: 0 !important;
            text-align: center;
            letter-spacing: -1px;
        }
        
        .hero-title-orange {
            font-size: 3.5rem;
            font-weight: 900;
            color: #FF6600;
            line-height: 1.0 !important;
            margin-top: 5px !important;
            margin-bottom: 1.5rem !important;
            text-align: center;
            letter-spacing: -1px;
        }
        
        .hero-subtitle {
            font-size: 1.25rem;
            color: #64748B;
            text-align: center !important;
            max-width: 700px;
            margin: 0 auto 2.5rem auto !important;
            line-height: 1.6;
            display: block;
        }

        /* ===== STATS BAR ===== */
        .stats-bar {
            background-color: #1a1a2e;
            padding: 3rem 1rem;
            border-radius: 16px;
            margin: 3rem 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        }
        
        .stat-item {
            text-align: center;
            padding: 10px;
        }
        
        .stat-icon {
            font-size: 2.5rem;
            margin-bottom: 10px;
            display: block;
        }
        
        .stat-number {
            font-size: 3rem;
            font-weight: 800;
            color: #FF6600;
            margin: 0;
            line-height: 1;
        }
        
        .stat-label {
            font-size: 0.9rem;
            color: #E2E8F0;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            font-weight: 600;
            margin-top: 10px;
        }

        /* ===== MOCKUP ===== */
        .mockup-container {
            max-width: 900px;
            margin: 0 auto 40px auto;
            background: #1a1a2e;
            border-radius: 12px;
            padding: 12px;
            box-shadow: 0 25px 50px rgba(0,0,0,0.2);
        }
        
        .mockup-screen {
            background: white;
            border-radius: 8px;
            overflow: hidden;
        }
        
        .mockup-header {
            background: linear-gradient(90deg, #FF6600, #FF8533);
            padding: 15px 20px;
            color: white;
            text-align: left;
        }
        
        .mockup-body {
            padding: 30px;
            text-align: left;
        }
        
        .mockup-row {
            display: flex;
            gap: 15px;
            margin-bottom: 15px;
        }
        
        .mockup-field {
            flex: 1;
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 6px;
            padding: 10px 15px;
            font-size: 0.9rem;
            color: #475569;
        }

        /* ===== SECTIONS GENERIC ===== */
        .section-tag {
            display: inline-block;
            background: #FFF7ED;
            color: #EA580C;
            padding: 8px 18px;
            border-radius: 25px;
            font-size: 0.85rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .section-title {
            font-size: 2.3rem;
            font-weight: 800;
            color: #1a1a2e;
            text-align: center;
            margin: 15px 0 10px 0;
        }
        
        .section-subtitle {
            font-size: 1.1rem;
            color: #64748B;
            text-align: center !important;
            margin: 0 auto 40px auto !important;
            max-width: 600px;
            display: block;
        }

        /* ===== CARDS ===== */
        .feature-card {
            background: white;
            border: 1px solid #E2E8F0;
            border-radius: 16px;
            padding: 30px 25px;
            text-align: center;
            height: 100%;
            transition: all 0.3s;
        }
        
        .feature-card:hover {
            border-color: #FF6600;
            box-shadow: 0 10px 30px rgba(0,0,0,0.08);
            transform: translateY(-3px);
        }
        
        .feature-icon {
            font-size: 2.8rem;
            margin-bottom: 15px;
        }
        
        .feature-title {
            font-size: 1.2rem;
            font-weight: 700;
            color: #1a1a2e;
            margin-bottom: 10px;
        }
        
        .feature-text {
            font-size: 0.95rem;
            color: #64748B;
            line-height: 1.6;
        }

        /* ===== REVIEWS (NUOVO DESIGN CON FOTO) ===== */
        .review-card {
            background: white;
            border: 1px solid #E2E8F0;
            border-radius: 16px;
            padding: 25px;
            height: 100%;
            text-align: left;
        }
        
        .review-header {
            display: flex;
            align-items: center;
            margin-bottom: 15px;
            border-bottom: 1px solid #F1F5F9;
            padding-bottom: 15px;
        }
        
        .review-avatar {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            object-fit: cover;
            margin-right: 15px;
            border: 2px solid #FF6600;
        }
        
        .review-info {
            display: flex;
            flex-direction: column;
        }
        
        .review-author {
            font-weight: 700;
            color: #1a1a2e;
            font-size: 1rem;
        }
        
        .review-role {
            color: #FF6600;
            font-size: 0.85rem;
            font-weight: 600;
        }
        
        .review-stars {
            color: #F59E0B;
            font-size: 1.1rem;
            margin-bottom: 10px;
        }
        
        .review-text {
            font-size: 0.95rem;
            color: #475569;
            line-height: 1.6;
            font-style: italic;
        }

        /* ===== PRICING ===== */
        .price-card {
            background: white;
            border: 2px solid #E2E8F0;
            border-radius: 20px;
            padding: 30px 25px;
            text-align: center;
            height: 100%;
        }
        
        .price-card.featured {
            border-color: #FF6600;
            background: linear-gradient(180deg, #FFF7ED 0%, white 100%);
            transform: scale(1.02);
            box-shadow: 0 10px 40px rgba(255,102,0,0.15);
            position: relative;
            z-index: 10;
        }
        
        .price-badge {
            background: linear-gradient(135deg, #FF6600, #FF8533);
            color: white;
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            display: inline-block;
            margin-bottom: 12px;
        }
        
        .price-name {
            font-size: 0.95rem;
            font-weight: 700;
            color: #64748B;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 8px;
        }
        
        .price-amount {
            font-size: 2.8rem;
            font-weight: 900;
            color: #1a1a2e;
            line-height: 1;
        }
        
        .price-amount span {
            font-size: 1rem;
            color: #94A3B8;
            font-weight: 500;
        }
        
        .price-period {
            color: #94A3B8;
            font-size: 0.95rem;
            margin-bottom: 20px;
        }
        
        .price-feature {
            padding: 10px 0;
            color: #475569;
            font-size: 0.9rem;
            border-bottom: 1px solid #F1F5F9;
            text-align: left;
        }
        
        .price-feature:last-child {
            border-bottom: none;
        }
        
        .price-feature.no {
            color: #CBD5E1;
        }

        /* ===== CTA ===== */
        .cta-box {
            background: linear-gradient(135deg, #FF6600, #FF8533);
            border-radius: 20px;
            padding: 60px 30px;
            text-align: center;
            box-shadow: 0 15px 40px rgba(255,102,0,0.25);
        }
        
        .cta-title {
            font-size: 2.2rem;
            font-weight: 800;
            color: white;
            margin-bottom: 15px;
        }
        
        .cta-subtitle {
            font-size: 1.2rem;
            color: rgba(255,255,255,0.95);
            margin-bottom: 30px;
        }

        /* ===== FOOTER ===== */
        .site-footer {
            background: #1a1a2e;
            padding: 40px 20px;
            text-align: center;
            margin-top: 60px;
            border-top: 1px solid #334155;
        }
        
        .footer-brand {
            font-size: 1.3rem;
            font-weight: 800;
            color: white;
            margin-bottom: 8px;
        }
        
        .footer-text {
            color: #94A3B8;
            font-size: 0.9rem;
        }

        /* ===== BUTTONS ===== */
        .stButton > button {
            border-radius: 10px !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
            padding: 12px 24px !important;
        }
        
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #FF6600, #FF8533) !important;
            color: white !important;
            border: none !important;
            box-shadow: 0 4px 15px rgba(255,102,0,0.3) !important;
        }
        
        .stButton > button[kind="primary"]:hover {
            box-shadow: 0 6px 20px rgba(255,102,0,0.4) !important;
            transform: translateY(-1px);
        }

        /* ===== RESPONSIVE ===== */
        @media (max-width: 768px) {
            .hero-title, .hero-title-orange { font-size: 2.2rem; line-height: 1.1 !important; }
            .section-title { font-size: 1.8rem; }
            .stat-number { font-size: 2rem; }
            .stat-icon { font-size: 2rem; }
            .price-card.featured { transform: scale(1); }
        }
    </style>
    """, unsafe_allow_html=True)


# ============================================================================
# COMPONENTI
# ============================================================================

def render_navbar():
    """Navbar semplice"""
    col1, col2, col3 = st.columns([3, 2, 1])
    with col1:
        st.markdown("### 🏗️ **POS FACILE**")
    with col3:
        if st.button("🔐 Accedi", key="nav_login"):
            st.session_state.show_auth = True
            st.session_state.auth_mode = 'login'
            st.rerun()
    
    st.markdown("---")


def render_hero():
    """Hero Section"""
    st.markdown("<div class='hero-container'>", unsafe_allow_html=True)
    
    # Badge centrato
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div style="text-align: center;"><span class="hero-badge">🚀 Provalo Gratis • Il primo POS è Omaggio</span></div>', unsafe_allow_html=True)
    
    # Titoli
    st.markdown('<h1 class="hero-title">Basta ore su Word.</h1>', unsafe_allow_html=True)
    st.markdown('<h1 class="hero-title-orange">POS conforme in 10 minuti.</h1>', unsafe_allow_html=True)
    
    # Sottotitolo (Centrato via CSS)
    st.markdown('<p class="hero-subtitle">Sei un geometra, un ingegnere o un consulente sicurezza? POS Facile genera Piani Operativi di Sicurezza conformi al D.Lgs 81/08 con l\'AI. Tu selezioni le lavorazioni, l\'app calcola rischi, DPI e misure. PDF pronto per il CSE.</p>', unsafe_allow_html=True)
    
    # CTA
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚀 INIZIA GRATIS ORA", type="primary", use_container_width=True, key="hero_cta"):
            go_to_register()
            st.rerun()
            
    st.markdown("</div>", unsafe_allow_html=True)


def render_stats_bar():
    """Stats bar con icone e numeri"""
    st.markdown("""
    <div class="stats-bar">
        <div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 20px;">
            <div class="stat-item">
                <span class="stat-icon">⏱️</span>
                <p class="stat-number">10 min</p>
                <p class="stat-label">Invece di 4 ore</p>
            </div>
            <div class="stat-item">
                <span class="stat-icon">📋</span>
                <p class="stat-number">100%</p>
                <p class="stat-label">Conforme D.Lgs 81/08</p>
            </div>
            <div class="stat-item">
                <span class="stat-icon">🔧</span>
                <p class="stat-number">12+</p>
                <p class="stat-label">Categorie lavorazioni</p>
            </div>
            <div class="stat-item">
                <span class="stat-icon">🧠</span>
                <p class="stat-number">AI</p>
                <p class="stat-label">Analisi rischi</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_mockup():
    """Mockup Applicazione"""
    st.markdown("""
    <div class="mockup-container">
        <div class="mockup-screen">
            <div class="mockup-header">
                <div style="font-weight: 700; font-size: 1.1rem;">🏗️ POS FACILE - Nuovo POS</div>
            </div>
            <div class="mockup-body">
                <div class="mockup-row">
                    <div class="mockup-field">📋 Cliente: Edilizia Rossi S.r.l.</div>
                    <div class="mockup-field">📍 Cantiere: Via Roma 15, Macerata</div>
                </div>
                <div class="mockup-row">
                    <div class="mockup-field">👷 Datore di Lavoro: Mario Rossi</div>
                    <div class="mockup-field">📅 Durata prevista: 45 giorni</div>
                </div>
                <div class="mockup-row">
                    <div class="mockup-field" style="flex: 2;">🔧 Lavorazioni: Demolizioni, Scavi, Opere murarie, Impianti elettrici → Rischi, DPI e misure calcolati</div>
                </div>
                <div style="background: #FF6600; color: white; display: inline-block; padding: 10px 20px; border-radius: 6px; font-weight: 600; margin-top: 10px; font-size: 0.9rem;">✨ Genera POS con AI</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_trust():
    """Trust badges (Optional - teniamo semplice)"""
    pass


def render_features():
    """Features"""
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div style="text-align: center;"><span class="section-tag">✨ FUNZIONALITÀ</span></div>', unsafe_allow_html=True)
    
    st.markdown('<h2 class="section-title">Perché i professionisti scelgono POS FACILE</h2>', unsafe_allow_html=True)
    st.markdown('<p class="section-subtitle">Meno tempo sulla burocrazia, più tempo per i tuoi clienti.</p>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🧠</div>
            <div class="feature-title">AI che conosce il D.Lgs 81/08</div>
            <div class="feature-text">Seleziona le lavorazioni e l'AI genera rischi specifici, DPI con norme EN, misure di prevenzione e valori limite di esposizione.</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">⚡</div>
            <div class="feature-title">Da 4 ore a 10 minuti</div>
            <div class="feature-text">Basta copiare da vecchi template Word. Compila una volta i dati dell'impresa, li ritrovi per ogni cantiere successivo.</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">✅</div>
            <div class="feature-title">Conforme Allegato XV</div>
            <div class="feature-text">Struttura completa: premessa, organigramma, valutazione rischi, procedure emergenza, cronoprogramma. Pronto per il CSE e per l'ASL.</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    c4, c5, c6 = st.columns(3)
    with c4:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📎</div>
            <div class="feature-title">PDF Unico con Allegati</div>
            <div class="feature-text">Carica DURC, Visura, Attestati e Idoneità. Li uniamo al POS in un unico PDF pronto per la PEC.</div>
        </div>
        """, unsafe_allow_html=True)
    with c5:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">💾</div>
            <div class="feature-title">Gestisci più imprese</div>
            <div class="feature-text">Salvi l'anagrafica di ogni cliente. Al prossimo cantiere carichi i dati in un click: lavoratori, attrezzature, figure della sicurezza.</div>
        </div>
        """, unsafe_allow_html=True)
    with c6:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">☁️</div>
            <div class="feature-title">Sempre con te in cantiere</div>
            <div class="feature-text">Web app cloud: funziona da PC, tablet e smartphone. Nessuna installazione.</div>
        </div>
        """, unsafe_allow_html=True)


def render_how_it_works():
    """Come funziona"""
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div style="text-align: center;"><span class="section-tag">📋 COME FUNZIONA</span></div>', unsafe_allow_html=True)
    
    st.markdown('<h2 class="section-title">Come funziona</h2>', unsafe_allow_html=True)
    st.markdown('<p class="section-subtitle">Dal primo click al PDF conforme in 4 passaggi.</p>', unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("""
        <div class="feature-card">
            <div style="font-size: 2.5rem; margin-bottom: 10px;">1️⃣</div>
            <div class="feature-title">Dati Impresa</div>
            <div class="feature-text">Inserisci o carica l'anagrafica del cliente.</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="feature-card">
            <div style="font-size: 2.5rem; margin-bottom: 10px;">2️⃣</div>
            <div class="feature-title">Cantiere e Lavorazioni</div>
            <div class="feature-text">Seleziona le lavorazioni previste dal cantiere.</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="feature-card">
            <div style="font-size: 2.5rem; margin-bottom: 10px;">3️⃣</div>
            <div class="feature-title">L'AI Analizza i Rischi</div>
            <div class="feature-text">Rischi, DPI, misure e valori limite generati automaticamente.</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown("""
        <div class="feature-card">
            <div style="font-size: 2.5rem; margin-bottom: 10px;">4️⃣</div>
            <div class="feature-title">Scarica il PDF</div>
            <div class="feature-text">POS completo con allegati. Pronto per firma e invio al CSE.</div>
        </div>
        """, unsafe_allow_html=True)


def render_reviews():
    """Recensioni con Foto"""
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div style="text-align: center;"><span class="section-tag">⭐ TESTIMONIANZE</span></div>', unsafe_allow_html=True)
    
    st.markdown('<h2 class="section-title">Cosa dicono i professionisti</h2>', unsafe_allow_html=True)
    st.markdown('<p class="section-subtitle">Chi redige POS ogni settimana ha scelto POS Facile.</p>', unsafe_allow_html=True)
    
    # Immagini avatar (Unsplash stock photos)
    avatar_marco = "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=faces"
    avatar_laura = "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150&h=150&fit=crop&crop=faces"
    avatar_paolo = "https://images.unsplash.com/photo-1560250097-0b93528c311a?w=150&h=150&fit=crop&crop=faces"

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="review-card">
            <div class="review-header">
                <img src="{avatar_marco}" class="review-avatar">
                <div class="review-info">
                    <div class="review-author">Marco R.</div>
                    <div class="review-role">Geometra libero professionista</div>
                </div>
            </div>
            <div class="review-stars">★★★★★</div>
            <div class="review-text">"Faccio 6-8 POS al mese per le imprese della zona. Prima ci mettevo mezza giornata ciascuno, adesso in 10 minuti ho un documento che il CSE non mi ha mai contestato."</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="review-card">
            <div class="review-header">
                <img src="{avatar_laura}" class="review-avatar">
                <div class="review-info">
                    <div class="review-author">Ing. Laura B.</div>
                    <div class="review-role">CSP/CSE e RSPP</div>
                </div>
            </div>
            <div class="review-stars">★★★★★</div>
            <div class="review-text">"La parte dei rischi specifici con norme EN e valori limite è quello che fa la differenza. Non è il solito template vuoto — qui c'è sostanza tecnica vera."</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="review-card">
            <div class="review-header">
                <img src="{avatar_paolo}" class="review-avatar">
                <div class="review-info">
                    <div class="review-author">Geom. Paolo G.</div>
                    <div class="review-role">Consulente sicurezza cantieri</div>
                </div>
            </div>
            <div class="review-stars">★★★★★</div>
            <div class="review-text">"Gestisco la sicurezza per 12 imprese. Il fatto di salvare le anagrafiche e ricaricarle mi fa risparmiare un'enormità di tempo. Il piano Professional si ripaga al primo POS."</div>
        </div>
        """, unsafe_allow_html=True)


def render_pricing():
    """Prezzi"""
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div style="text-align: center;"><span class="section-tag">💰 PREZZI</span></div>', unsafe_allow_html=True)
    
    st.markdown('<h2 class="section-title">Quanto tempo vuoi risparmiare?</h2>', unsafe_allow_html=True)
    st.markdown('<p class="section-subtitle">Ogni piano si ripaga con un singolo POS rispetto al tempo che risparmi.</p>', unsafe_allow_html=True)
    
    # Pricing cards
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown("""
        <div class="price-card">
            <div class="price-name">FREE</div>
            <div class="price-amount">€0</div>
            <div class="price-period">per sempre</div>
            <div class="price-feature">✅ 1 POS gratuito</div>
            <div class="price-feature">✅ Tutte le lavorazioni</div>
            <div class="price-feature">✅ PDF professionale</div>
            <div class="price-feature no">✗ Salvataggio anagrafiche</div>
            <div class="price-feature no">✗ Supporto prioritario</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Prova Gratis", key="price_free", use_container_width=True):
            go_to_register()
            st.rerun()
    
    with c2:
        st.markdown("""
        <div class="price-card">
            <div class="price-name">STARTER</div>
            <div class="price-amount">€9<span>,99</span></div>
            <div class="price-period">al mese</div>
            <div class="price-feature">✅ <b>3 POS</b> al mese</div>
            <div class="price-feature">✅ Salva anagrafiche</div>
            <div class="price-feature">✅ Storico documenti</div>
            <div class="price-feature">✅ Analisi AI</div>
            <div class="price-feature">✅ Supporto email</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Scegli Starter", key="price_starter", use_container_width=True):
            go_to_register()
            st.rerun()
    
    with c3:
        st.markdown("""
        <div class="price-card featured">
            <div class="price-badge">🔥 PIÙ SCELTO</div>
            <div class="price-name" style="color: #FF6600;">PROFESSIONAL</div>
            <div class="price-amount">€24<span>,99</span></div>
            <div class="price-period">al mese</div>
            <div class="price-feature">✅ <b>10 POS</b> al mese</div>
            <div class="price-feature">✅ <b>AI Avanzata</b></div>
            <div class="price-feature">✅ Magic Writer</div>
            <div class="price-feature">✅ Supporto prioritario</div>
            <div class="price-feature">✅ Anagrafiche illimitate</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🚀 Scegli Professional", key="price_professional", type="primary", use_container_width=True):
            go_to_register()
            st.rerun()
    
    with c4:
        st.markdown("""
        <div class="price-card">
            <div class="price-name">UNLIMITED</div>
            <div class="price-amount">€49<span>,99</span></div>
            <div class="price-period">al mese</div>
            <div class="price-feature">✅ <b>POS Illimitati</b></div>
            <div class="price-feature">✅ Tutto di Professional</div>
            <div class="price-feature">✅ Supporto WhatsApp</div>
            <div class="price-feature">✅ Priorità server</div>
            <div class="price-feature">✅ Nuove funzioni in anteprima</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Scegli Unlimited", key="price_unlimited", use_container_width=True):
            go_to_register()
            st.rerun()


def render_cta():
    """Call to action finale"""
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="cta-box">
        <div class="cta-title">🎁 Prova con un POS reale — è gratis</div>
        <div class="cta-subtitle">Registrati, genera il tuo primo POS su un cantiere vero, e vedi con i tuoi occhi quanto tempo risparmi.</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 REGISTRATI GRATIS", type="primary", use_container_width=True, key="cta_btn"):
            go_to_register()
            st.rerun()


def render_faq():
    """FAQ"""
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div style="text-align: center;"><span class="section-tag">❓ FAQ</span></div>', unsafe_allow_html=True)
    
    st.markdown('<h2 class="section-title">Domande Frequenti</h2>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        with st.expander("📋 Il POS generato è conforme alla normativa?"):
            st.write("**Sì.** Il documento segue fedelmente l'Allegato XV del D.Lgs 81/08 con tutte le sezioni obbligatorie: dati impresa, organigramma sicurezza, valutazione rischi specifici per lavorazione, DPI con norme EN, misure di prevenzione, procedure di emergenza e cronoprogramma.")
        
        with st.expander("👷 Posso usarlo per gestire più imprese clienti?"):
            st.write("**Sì.** Con i piani a pagamento puoi salvare le anagrafiche di più imprese (lavoratori, attrezzature, figure della sicurezza) e ricaricarle in un click quando crei un nuovo POS per lo stesso cliente.")
        
        with st.expander("🎁 Come funziona il POS gratuito?"):
            st.write("Registrandoti ottieni **1 POS gratuito** completo, con tutte le funzionalità. Generalo su un cantiere reale per valutare la qualità del documento.")
        
        with st.expander("🤖 Come funziona l'analisi AI dei rischi?"):
            st.write("L'AI analizza le lavorazioni selezionate e la descrizione del cantiere per generare rischi specifici, misure di prevenzione e DPI. Tu mantieni il **controllo finale** e puoi modificare tutto prima di generare il PDF.")
        
        with st.expander("📎 Posso allegare documenti al POS?"):
            st.write("**Sì.** Puoi caricare DURC, Visura Camerale, Attestati di Formazione, Idoneità Sanitarie e Schede SDS. Vengono uniti al POS in un **unico PDF** pronto per l'invio via PEC al Coordinatore.")
        
        with st.expander("💳 Come funzionano i pagamenti?"):
            st.write("Pagamenti sicuri con **Lemon Squeezy**. Ricevi una licenza via email da inserire nell'app. Puoi annullare in qualsiasi momento.")


def render_footer():
    """Footer"""
    st.markdown("""
    <div class="site-footer">
        <div class="footer-brand">🏗️ POS FACILE</div>
        <div class="footer-text">Lo strumento dei professionisti della sicurezza in cantiere.</div>
        <div class="footer-text">© 2026 POS FACILE. Tutti i diritti riservati.</div>
    </div>
    """, unsafe_allow_html=True)


# ============================================================================
# MAIN
# ============================================================================
def main():
    inject_css()
    init_auth_state()
    
    if 'auth_mode' not in st.session_state:
        st.session_state.auth_mode = 'register'
    
    if is_authenticated():
        # CSS per sidebar SEMPRE FISSA (non chiudibile)
        st.markdown("""
        <style>
            /* Sidebar SEMPRE visibile e fissa */
            [data-testid="stSidebar"] {
                display: block !important;
                width: 300px !important;
                min-width: 300px !important;
                max-width: 300px !important;
                transform: none !important;
                position: relative !important;
                visibility: visible !important;
            }
            
            [data-testid="stSidebar"][aria-expanded="false"] {
                display: block !important;
                width: 300px !important;
                min-width: 300px !important;
                margin-left: 0 !important;
                transform: none !important;
                visibility: visible !important;
            }
            
            section[data-testid="stSidebar"] > div {
                width: 300px !important;
            }
            
            /* NASCONDI SOLO il pulsante freccia di chiusura (primo bottone della sidebar) */
            [data-testid="collapsedControl"],
            [data-testid="stSidebarCollapseButton"] {
                display: none !important;
            }
            
            /* Rimuovi lo spazio del pulsante chiusura */
            [data-testid="stSidebarUserContent"] {
                padding-top: 1rem !important;
            }
            
            /* I pulsanti di navigazione nella sidebar devono essere VISIBILI */
            [data-testid="stSidebar"] .stButton > button {
                display: flex !important;
                visibility: visible !important;
                width: 100% !important;
            }
        </style>
        """, unsafe_allow_html=True)
        
        # Gestione errori license_manager
        try:
            render_subscription_sidebar()
        except Exception as e:
            # Se c'è un errore, mostra sidebar minimale
            with st.sidebar:
                st.markdown("### 💎 Abbonamento")
                st.info("Piano: **Free**")
                st.caption("1 POS disponibile")
        
        try:
            from app import main as run_pos_app
            run_pos_app()
        except ImportError:
            st.error("❌ File app.py non trovato.")
    
    elif st.session_state.get('show_auth', False):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("← Torna alla Home", key="back_home"):
                st.session_state.show_auth = False
                st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        with col2:
            if AUTH_AVAILABLE:
                try:
                    render_auth_page(default_mode=st.session_state.auth_mode)
                except TypeError:
                    render_auth_page()
            else:
                st.info("📝 **Pagina di Registrazione**")
                st.write("Il modulo di autenticazione non è ancora configurato.")
    
    else:
        render_navbar()
        render_hero()
        render_stats_bar() 
        render_mockup()
        render_features()
        render_how_it_works()
        render_reviews()
        render_pricing()
        render_cta()
        render_faq()
        render_footer()


if __name__ == "__main__":
    main()
