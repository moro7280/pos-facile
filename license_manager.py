# -*- coding: utf-8 -*-
"""
POS FACILE - License Manager (Lemon Squeezy)
Gestisce la validazione delle licenze e gli abbonamenti
V2 - Gestione errori migliorata
"""

import streamlit as st
import requests

# Mapping tra variant ID di Lemon Squeezy e piano
# IMPORTANTE: Questi valori dipendono da come hai chiamato i "Variant" su Lemon Squeezy.
# Se il nome del prodotto contiene "starter", "professional" o "unlimited",
# la funzione validate_license cercherà di mapparli a queste chiavi.
VARIANT_TO_PLAN = {
    'starter': 'base',      # Mappa 'starter' di LS al nostro 'base'
    'professional': 'pro',  # Mappa 'professional' di LS al nostro 'pro'
    'unlimited': 'unlimited'# Mappa 'unlimited' di LS al nostro 'unlimited'
}

PLAN_NAMES = {
    'free': '🆓 Free',
    'base': '⭐ Starter', # Aggiornato nome per coerenza con i tuoi link
    'pro': '💎 Professional', # Aggiornato nome
    'unlimited': '🚀 Unlimited'
}

PLAN_LIMITS = {
    'free': 1,
    'base': 3,   # Aggiornato limite Starter a 3 POS come da tua indicazione precedente
    'pro': 10,   # Aggiornato limite Professional a 10 POS
    'unlimited': 999999
}

PLAN_PRICES = {
    'free': '€0',
    'base': '€9,99/mese',    # Aggiornato prezzo Starter
    'pro': '€24,99/mese',    # Aggiornato prezzo Professional
    'unlimited': '€49,99/mese' # Aggiornato prezzo Unlimited
}

# Link di checkout forniti
CHECKOUT_LINKS = {
    'base': 'https://posfacile.lemonsqueezy.com/checkout/buy/6154ced3-2892-45fa-a7ef-f08f97c24635',
    'pro': 'https://posfacile.lemonsqueezy.com/checkout/buy/ff234bb0-1d0b-433c-8fbb-a63e907755e6',
    'unlimited': 'https://posfacile.lemonsqueezy.com/checkout/buy/59eda380-a79c-45aa-9cba-6962a249a71d'
}


def validate_license(license_key: str) -> tuple:
    """
    Valida una licenza con Lemon Squeezy.
    Restituisce: (is_valid: bool, piano: str, message: str)
    """
    if not license_key or len(license_key) < 10:
        return False, None, "Chiave licenza non valida"
    
    try:
        # Tenta di recuperare l'API Key dai secrets.
        # Assicurati di avere [lemon_squeezy] api_key = "..." nel tuo .streamlit/secrets.toml
        api_key = st.secrets.get("lemon_squeezy", {}).get("api_key", "")
        # Fallback per compatibilità con vecchie configurazioni, se necessario:
        if not api_key:
             api_key = st.secrets.get("LEMONSQUEEZY_API_KEY", "")

        if not api_key:
            return False, None, "Configurazione API Key di Lemon Squeezy mancante nei secrets."
        
        url = "https://api.lemonsqueezy.com/v1/licenses/activate"
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # instance_name aiuta a identificare l'attivazione su LS
        data = {
            "license_key": license_key,
            "instance_name": f"POSFacile_Web_{st.session_state.get('user_id', 'unknown')[:8]}"
        }
        
        response = requests.post(url, json=data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            res_json = response.json()
            
            # Controlla se la licenza è valida e attivata
            if res_json.get('activated') and res_json.get('valid'):
                meta = res_json.get('meta', {})
                # Usa il nome della variante (es. "Starter Plan") per determinare il piano interno
                variant_name = meta.get('variant_name', '').lower()
                product_name = meta.get('product_name', '').lower()
                
                # Logica di matching basata sui nomi dei tuoi prodotti su LS
                if 'unlimited' in variant_name or 'unlimited' in product_name:
                    piano = 'unlimited'
                elif 'professional' in variant_name or 'professional' in product_name:
                    piano = 'pro'
                elif 'starter' in variant_name or 'starter' in product_name:
                    piano = 'base'
                else:
                    # Fallback se il nome non viene riconosciuto
                    piano = 'base'
                    print(f"ATTENZIONE: Piano non riconosciuto per variante '{variant_name}'. Assegnato 'base'.")
                
                return True, piano, f"Licenza attivata! Piano: {PLAN_NAMES.get(piano, piano)}"
            else:
                error = res_json.get('error', {}).get('detail', 'Licenza non valida o scaduta')
                return False, None, f"Errore: {error}"
        
        elif response.status_code == 404:
            return False, None, "Chiave licenza non trovata."
        
        elif response.status_code == 400:
            # Se è già attivata, prova a validarla (per casi di riattivazione sulla stessa istanza)
            return validate_existing_license(license_key)
        
        else:
            return False, None, f"Errore server Lemon Squeezy (codice {response.status_code})"
            
    except requests.exceptions.Timeout:
        return False, None, "Timeout connessione. Riprova più tardi."
    except requests.exceptions.RequestException as e:
        return False, None, f"Errore di connessione: {str(e)}"
    except Exception as e:
        return False, None, f"Errore imprevisto durante la validazione: {str(e)}"


def validate_existing_license(license_key: str) -> tuple:
    """
    Valida una licenza senza tentare di attivarla (utile per check periodici).
    """
    try:
        api_key = st.secrets.get("lemon_squeezy", {}).get("api_key", "")
        if not api_key: api_key = st.secrets.get("LEMONSQUEEZY_API_KEY", "")

        if not api_key: return False, None, "API Key mancante."
        
        url = "https://api.lemonsqueezy.com/v1/licenses/validate"
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        data = {"license_key": license_key}
        
        response = requests.post(url, json=data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            res_json = response.json()
            
            if res_json.get('valid'):
                meta = res_json.get('meta', {})
                variant_name = meta.get('variant_name', '').lower()
                product_name = meta.get('product_name', '').lower()
                
                if 'unlimited' in variant_name or 'unlimited' in product_name:
                    piano = 'unlimited'
                elif 'professional' in variant_name or 'professional' in product_name:
                    piano = 'pro'
                elif 'starter' in variant_name or 'starter' in product_name:
                    piano = 'base'
                else:
                    piano = 'base'
                
                return True, piano, f"Licenza valida! Piano: {PLAN_NAMES.get(piano, piano)}"
            else:
                return False, None, "Licenza scaduta o non valida."
        
        return False, None, f"Impossibile validare la licenza (Status {response.status_code})"
        
    except Exception as e:
        return False, None, f"Errore durante la validazione esistente: {str(e)}"


def deactivate_license(license_key: str) -> bool:
    """Disattiva una licenza per liberare un'attivazione."""
    try:
        api_key = st.secrets.get("lemon_squeezy", {}).get("api_key", "")
        if not api_key: api_key = st.secrets.get("LEMONSQUEEZY_API_KEY", "")

        if not api_key: return False
        
        url = "https://api.lemonsqueezy.com/v1/licenses/deactivate"
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # L'instance_id deve corrispondere a quello usato per l'attivazione
        data = {
            "license_key": license_key,
            "instance_id": f"POSFacile_Web_{st.session_state.get('user_id', 'unknown')[:8]}"
        }
        
        response = requests.post(url, json=data, headers=headers, timeout=10)
        return response.status_code == 200
        
    except:
        return False


def get_default_profile():
    """Restituisce un profilo di default per utenti senza profilo nel DB"""
    return {
        'piano': 'free',
        'pos_generati_mese': 0,
        'pos_generati_totale': 0,
        'license_key': None
    }


def render_subscription_sidebar():
    """Renderizza lo stato abbonamento nella sidebar - V2 con gestione errori"""
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💎 Abbonamento")
    
    # Verifica user_id (simulato se non c'è login reale)
    user_id = st.session_state.get('user_id')
    if not user_id:
        # Se non c'è un sistema di login, si può usare un ID di sessione temporaneo
        # Per ora mostriamo un avviso.
        # st.sidebar.info("👤 Login non rilevato. Funzionalità limitate.")
        # Per testare senza login, commenta le due righe sopra e scommenta questa:
        user_id = "test_user" 
        st.session_state['user_id'] = user_id

    
    # Prova a recuperare il profilo dal database (se esiste un modulo database.py)
    profile = None
    db_available = False
    db_activate_license_func = None
    
    try:
        # Tenta di importare le funzioni DB solo se il file esiste
        from database import get_user_profile, activate_license as db_act_func, create_user_profile
        db_available = True
        db_activate_license_func = db_act_func
        profile = get_user_profile(user_id)
        
        # Se il profilo non esiste, proviamo a crearlo
        if not profile:
            try:
                create_user_profile(user_id)
                profile = get_user_profile(user_id)
            except Exception:
                pass
                
    except ImportError:
        db_available = False
        # st.sidebar.warning("Modulo database non trovato. Uso profilo in memoria.")
    except Exception as e:
        db_available = False
        # st.sidebar.error(f"Errore connessione DB: {e}. Uso profilo in memoria.")
    
    # Se ancora non abbiamo un profilo (no DB o errore), usa quello di default in session state
    if not profile:
        if 'user_profile' not in st.session_state:
            st.session_state.user_profile = get_default_profile()
        profile = st.session_state.user_profile
    
    # Estrai dati dal profilo
    piano = profile.get('piano', 'free')
    pos_mese = profile.get('pos_generati_mese', 0)
    # pos_totale = profile.get('pos_generati_totale', 0) # Non usato nella UI attuale
    limite = PLAN_LIMITS.get(piano, 1)
    
    # Salva nel session_state per uso da altre parti dell'app
    st.session_state.user_plan = piano
    st.session_state.pos_used_this_month = pos_mese
    st.session_state.pos_limit = limite
    
    # Mostra stato piano con stile migliorato
    piano_color = {
        'free': '#6B7280',
        'base': '#3B82F6', 
        'pro': '#FF6600',
        'unlimited': '#10B981'
    }.get(piano, '#6B7280')
    
    st.sidebar.markdown(f"""
    <div style="background: linear-gradient(135deg, {piano_color}20, {piano_color}05); 
                border: 1px solid {piano_color}50; 
                border-radius: 10px; 
                padding: 15px; 
                margin-bottom: 15px;">
        <p style="margin: 0 0 5px 0; color: #64748B; font-size: 0.8rem; font-weight: 600;">PIANO ATTIVO</p>
        <p style="margin: 0; color: {piano_color}; font-size: 1.4rem; font-weight: 700;">
            {PLAN_NAMES.get(piano, piano)}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Mostra utilizzo POS
    if piano == 'free':
        if pos_mese >= limite:
            st.sidebar.error(f"🚫 Limite POS gratuito raggiunto ({pos_mese}/{limite})")
            st.sidebar.caption("Passa a un piano a pagamento per crearne altri.")
        else:
            st.sidebar.success(f"✅ {limite - pos_mese} POS gratuiti rimanenti")
    elif piano == 'unlimited':
        st.sidebar.success("✅ POS illimitati")
    else:
        # Piani Base e Pro
        remaining = max(0, limite - pos_mese)
        progress = min(pos_mese / limite, 1.0) if limite > 0 else 0
        
        st.sidebar.markdown(f"""
        <div style="background: #F8FAFC; border-radius: 8px; padding: 12px; margin-bottom: 10px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                <span style="color: #64748B; font-size: 0.85rem;">POS questo mese</span>
                <span style="color: #1a1a2e; font-weight: 700;">{pos_mese}/{limite}</span>
            </div>
            <div style="background: #E2E8F0; border-radius: 10px; height: 8px; overflow: hidden;">
                <div style="background: {'#EF4444' if progress >= 0.9 else '#FF6600'}; 
                            width: {progress * 100}%; 
                            height: 100%; 
                            border-radius: 10px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if remaining > 0:
            # st.sidebar.success(f"✅ {remaining} POS rimanenti")
            pass # Barra già sufficiente
        else:
            st.sidebar.error("🚫 Limite mensile raggiunto")
    
    # Se free, mostra area attivazione licenza
    if piano == 'free':
        st.sidebar.markdown("---")
        st.sidebar.markdown("#### 🔑 Attiva Licenza")
        
        # Input licenza con key unica per evitare conflitti
        license_input = st.sidebar.text_input(
            "Hai acquistato un piano?",
            placeholder="Inserisci la chiave (es. XXXX-...)",
            type="password",
            key="license_input_sidebar_unique"
        )
        
        if st.sidebar.button("✅ Attiva Ora", use_container_width=True, key="btn_activate_license_sidebar"):
            if license_input:
                with st.sidebar.spinner("Convalida in corso..."):
                    valid, new_piano, msg = validate_license(license_input)
                    
                    if valid and new_piano:
                        st.sidebar.success(msg)
                        
                        # Aggiorna il DB se disponibile
                        if db_available and db_activate_license_func:
                            try:
                                if db_activate_license_func(user_id, license_input, new_piano):
                                    st.balloons()
                                    st.rerun()
                                else:
                                    st.sidebar.error("Errore nel salvataggio della licenza sul database.")
                            except Exception as e:
                                st.sidebar.error(f"Errore DB durante attivazione: {e}")
                        else:
                            # Aggiorna solo la sessione (no persistenza)
                            st.session_state.user_profile['piano'] = new_piano
                            st.session_state.user_profile['license_key'] = license_input
                            st.balloons()
                            st.rerun()
                    else:
                        st.sidebar.error(msg)
            else:
                st.sidebar.warning("Inserisci la chiave della licenza.")
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("#### 💳 Acquista un Piano")
        
        # Pulsanti acquisto con i TUOI LINK AGGIORNATI
        st.sidebar.markdown(f"""
        <a href="{CHECKOUT_LINKS['base']}" target="_blank" style="text-decoration: none;">
            <div style="background: linear-gradient(135deg, #3B82F6, #2563EB); color: white; padding: 12px; border-radius: 8px; text-align: center; margin: 8px 0; font-weight: 600; font-size: 0.9rem; transition: transform 0.2s;" onmouseover="this.style.transform='scale(1.02)'" onmouseout="this.style.transform='scale(1.0)'">
                ⭐ Starter - {PLAN_PRICES['base']}
            </div>
        </a>
        <a href="{CHECKOUT_LINKS['pro']}" target="_blank" style="text-decoration: none;">
            <div style="background: linear-gradient(135deg, #FF6600, #E55A00); color: white; padding: 12px; border-radius: 8px; text-align: center; margin: 8px 0; font-weight: 600; font-size: 0.9rem; transition: transform 0.2s;" onmouseover="this.style.transform='scale(1.02)'" onmouseout="this.style.transform='scale(1.0)'">
                💎 Professional - {PLAN_PRICES['pro']}
            </div>
        </a>
        <a href="{CHECKOUT_LINKS['unlimited']}" target="_blank" style="text-decoration: none;">
            <div style="background: linear-gradient(135deg, #10B981, #059669); color: white; padding: 12px; border-radius: 8px; text-align: center; margin: 8px 0; font-weight: 600; font-size: 0.9rem; transition: transform 0.2s;" onmouseover="this.style.transform='scale(1.02)'" onmouseout="this.style.transform='scale(1.0)'">
                🚀 Unlimited - {PLAN_PRICES['unlimited']}
            </div>
        </a>
        """, unsafe_allow_html=True)
        
        st.sidebar.caption("📧 Riceverai la licenza via email subito dopo l'acquisto.")
    
    else:
        # Utente con piano a pagamento attivo
        st.sidebar.markdown("---")
        license_key = profile.get('license_key', '')
        if license_key:
            st.sidebar.caption(f"🔑 Licenza attiva: `{license_key[:6]}...`")
            
            col_verify, col_deactivate = st.sidebar.columns(2)
            with col_verify:
                if st.button("🔄 Verifica", use_container_width=True, key="btn_verify_exist"):
                    with st.spinner("Check..."):
                        valid, _, msg = validate_existing_license(license_key)
                        if valid:
                            st.toast("Licenza valida ✅", icon="✅")
                        else:
                            st.error(msg)
            with col_deactivate:
                # Pulsante Disattiva (opzionale, per permettere di spostare la licenza)
                # if st.button("❌ Disattiva", use_container_width=True, key="btn_deactivate"):
                #     with st.spinner("Disattivazione..."):
                #         if deactivate_license(license_key):
                #             # Reset al piano free nel DB/Sessione
                #             if db_available and db_activate_license_func:
                #                 db_activate_license_func(user_id, None, 'free')
                #             st.session_state.user_profile['piano'] = 'free'
                #             st.session_state.user_profile['license_key'] = None
                #             st.success("Licenza disattivata.")
                #             st.rerun()
                #         else:
                #             st.error("Errore durante la disattivazione.")
                pass


def render_pricing_cards():
    """Renderizza le card dei prezzi (es. per una pagina 'Prezzi' principale)"""
    
    # Stili CSS per le card (puoi spostarli in un file CSS esterno se preferisci)
    st.markdown("""
    <style>
        .pricing-container {
            display: flex; gap: 20px; justify-content: center; flex-wrap: wrap; margin: 2rem 0;
        }
        .pricing-card {
            background: white; border-radius: 16px; padding: 2rem; width: 280px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08); text-align: center; transition: all 0.3s ease;
            border: 1px solid #eee; display: flex; flex-direction: column;
        }
        .pricing-card:hover { transform: translateY(-5px); box-shadow: 0 8px 25px rgba(0,0,0,0.12); }
        .pricing-card.featured { border: 2px solid #FF6600; transform: scale(1.03); }
        .pricing-card.featured:hover { transform: scale(1.03) translateY(-5px); }
        .pricing-title { font-size: 1.4rem; font-weight: 700; margin-bottom: 0.5rem; color: #1a1a2e; }
        .pricing-price { font-size: 2.2rem; font-weight: 800; color: #FF6600; margin: 1rem 0; }
        .pricing-price span { font-size: 0.9rem; color: #666; font-weight: 400; }
        .pricing-features { text-align: left; margin: 1.5rem 0; padding: 0; flex-grow: 1; }
        .pricing-features li { margin: 0.8rem 0; list-style: none; font-size: 0.95rem; color: #4a5568; display: flex; align-items: center; }
        .pricing-features li svg { margin-right: 8px; color: #10B981; flex-shrink: 0; }
        .pricing-btn {
            display: inline-block; width: 100%; padding: 12px 24px; background: #FF6600; color: white !important;
            text-decoration: none; border-radius: 10px; font-weight: 700; transition: background 0.3s; cursor: pointer;
        }
        .pricing-btn:hover { background: #E55A00; }
        .pricing-btn.secondary { background: #E2E8F0; color: #4a5568 !important; }
        .pricing-btn.secondary:hover { background: #CBD5E0; }
        .badge-popular { background: #FF6600; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; display: inline-block; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)
    
    # Icona di spunta SVG per le liste
    check_icon = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>"""

    col1, col2, col3, col4 = st.columns(4)
    
    # Card Free
    with col1:
        st.markdown(f"""
        <div class="pricing-card">
            <div class="pricing-title">{PLAN_NAMES['free']}</div>
            <div class="pricing-price">{PLAN_PRICES['free']}</div>
            <ul class="pricing-features">
                <li>{check_icon} 1 POS gratuito / mese</li>
                <li>{check_icon} Tutte le lavorazioni</li>
                <li>{check_icon} Analisi AI base</li>
                <li>{check_icon} Export PDF standard</li>
            </ul>
            <a href="#" class="pricing-btn secondary" onclick="return false;">Piano Attuale</a>
        </div>
        """, unsafe_allow_html=True)
    
    # Card Starter
    with col2:
        st.markdown(f"""
        <div class="pricing-card">
            <div class="pricing-title">{PLAN_NAMES['base']}</div>
            <div class="pricing-price">{PLAN_PRICES['base'].split('/')[0]}<span>/mese</span></div>
            <ul class="pricing-features">
                <li>{check_icon} <b>{PLAN_LIMITS['base']} POS</b> al mese</li>
                <li>{check_icon} Analisi Rischi AI</li>
                <li>{check_icon} Anagrafiche illimitate</li>
                <li>{check_icon} Supporto Email</li>
            </ul>
            <a href="{CHECKOUT_LINKS['base']}" target="_blank" class="pricing-btn">Scegli Starter</a>
        </div>
        """, unsafe_allow_html=True)
    
    # Card Professional (Featured)
    with col3:
        st.markdown(f"""
        <div class="pricing-card featured">
            <div><span class="badge-popular">⭐ PIÙ SCELTO</span></div>
            <div class="pricing-title">{PLAN_NAMES['pro']}</div>
            <div class="pricing-price">{PLAN_PRICES['pro'].split('/')[0]}<span>/mese</span></div>
            <ul class="pricing-features">
                <li>{check_icon} <b>{PLAN_LIMITS['pro']} POS</b> al mese</li>
                <li>{check_icon} <b>AI Avanzata</b> (Magic Writer)</li>
                <li>{check_icon} Anagrafiche illimitate</li>
                <li>{check_icon} Supporto Prioritario</li>
            </ul>
            <a href="{CHECKOUT_LINKS['pro']}" target="_blank" class="pricing-btn">Scegli Professional</a>
        </div>
        """, unsafe_allow_html=True)
    
    # Card Unlimited
    with col4:
        st.markdown(f"""
        <div class="pricing-card">
            <div class="pricing-title">{PLAN_NAMES['unlimited']}</div>
            <div class="pricing-price">{PLAN_PRICES['unlimited'].split('/')[0]}<span>/mese</span></div>
            <ul class="pricing-features">
                <li>{check_icon} <b>POS Illimitati</b></li>
                <li>{check_icon} AI Avanzata senza limiti</li>
                <li>{check_icon} Anagrafiche illimitate</li>
                <li>{check_icon} <b>Supporto WhatsApp</b></li>
            </ul>
            <a href="{CHECKOUT_LINKS['unlimited']}" target="_blank" class="pricing-btn">Scegli Unlimited</a>
        </div>
        """, unsafe_allow_html=True)

# --- ESEMPIO DI UTILIZZO SE LANCIATO COME SCRIPT ---
if __name__ == "__main__":
    # Configura una chiave API fittizia per il test locale se non presente nei secrets
    if "lemon_squeezy" not in st.secrets:
        # st.secrets["lemon_squeezy"] = {"api_key": "LA_TUA_CHIAVE_DI_TEST_QUI"} # Scommenta e metti la tua per testare
        pass

    st.set_page_config(page_title="Test License Manager", layout="wide")
    
    st.title("Test del License Manager")
    
    # Simula un utente loggato
    if 'user_id' not in st.session_state:
        st.session_state.user_id = "test_user_123"
        
    with st.sidebar:
        st.header("Sidebar Simulation")
        render_subscription_sidebar()
        
    st.header("Pricing Cards Render")
    render_pricing_cards()
    
    st.divider()
    st.header("Debug e Test Manuale")
    
    col_test1, col_test2 = st.columns(2)
    
    with col_test1:
        st.subheader("Test Validazione Licenza (Attivazione)")
        test_key_input = st.text_input("Inserisci una chiave di test (Lemon Squeezy Test Mode):", key="test_key_act")
        if st.button("Test Attivazione"):
            if test_key_input:
                with st.spinner("Chiamata API..."):
                    res = validate_license(test_key_input)
                    st.write(res)
            else:
                st.warning("Inserisci una chiave.")
                
    with col_test2:
        st.subheader("Test Validazione Esistente (Solo Check)")
        test_key_exist = st.text_input("Inserisci una chiave già attiva:", key="test_key_val")
        if st.button("Test Validazione"):
            if test_key_exist:
                 with st.spinner("Chiamata API..."):
                    res = validate_existing_license(test_key_exist)
                    st.write(res)
            else:
                st.warning("Inserisci una chiave.")
