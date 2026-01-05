# -*- coding: utf-8 -*-
"""
CANTIERE SICURO - License Manager (Lemon Squeezy)
Gestisce la validazione delle licenze e gli abbonamenti
V2 - Gestione errori migliorata
"""

import streamlit as st
import requests

# Mapping tra variant ID di Lemon Squeezy e piano
VARIANT_TO_PLAN = {
    'base': 'base',
    'pro': 'pro', 
    'unlimited': 'unlimited'
}

PLAN_NAMES = {
    'free': '🆓 Free',
    'base': '⭐ Base',
    'pro': '💎 Pro',
    'unlimited': '🚀 Unlimited'
}

PLAN_LIMITS = {
    'free': 1,
    'base': 5,
    'pro': 20,
    'unlimited': 999999
}

PLAN_PRICES = {
    'free': '€0',
    'base': '€29,99/mese',
    'pro': '€79,99/mese',
    'unlimited': '€119,99/mese'
}


def validate_license(license_key: str) -> tuple:
    """
    Valida una licenza con Lemon Squeezy.
    Restituisce: (is_valid: bool, piano: str, message: str)
    """
    if not license_key or len(license_key) < 10:
        return False, None, "Chiave licenza non valida"
    
    try:
        api_key = st.secrets.get("LEMONSQUEEZY_API_KEY", "")
        if not api_key:
            return False, None, "Configurazione API mancante"
        
        url = "https://api.lemonsqueezy.com/v1/licenses/activate"
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        data = {
            "license_key": license_key,
            "instance_name": f"CantiereSicuro_Web_{st.session_state.get('user_id', 'unknown')[:8]}"
        }
        
        response = requests.post(url, json=data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            res_json = response.json()
            
            if res_json.get('activated') or res_json.get('valid'):
                meta = res_json.get('meta', {})
                product_name = res_json.get('meta', {}).get('product_name', '').lower()
                
                if 'unlimited' in product_name:
                    piano = 'unlimited'
                elif 'pro' in product_name:
                    piano = 'pro'
                else:
                    piano = 'base'
                
                return True, piano, f"Licenza attivata! Piano: {PLAN_NAMES.get(piano, piano)}"
            else:
                error = res_json.get('error', 'Licenza non valida')
                return False, None, f"Errore: {error}"
        
        elif response.status_code == 404:
            return False, None, "Chiave licenza non trovata"
        
        elif response.status_code == 400:
            return validate_existing_license(license_key)
        
        else:
            return False, None, f"Errore server (codice {response.status_code})"
            
    except requests.exceptions.Timeout:
        return False, None, "Timeout - riprova più tardi"
    except requests.exceptions.RequestException as e:
        return False, None, f"Errore di connessione: {str(e)}"
    except Exception as e:
        return False, None, f"Errore imprevisto: {str(e)}"


def validate_existing_license(license_key: str) -> tuple:
    """
    Valida una licenza già attivata.
    """
    try:
        api_key = st.secrets.get("LEMONSQUEEZY_API_KEY", "")
        
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
                product_name = res_json.get('meta', {}).get('product_name', '').lower()
                
                if 'unlimited' in product_name:
                    piano = 'unlimited'
                elif 'pro' in product_name:
                    piano = 'pro'
                else:
                    piano = 'base'
                
                return True, piano, f"Licenza valida! Piano: {PLAN_NAMES.get(piano, piano)}"
            else:
                return False, None, "Licenza scaduta o non valida"
        
        return False, None, "Impossibile validare la licenza"
        
    except Exception as e:
        return False, None, f"Errore: {str(e)}"


def deactivate_license(license_key: str) -> bool:
    """Disattiva una licenza"""
    try:
        api_key = st.secrets.get("LEMONSQUEEZY_API_KEY", "")
        
        url = "https://api.lemonsqueezy.com/v1/licenses/deactivate"
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        data = {
            "license_key": license_key,
            "instance_id": f"CantiereSicuro_Web_{st.session_state.get('user_id', 'unknown')[:8]}"
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
    
    # Verifica user_id
    user_id = st.session_state.get('user_id')
    if not user_id:
        st.sidebar.info("👤 Effettua il login per vedere il tuo piano")
        return
    
    # Prova a recuperare il profilo dal database
    profile = None
    db_available = False
    db_activate_license = None
    
    try:
        from database import get_user_profile, activate_license as db_activate_license_func, create_user_profile
        db_available = True
        db_activate_license = db_activate_license_func
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
    except Exception as e:
        db_available = False
    
    # Se ancora non abbiamo un profilo, usa quello di default
    if not profile:
        profile = get_default_profile()
        if 'user_profile' not in st.session_state:
            st.session_state.user_profile = profile
    
    # Estrai dati dal profilo
    piano = profile.get('piano', 'free')
    pos_mese = profile.get('pos_generati_mese', 0)
    pos_totale = profile.get('pos_generati_totale', 0)
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
        if pos_totale >= 1:
            st.sidebar.error("🚫 POS gratuito esaurito")
            st.sidebar.caption("Passa a un piano a pagamento per continuare")
        else:
            st.sidebar.success("✅ 1 POS gratuito disponibile")
    elif piano == 'unlimited':
        st.sidebar.success("✅ POS illimitati")
    else:
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
            st.sidebar.success(f"✅ {remaining} POS rimanenti")
        else:
            st.sidebar.error("🚫 Limite mensile raggiunto")
    
    # Se free, mostra opzioni upgrade
    if piano == 'free':
        st.sidebar.markdown("---")
        st.sidebar.markdown("#### 🚀 Passa a PRO")
        
        # Input licenza
        license_input = st.sidebar.text_input(
            "Hai già una licenza?",
            placeholder="Inserisci chiave...",
            type="password",
            key="license_input_sidebar"
        )
        
        if st.sidebar.button("✅ Attiva Licenza", use_container_width=True, key="btn_activate_license"):
            if license_input:
                with st.sidebar.spinner("Verifica in corso..."):
                    valid, new_piano, msg = validate_license(license_input)
                    if valid and new_piano:
                        if db_available and db_activate_license:
                            try:
                                if db_activate_license(user_id, license_input, new_piano):
                                    st.sidebar.success(msg)
                                    st.rerun()
                                else:
                                    st.sidebar.error("Errore salvataggio licenza")
                            except Exception as e:
                                st.sidebar.error(f"Errore DB: {str(e)}")
                        else:
                            st.session_state.user_plan = new_piano
                            st.session_state.pos_limit = PLAN_LIMITS.get(new_piano, 1)
                            st.sidebar.success(msg)
                            st.rerun()
                    else:
                        st.sidebar.error(msg)
            else:
                st.sidebar.warning("Inserisci la chiave licenza")
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("#### 💳 Acquista un piano")
        
        # Pulsanti acquisto
        checkout_base = st.secrets.get("CHECKOUT_BASE", "https://cantieresicuro.lemonsqueezy.com/checkout/buy/base")
        checkout_pro = st.secrets.get("CHECKOUT_PRO", "https://cantieresicuro.lemonsqueezy.com/checkout/buy/pro")
        checkout_unlimited = st.secrets.get("CHECKOUT_UNLIMITED", "https://cantieresicuro.lemonsqueezy.com/checkout/buy/unlimited")
        
        st.sidebar.markdown(f"""
        <a href="{checkout_base}" target="_blank" style="text-decoration: none;">
            <div style="background: linear-gradient(135deg, #3B82F6, #2563EB); color: white; padding: 12px; border-radius: 8px; text-align: center; margin: 8px 0; font-weight: 600; font-size: 0.9rem;">
                ⭐ Base - €29,99/mese
            </div>
        </a>
        <a href="{checkout_pro}" target="_blank" style="text-decoration: none;">
            <div style="background: linear-gradient(135deg, #FF6600, #E55A00); color: white; padding: 12px; border-radius: 8px; text-align: center; margin: 8px 0; font-weight: 600; font-size: 0.9rem;">
                💎 Pro - €79,99/mese
            </div>
        </a>
        <a href="{checkout_unlimited}" target="_blank" style="text-decoration: none;">
            <div style="background: linear-gradient(135deg, #10B981, #059669); color: white; padding: 12px; border-radius: 8px; text-align: center; margin: 8px 0; font-weight: 600; font-size: 0.9rem;">
                🚀 Unlimited - €119,99/mese
            </div>
        </a>
        """, unsafe_allow_html=True)
        
        st.sidebar.caption("📧 Dopo l'acquisto riceverai la licenza via email")
    
    else:
        # Utente con piano a pagamento
        st.sidebar.markdown("---")
        license_key = profile.get('license_key', '')
        if license_key:
            st.sidebar.caption(f"🔑 Licenza: {license_key[:8]}...")
            
            if st.sidebar.button("🔄 Verifica Licenza", use_container_width=True, key="btn_verify_license"):
                with st.sidebar.spinner("Verifica..."):
                    valid, _, msg = validate_existing_license(license_key)
                    if valid:
                        st.sidebar.success("Licenza valida ✅")
                    else:
                        st.sidebar.error(msg)


def render_pricing_cards():
    """Renderizza le card dei prezzi per la landing page"""
    
    checkout_base = st.secrets.get("CHECKOUT_BASE", "#")
    checkout_pro = st.secrets.get("CHECKOUT_PRO", "#")
    checkout_unlimited = st.secrets.get("CHECKOUT_UNLIMITED", "#")
    
    st.markdown("""
    <style>
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
            width: 280px;
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
        .pricing-card.featured:hover {
            transform: scale(1.05) translateY(-5px);
        }
        .pricing-title {
            font-size: 1.5rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        .pricing-price {
            font-size: 2.5rem;
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
        }
        .pricing-features li {
            margin: 0.5rem 0;
            list-style: none;
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
        .pricing-btn.secondary {
            background: #E0E0E0;
            color: #333 !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="pricing-card">
            <div class="pricing-title">🆓 Free</div>
            <div class="pricing-price">€0</div>
            <ul class="pricing-features">
                <li>1 POS gratuito</li>
                <li>Tutte le lavorazioni</li>
                <li>Analisi AI base</li>
                <li>PDF professionale</li>
            </ul>
            <a href="#" class="pricing-btn secondary">Piano attuale</a>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="pricing-card">
            <div class="pricing-title">⭐ Base</div>
            <div class="pricing-price">€29,99<span>/mese</span></div>
            <ul class="pricing-features">
                <li>5 POS al mese</li>
                <li>Salva anagrafiche</li>
                <li>Storico POS</li>
                <li>Supporto email</li>
            </ul>
            <a href="{checkout_base}" target="_blank" class="pricing-btn">Acquista ora</a>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="pricing-card featured">
            <div style="background: #FF6600; color: white; padding: 5px; border-radius: 20px; font-size: 12px; margin-bottom: 10px;">⭐ PIÙ POPOLARE</div>
            <div class="pricing-title">💎 Pro</div>
            <div class="pricing-price">€79,99<span>/mese</span></div>
            <ul class="pricing-features">
                <li>20 POS al mese</li>
                <li>Analisi AI avanzata</li>
                <li>Template personalizzati</li>
                <li>Supporto prioritario</li>
            </ul>
            <a href="{checkout_pro}" target="_blank" class="pricing-btn">Acquista ora</a>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="pricing-card">
            <div class="pricing-title">🚀 Unlimited</div>
            <div class="pricing-price">€119,99<span>/mese</span></div>
            <ul class="pricing-features">
                <li>POS illimitati</li>
                <li>Multi-utente (soon)</li>
                <li>API access (soon)</li>
                <li>Supporto dedicato</li>
            </ul>
            <a href="{checkout_unlimited}" target="_blank" class="pricing-btn">Acquista ora</a>
        </div>
        """, unsafe_allow_html=True)