# -*- coding: utf-8 -*-
"""
POS FACILE - Landing Page
Target: Geometri, Ingegneri, Consulenti Sicurezza, CSP/CSE
"""

import streamlit as st


def render_landing_page():
    """Renderizza la landing page completa - Target professionisti"""
    
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
            font-size: 3rem;
            margin-bottom: 0.5rem;
            color: #FF6600;
            line-height: 1.1;
        }
        .hero h2 {
            font-size: 2rem;
            margin-bottom: 1.5rem;
            color: white;
            font-weight: 400;
        }
        .hero p {
            font-size: 1.2rem;
            color: #B0BEC5;
            margin-bottom: 2rem;
            max-width: 700px;
            margin-left: auto;
            margin-right: auto;
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
        .feature-icon { font-size: 3rem; margin-bottom: 1rem; }
        .feature-title { font-size: 1.2rem; font-weight: bold; margin-bottom: 0.5rem; color: #1a1a2e; }
        .feature-desc { color: #666; font-size: 0.95rem; line-height: 1.6; }
        
        /* Stats */
        .stats-container {
            display: flex; justify-content: center; gap: 4rem;
            margin: 3rem 0; flex-wrap: wrap;
        }
        .stat-item { text-align: center; }
        .stat-number { font-size: 3rem; font-weight: bold; color: #FF6600; }
        .stat-label { color: #666; font-size: 1rem; }
        
        /* Testimonials */
        .testimonial {
            background: #f8f9fa; padding: 2rem; border-radius: 16px;
            margin: 1rem 0; border-left: 4px solid #FF6600; height: 100%;
        }
        .testimonial-text { font-style: italic; font-size: 1rem; color: #333; margin-bottom: 1rem; line-height: 1.6; }
        .testimonial-author { font-weight: bold; color: #1a1a2e; }
        .testimonial-role { color: #FF6600; font-size: 0.9rem; font-weight: 600; }
        
        /* CTA Section */
        .cta-section {
            background: linear-gradient(135deg, #FF6600 0%, #ff8533 100%);
            color: white; padding: 4rem 2rem; border-radius: 20px;
            text-align: center; margin: 3rem 0;
        }
        .cta-section h2 { font-size: 2.2rem; margin-bottom: 1rem; }
        .cta-section p { font-size: 1.1rem; margin-bottom: 2rem; opacity: 0.95; }
        
        /* Footer */
        .footer {
            text-align: center; padding: 2rem; color: #666;
            border-top: 1px solid #eee; margin-top: 3rem;
        }
        
        /* Pricing */
        .pricing-card {
            background: white; border-radius: 16px; padding: 2rem; width: 100%;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08); text-align: center;
            transition: transform 0.3s; border: 1px solid #eee;
        }
        .pricing-card:hover { transform: translateY(-5px); }
        .pricing-card.featured { border: 2px solid #FF6600; transform: scale(1.02); }
        .pricing-title { font-size: 1.2rem; font-weight: 700; margin-bottom: 0.5rem; }
        .pricing-price { font-size: 2.2rem; font-weight: 800; color: #FF6600; margin: 0.5rem 0; }
        .pricing-price span { font-size: 0.9rem; color: #666; font-weight: 400; }
        .pricing-per-pos { font-size: 0.85rem; color: #64748B; margin-bottom: 1rem; }
        .pricing-features { text-align: left; margin: 1rem 0; padding: 0; }
        .pricing-features li { margin: 0.5rem 0; list-style: none; font-size: 0.9rem; }
        .pricing-features li::before { content: "✅ "; }
        .pricing-features li.no::before { content: "✗ "; color: #CBD5E1; }
        .pricing-features li.no { color: #CBD5E1; }
        .pricing-btn {
            display: inline-block; width: 100%; padding: 12px 24px;
            background: #FF6600; color: white !important; text-decoration: none;
            border-radius: 8px; font-weight: bold; transition: background 0.3s;
        }
        .pricing-btn:hover { background: #E55A00; }
        .pricing-btn.outline { background: white; color: #FF6600 !important; border: 2px solid #FF6600; }
    </style>
    """, unsafe_allow_html=True)
    
    # ==================== HERO SECTION ====================
    st.markdown("""
    <div class="hero">
        <h1>Basta ore su Word.</h1>
        <h2>POS conforme in 10 minuti.</h2>
        <p>Sei un geometra, un ingegnere o un consulente sicurezza? POS Facile genera 
        Piani Operativi di Sicurezza conformi al D.Lgs 81/08 con l'AI. Selezioni le 
        lavorazioni, l'app calcola rischi, DPI e misure. PDF pronto per il CSE.</p>
        <a href="#pricing" class="hero-btn">🎁 Primo POS Gratis</a>
        <a href="#features" class="hero-btn secondary">Vedi come funziona</a>
    </div>
    """, unsafe_allow_html=True)
    
    # ==================== STATS ====================
    st.markdown("""
    <div class="stats-container">
        <div class="stat-item">
            <div class="stat-number">10 min</div>
            <div class="stat-label">Invece di 4 ore</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">100%</div>
            <div class="stat-label">Conforme D.Lgs 81/08</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">12+</div>
            <div class="stat-label">Lavorazioni con rischi</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">AI</div>
            <div class="stat-label">Analisi rischi</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ==================== FEATURES ====================
    st.markdown("<a name='features'></a>", unsafe_allow_html=True)
    st.markdown("## ✨ Perché i professionisti scelgono POS FACILE")
    st.markdown("<p style='text-align: center; color: #666; margin-bottom: 2rem;'>Meno tempo sulla burocrazia, più tempo per i tuoi clienti.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🧠</div>
            <div class="feature-title">AI che conosce il D.Lgs 81/08</div>
            <div class="feature-desc">Seleziona le lavorazioni e l'AI genera rischi specifici, DPI con norme EN, misure di prevenzione e valori limite di esposizione.</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">⚡</div>
            <div class="feature-title">Da 4 ore a 10 minuti</div>
            <div class="feature-desc">Basta copiare da vecchi template Word. Compila una volta i dati dell'impresa, li ritrovi per ogni cantiere successivo.</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">✅</div>
            <div class="feature-title">Conforme Allegato XV</div>
            <div class="feature-desc">Struttura completa: premessa, organigramma, valutazione rischi, procedure emergenza, cronoprogramma. Pronto per CSE e ASL.</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col4, col5, col6 = st.columns(3)
    
    with col4:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📎</div>
            <div class="feature-title">PDF Unico con Allegati</div>
            <div class="feature-desc">Carica DURC, Visura, Attestati e Idoneità. Li uniamo al POS in un unico PDF pronto per la PEC.</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">💾</div>
            <div class="feature-title">Gestisci più imprese</div>
            <div class="feature-desc">Salvi l'anagrafica di ogni cliente. Al prossimo cantiere carichi i dati in un click: lavoratori, attrezzature, figure della sicurezza.</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col6:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">☁️</div>
            <div class="feature-title">Sempre con te in cantiere</div>
            <div class="feature-desc">Web app cloud: funziona da PC, tablet e smartphone. Nessuna installazione.</div>
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
            <h4>Dati Impresa</h4>
            <p style="color: #666;">Inserisci o carica l'anagrafica del cliente</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <div style="font-size: 3rem;">2️⃣</div>
            <h4>Cantiere e Lavorazioni</h4>
            <p style="color: #666;">Seleziona le lavorazioni previste</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <div style="font-size: 3rem;">3️⃣</div>
            <h4>L'AI Analizza i Rischi</h4>
            <p style="color: #666;">Rischi, DPI e misure automatiche</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <div style="font-size: 3rem;">4️⃣</div>
            <h4>Scarica il PDF</h4>
            <p style="color: #666;">Pronto per firma e invio al CSE</p>
        </div>
        """, unsafe_allow_html=True)
    
    # ==================== PRICING ====================
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<a name='pricing'></a>", unsafe_allow_html=True)
    st.markdown("## 💰 Quanto tempo vuoi risparmiare?")
    st.markdown("<p style='text-align: center; color: #666; font-size: 1.1rem;'>Ogni piano si ripaga con un singolo POS rispetto al tempo risparmiato.</p>", unsafe_allow_html=True)
    
    checkout_starter = st.secrets.get("CHECKOUT_STARTER", "#")
    checkout_professional = st.secrets.get("CHECKOUT_PROFESSIONAL", "#")
    checkout_unlimited = st.secrets.get("CHECKOUT_UNLIMITED", "#")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="pricing-card">
            <div class="pricing-title">🆓 Free</div>
            <div class="pricing-price">€0</div>
            <div class="pricing-per-pos">per sempre</div>
            <ul class="pricing-features">
                <li>1 POS gratuito</li>
                <li>Tutte le lavorazioni</li>
                <li>PDF professionale</li>
                <li class="no">Salvataggio anagrafiche</li>
            </ul>
            <a href="#" class="pricing-btn outline">Prova Gratis</a>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="pricing-card">
            <div class="pricing-title">⭐ Starter</div>
            <div class="pricing-price">€9,99<span>/mese</span></div>
            <div class="pricing-per-pos">~€3,33 a POS</div>
            <ul class="pricing-features">
                <li><b>3 POS</b> al mese</li>
                <li>Salva anagrafiche clienti</li>
                <li>Storico documenti</li>
                <li>Supporto email</li>
            </ul>
            <a href="{checkout_starter}" target="_blank" class="pricing-btn">Scegli Starter</a>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="pricing-card featured">
            <div style="background: #FF6600; color: white; padding: 4px 14px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; display: inline-block; margin-bottom: 10px;">🔥 PIÙ SCELTO</div>
            <div class="pricing-title" style="color: #FF6600;">💎 Professional</div>
            <div class="pricing-price">€24,99<span>/mese</span></div>
            <div class="pricing-per-pos">~€2,50 a POS</div>
            <ul class="pricing-features">
                <li><b>10 POS</b> al mese</li>
                <li><b>AI Avanzata</b></li>
                <li>Anagrafiche illimitate</li>
                <li>Supporto prioritario</li>
            </ul>
            <a href="{checkout_professional}" target="_blank" class="pricing-btn">🚀 Scegli Professional</a>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="pricing-card">
            <div class="pricing-title">🚀 Unlimited</div>
            <div class="pricing-price">€49,99<span>/mese</span></div>
            <div class="pricing-per-pos">POS illimitati</div>
            <ul class="pricing-features">
                <li><b>POS Illimitati</b></li>
                <li>Tutto di Professional</li>
                <li>Supporto WhatsApp</li>
                <li>Nuove funzioni in anteprima</li>
            </ul>
            <a href="{checkout_unlimited}" target="_blank" class="pricing-btn">Scegli Unlimited</a>
        </div>
        """, unsafe_allow_html=True)
    
    # ==================== TESTIMONIALS ====================
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("## 💬 Cosa dicono i professionisti")
    st.markdown("<p style='text-align: center; color: #666;'>Chi redige POS ogni settimana ha scelto POS Facile.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="testimonial">
            <div class="testimonial-text">"Faccio 6-8 POS al mese per le imprese della zona. Prima ci mettevo mezza giornata ciascuno, adesso in 10 minuti ho un documento che il CSE non mi ha mai contestato."</div>
            <div class="testimonial-author">Marco R.</div>
            <div class="testimonial-role">Geometra libero professionista</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="testimonial">
            <div class="testimonial-text">"La parte dei rischi specifici con norme EN e valori limite è quello che fa la differenza. Non è il solito template vuoto — qui c'è sostanza tecnica vera."</div>
            <div class="testimonial-author">Ing. Laura B.</div>
            <div class="testimonial-role">CSP/CSE e RSPP</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="testimonial">
            <div class="testimonial-text">"Gestisco la sicurezza per 12 imprese. Salvare le anagrafiche e ricaricarle mi fa risparmiare un'enormità di tempo. Il piano Professional si ripaga al primo POS."</div>
            <div class="testimonial-author">Geom. Paolo G.</div>
            <div class="testimonial-role">Consulente sicurezza cantieri</div>
        </div>
        """, unsafe_allow_html=True)
    
    # ==================== CTA FINALE ====================
    st.markdown("""
    <div class="cta-section">
        <h2>🎁 Prova con un POS reale — è gratis</h2>
        <p>Registrati, genera il tuo primo POS su un cantiere vero, e vedi con i tuoi occhi quanto tempo risparmi.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ==================== FAQ ====================
    st.markdown("## ❓ Domande Frequenti")
    
    with st.expander("📋 Il POS generato è conforme alla normativa?"):
        st.write("**Sì.** Il documento segue fedelmente l'Allegato XV del D.Lgs 81/08 con tutte le sezioni obbligatorie: dati impresa, organigramma sicurezza, valutazione rischi specifici per lavorazione, DPI con norme EN di riferimento, misure di prevenzione, procedure di emergenza e cronoprogramma.")
    
    with st.expander("👷 Posso usarlo per gestire più imprese clienti?"):
        st.write("**Sì.** Con i piani a pagamento puoi salvare le anagrafiche di più imprese (lavoratori, attrezzature, figure della sicurezza) e ricaricarle in un click quando crei un nuovo POS per lo stesso cliente.")
    
    with st.expander("🎁 Come funziona il POS gratuito?"):
        st.write("Registrandoti ottieni **1 POS gratuito** completo, con tutte le funzionalità. Generalo su un cantiere reale per valutare la qualità del documento. Per generare altri POS, scegli un piano.")
    
    with st.expander("🤖 Come funziona l'analisi AI dei rischi?"):
        st.write("L'AI analizza le lavorazioni selezionate e la descrizione del cantiere per generare rischi specifici, misure di prevenzione e DPI appropriati. Tu mantieni il **controllo finale** e puoi modificare tutto prima di generare il PDF.")
    
    with st.expander("📎 Posso allegare documenti al POS?"):
        st.write("**Sì.** Puoi caricare DURC, Visura Camerale, Attestati di Formazione, Idoneità Sanitarie, Libretti Attrezzature e Schede SDS. Vengono uniti al POS in un **unico PDF** pronto per l'invio via PEC al Coordinatore.")
    
    with st.expander("💳 Come funzionano i pagamenti?"):
        st.write("Pagamenti sicuri con **Lemon Squeezy**. Ricevi una licenza via email da inserire nell'app. Puoi annullare in qualsiasi momento.")
    
    # ==================== FOOTER ====================
    st.markdown("""
    <div class="footer">
        <p><strong>POS FACILE</strong> — Lo strumento dei professionisti della sicurezza in cantiere.</p>
        <p style="font-size: 14px;">© 2026 — Tutti i diritti riservati</p>
        <p style="font-size: 12px; color: #999;">
            <a href="/privacy" style="color: #999;">Privacy Policy</a> • 
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
