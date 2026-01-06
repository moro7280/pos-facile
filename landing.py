# -*- coding: utf-8 -*-
"""
POS FACILE - Landing Page
Pagina di presentazione del servizio
"""

import streamlit as st


def render_landing_page():
    """Renderizza la landing page completa"""
    
    # CSS Custom per landing page
    st.markdown("""
    <style>
        /* Hero Section */
        .hero {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            color: white;
            padding: 4rem 2rem;
            border-radius: 20px;
            text-align: center;
            margin-bottom: 3rem;
        }
        .hero h1 {
            font-size: 3.5rem;
            margin-bottom: 1rem;
            color: #FF6600;
        }
        .hero p {
            font-size: 1.4rem;
            color: #B0BEC5;
            margin-bottom: 2rem;
        }
        .hero-btn {
            display: inline-block;
            padding: 16px 40px;
            background: #FF6600;
            color: white !important;
            text-decoration: none;
            border-radius: 30px;
            font-size: 1.2rem;
            font-weight: bold;
            transition: all 0.3s;
            margin: 10px;
        }
        .hero-btn:hover {
            background: #E55A00;
            transform: scale(1.05);
        }
        .hero-btn.secondary {
            background: transparent;
            border: 2px solid #FF6600;
        }
        
        /* Features */
        .feature-card {
            background: white;
            padding: 2rem;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            text-align: center;
            height: 100%;
            transition: transform 0.3s;
        }
        .feature-card:hover {
            transform: translateY(-5px);
        }
        .feature-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        .feature-title {
            font-size: 1.3rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
            color: #1a1a2e;
        }
        .feature-desc {
            color: #666;
            font-size: 1rem;
        }
        
        /* Stats */
        .stats-container {
            display: flex;
            justify-content: center;
            gap: 4rem;
            margin: 3rem 0;
            flex-wrap: wrap;
        }
        .stat-item {
            text-align: center;
        }
        .stat-number {
            font-size: 3rem;
            font-weight: bold;
            color: #FF6600;
        }
        .stat-label {
            color: #666;
            font-size: 1.1rem;
        }
        
        /* Testimonials */
        .testimonial {
            background: #f8f9fa;
            padding: 2rem;
            border-radius: 16px;
            margin: 1rem 0;
            border-left: 4px solid #FF6600;
        }
        .testimonial-text {
            font-style: italic;
            font-size: 1.1rem;
            color: #333;
            margin-bottom: 1rem;
        }
        .testimonial-author {
            font-weight: bold;
            color: #666;
        }
        
        /* CTA Section */
        .cta-section {
            background: linear-gradient(135deg, #FF6600 0%, #ff8533 100%);
            color: white;
            padding: 4rem 2rem;
            border-radius: 20px;
            text-align: center;
            margin: 3rem 0;
        }
        .cta-section h2 {
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }
        .cta-section p {
            font-size: 1.2rem;
            margin-bottom: 2rem;
            opacity: 0.9;
        }
        .cta-btn {
            display: inline-block;
            padding: 16px 40px;
            background: white;
            color: #FF6600 !important;
            text-decoration: none;
            border-radius: 30px;
            font-size: 1.2rem;
            font-weight: bold;
            transition: all 0.3s;
        }
        .cta-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        /* Footer */
        .footer {
            text-align: center;
            padding: 2rem;
            color: #666;
            border-top: 1px solid #eee;
            margin-top: 3rem;
        }
        
        /* Pricing Cards - Importato da license_manager */
        .pricing-container {
            display: flex;
            gap: 20px;
            justify-content: center;
            flex-wrap: wrap;
            margin: 2rem 0;
        }
        .pricing-card {
            background: white;
            border-radius: 16px;
            padding: 2rem;
            width: 260px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s;
        }
        .pricing-card:hover {
            transform: translateY(-5px);
        }
        .pricing-card.featured {
            border: 3px solid #FF6600;
            transform: scale(1.05);
        }
        .pricing-title {
            font-size: 1.4rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        .pricing-price {
            font-size: 2.2rem;
            font-weight: bold;
            color: #FF6600;
            margin: 1rem 0;
        }
        .pricing-price span {
            font-size: 1rem;
            color: #666;
        }
        .pricing-features {
            text-align: left;
            margin: 1.5rem 0;
            padding-left: 0;
        }
        .pricing-features li {
            margin: 0.5rem 0;
            list-style: none;
            font-size: 0.95rem;
        }
        .pricing-features li::before {
            content: "✅ ";
        }
        .pricing-btn {
            display: inline-block;
            width: 100%;
            padding: 12px 24px;
            background: #FF6600;
            color: white !important;
            text-decoration: none;
            border-radius: 8px;
            font-weight: bold;
            transition: background 0.3s;
        }
        .pricing-btn:hover {
            background: #E55A00;
        }
        .pricing-btn.outline {
            background: white;
            color: #FF6600 !important;
            border: 2px solid #FF6600;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # ==================== HERO SECTION ====================
    st.markdown("""
    <div class="hero">
        <h1>🏗️ POS FACILE</h1>
        <p>Il Piano Operativo di Sicurezza perfetto in 5 minuti.<br>
        Conforme al D.Lgs 81/08 • Generato con AI • Pronto per l'ASL</p>
        <a href="#pricing" class="hero-btn">🎁 Prova Gratis</a>
        <a href="#features" class="hero-btn secondary">Scopri di più</a>
    </div>
    """, unsafe_allow_html=True)
    
    # ==================== STATS ====================
    st.markdown("""
    <div class="stats-container">
        <div class="stat-item">
            <div class="stat-number">100%</div>
            <div class="stat-label">Conforme D.Lgs 81/08</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">5 min</div>
            <div class="stat-label">Tempo medio generazione</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">50+</div>
            <div class="stat-label">Lavorazioni incluse</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">AI</div>
            <div class="stat-label">Analisi rischi automatica</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ==================== FEATURES ====================
    st.markdown("<a name='features'></a>", unsafe_allow_html=True)
    st.markdown("## ✨ Perché POS FACILE?")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">⚡</div>
            <div class="feature-title">Veloce</div>
            <div class="feature-desc">Genera un POS completo in meno di 5 minuti. Niente più ore a compilare documenti.</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <div class="feature-title">Intelligente</div>
            <div class="feature-desc">L'AI analizza la descrizione lavori e identifica automaticamente rischi e misure di prevenzione.</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">✅</div>
            <div class="feature-title">Conforme</div>
            <div class="feature-desc">100% conforme all'Allegato XV del D.Lgs 81/08. Pronto per ispezioni ASL.</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col4, col5, col6 = st.columns(3)
    
    with col4:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📋</div>
            <div class="feature-title">Completo</div>
            <div class="feature-desc">Include tutte le sezioni richieste: rischi, DPI, emergenze, firme, cronoprogramma e allegati.</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">💾</div>
            <div class="feature-title">Salva i dati</div>
            <div class="feature-desc">Le anagrafiche della tua impresa vengono salvate. Non dovrai più reinserirle.</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col6:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📎</div>
            <div class="feature-title">Allegati integrati</div>
            <div class="feature-desc">Carica DURC, visure e attestati. Li uniamo in un unico PDF pronto per la PEC.</div>
        </div>
        """, unsafe_allow_html=True)
    
    # ==================== COME FUNZIONA ====================
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("## 🎯 Come funziona")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <div style="font-size: 3rem;">1️⃣</div>
            <h4>Registrati gratis</h4>
            <p style="color: #666;">Crea il tuo account in 30 secondi</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <div style="font-size: 3rem;">2️⃣</div>
            <h4>Inserisci i dati</h4>
            <p style="color: #666;">Compila i dati dell'impresa e del cantiere</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <div style="font-size: 3rem;">3️⃣</div>
            <h4>L'AI fa il resto</h4>
            <p style="color: #666;">Analisi rischi e descrizioni automatiche</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <div style="font-size: 3rem;">4️⃣</div>
            <h4>Scarica il PDF</h4>
            <p style="color: #666;">POS professionale pronto all'uso</p>
        </div>
        """, unsafe_allow_html=True)
    
    # ==================== PRICING ====================
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<a name='pricing'></a>", unsafe_allow_html=True)
    st.markdown("## 💰 Piani e Prezzi")
    st.markdown("<p style='text-align: center; color: #666; font-size: 1.1rem;'>Scegli il piano più adatto alle tue esigenze</p>", unsafe_allow_html=True)
    
    # Recupera checkout URLs
    checkout_starter = st.secrets.get("CHECKOUT_STARTER", "#")
    checkout_professional = st.secrets.get("CHECKOUT_PROFESSIONAL", "#")
    checkout_unlimited = st.secrets.get("CHECKOUT_UNLIMITED", "#")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="pricing-card">
            <div class="pricing-title">🆓 Free</div>
            <div class="pricing-price">€0</div>
            <ul class="pricing-features">
                <li>1 POS gratuito</li>
                <li>Tutte le lavorazioni</li>
                <li>PDF professionale</li>
                <li>Analisi AI base</li>
            </ul>
            <a href="#" class="pricing-btn outline">Inizia gratis</a>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="pricing-card">
            <div class="pricing-title">⭐ Starter</div>
            <div class="pricing-price">€9,99<span>/mese</span></div>
            <ul class="pricing-features">
                <li>3 POS al mese</li>
                <li>Salva anagrafiche</li>
                <li>Storico documenti</li>
                <li>Supporto email</li>
            </ul>
            <a href="{checkout_starter}" target="_blank" class="pricing-btn">Acquista</a>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="pricing-card featured">
            <div style="background: #FF6600; color: white; padding: 5px 15px; border-radius: 20px; font-size: 11px; margin-bottom: 10px; display: inline-block;">⭐ PIÙ SCELTO</div>
            <div class="pricing-title">💎 Professional</div>
            <div class="pricing-price">€24,99<span>/mese</span></div>
            <ul class="pricing-features">
                <li>10 POS al mese</li>
                <li>AI avanzata</li>
                <li>Magic Writer</li>
                <li>Supporto prioritario</li>
            </ul>
            <a href="{checkout_professional}" target="_blank" class="pricing-btn">Acquista</a>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="pricing-card">
            <div class="pricing-title">🚀 Unlimited</div>
            <div class="pricing-price">€49,99<span>/mese</span></div>
            <ul class="pricing-features">
                <li>POS illimitati</li>
                <li>Tutto di Professional</li>
                <li>Supporto WhatsApp</li>
                <li>Priorità server</li>
            </ul>
            <a href="{checkout_unlimited}" target="_blank" class="pricing-btn">Acquista</a>
        </div>
        """, unsafe_allow_html=True)
    
    # ==================== TESTIMONIALS ====================
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("## 💬 Cosa dicono i nostri utenti")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="testimonial">
            <div class="testimonial-text">"Finalmente un software che mi fa risparmiare tempo! Prima passavo ore a compilare il POS, ora in 10 minuti ho tutto pronto."</div>
            <div class="testimonial-author">— Marco R., Geometra</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="testimonial">
            <div class="testimonial-text">"L'analisi AI dei rischi è impressionante. Identifica cose che a volte mi sfuggono. Strumento indispensabile."</div>
            <div class="testimonial-author">— Laura B., RSPP</div>
        </div>
        """, unsafe_allow_html=True)
    
    # ==================== CTA FINALE ====================
    st.markdown("""
    <div class="cta-section">
        <h2>🎁 Prova POS FACILE Gratis</h2>
        <p>Genera il tuo primo POS gratuitamente. Nessuna carta di credito richiesta.</p>
        <a href="#" class="cta-btn">Inizia ora →</a>
    </div>
    """, unsafe_allow_html=True)
    
    # ==================== FAQ ====================
    st.markdown("## ❓ Domande Frequenti")
    
    with st.expander("Il POS generato è conforme alla normativa?"):
        st.write("Sì, il documento è conforme al 100% all'Allegato XV del D.Lgs 81/08. Include tutte le sezioni obbligatorie: identificazione impresa e cantiere, valutazione rischi, DPI, misure di prevenzione, procedure emergenza, firme e allegati.")
    
    with st.expander("Posso modificare il POS dopo averlo generato?"):
        st.write("Il POS viene generato in formato PDF. Se hai bisogno di modifiche, puoi rigenerarlo con i dati aggiornati. Con i piani a pagamento puoi salvare le anagrafiche per velocizzare il processo.")
    
    with st.expander("Come funziona l'analisi AI?"):
        st.write("L'intelligenza artificiale analizza la descrizione dei lavori e identifica automaticamente le lavorazioni coinvolte, i rischi specifici e suggerisce le misure di prevenzione appropriate. Puoi sempre rivedere e modificare i suggerimenti.")
    
    with st.expander("Posso allegare documenti al POS?"):
        st.write("Sì! Puoi caricare DURC, visura camerale, attestati di formazione e altri documenti. Verranno uniti in un unico PDF pronto per l'invio via PEC.")
    
    with st.expander("Come funzionano i pagamenti?"):
        st.write("I pagamenti sono gestiti in modo sicuro da Lemon Squeezy. Dopo l'acquisto riceverai via email una chiave di licenza da inserire nell'applicazione per attivare il tuo piano.")
    
    # ==================== FOOTER ====================
    st.markdown("""
    <div class="footer">
        <p><strong>POS FACILE</strong> - Generatore POS professionale</p>
        <p style="font-size: 14px;">© 2025 - Tutti i diritti riservati</p>
        <p style="font-size: 12px; color: #999;">
            <a href="#" style="color: #999;">Privacy Policy</a> • 
            <a href="#" style="color: #999;">Termini di Servizio</a> • 
            <a href="#" style="color: #999;">Contatti</a>
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_login_cta():
    """Renderizza la CTA per login nella landing"""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("---")
        st.markdown("### 🚀 Pronto per iniziare?")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📝 Registrati gratis", use_container_width=True, type="primary"):
                st.session_state.show_auth = True
                st.session_state.auth_tab = "register"
                st.rerun()
        with c2:
            if st.button("🔐 Accedi", use_container_width=True):
                st.session_state.show_auth = True
                st.session_state.auth_tab = "login"
                st.rerun()
