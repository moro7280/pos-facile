# -*- coding: utf-8 -*-
"""
POS FACILE - Database Manager (Supabase)
Gestisce tutte le operazioni con il database
"""

import streamlit as st
from datetime import datetime

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False


def get_supabase_client() -> Client:
    """
    Restituisce il client Supabase.
    Priorità: client autenticato (dopo login) > client anon (nuovo).
    """
    if not SUPABASE_AVAILABLE:
        return None
    
    # 1. Se esiste un client autenticato in session_state (post-login), usa quello
    #    Questo è fondamentale per le RLS policies che richiedono auth.uid()
    if hasattr(st, 'session_state') and 'supabase_client' in st.session_state:
        return st.session_state.supabase_client
    
    # 2. Altrimenti crea un client anonimo (per operazioni pre-login)
    try:
        url = st.secrets.get("SUPABASE_URL", "")
        key = st.secrets.get("SUPABASE_ANON_KEY", "")
        
        if url and key:
            return create_client(url, key)
    except Exception as e:
        print(f"Errore connessione Supabase: {e}")
    
    return None


# ============================================================================
# GESTIONE PROFILO UTENTE
# ============================================================================

def get_user_profile(user_id: str) -> dict:
    """Recupera il profilo utente"""
    client = get_supabase_client()
    if not client:
        return None
    
    try:
        response = client.table('profiles').select('*').eq('id', user_id).single().execute()
        return response.data
    except Exception as e:
        print(f"Errore get_user_profile: {e}")
        return None


def create_user_profile(user_id: str, email: str = None) -> bool:
    """Crea un profilo utente se non esiste (fallback se il trigger Supabase non lo crea)"""
    client = get_supabase_client()
    if not client:
        return False
    
    try:
        data = {
            'id': user_id,
            'email': email or '',
            'piano': 'free',
            'pos_generati_totale': 0,
            'pos_generati_mese': 0
        }
        client.table('profiles').insert(data).execute()
        return True
    except Exception as e:
        # Se esiste già (duplicate key), non è un errore
        if 'duplicate' in str(e).lower() or '23505' in str(e):
            return True
        print(f"Errore create_user_profile: {e}")
        return False


def update_user_profile(user_id: str, data: dict) -> bool:
    """Aggiorna il profilo utente"""
    client = get_supabase_client()
    if not client:
        return False
    
    try:
        client.table('profiles').update(data).eq('id', user_id).execute()
        return True
    except Exception as e:
        print(f"Errore update_user_profile: {e}")
        return False


def get_pos_limits(piano: str) -> int:
    """Restituisce il limite POS per piano"""
    limits = {
        'free': 1,      # 1 POS totale per sempre
        'base': 3,      # 3 POS al mese (Starter)
        'pro': 10,      # 10 POS al mese (Professional)
        'unlimited': 999999  # Illimitati
    }
    return limits.get(piano, 1)


def can_generate_pos(user_id: str) -> tuple:
    """
    Verifica se l'utente può generare un POS.
    Restituisce: (can_generate: bool, message: str, remaining: int)
    """
    profile = get_user_profile(user_id)
    if not profile:
        return False, "Profilo non trovato", 0
    
    piano = profile.get('piano', 'free')
    pos_totale = profile.get('pos_generati_totale', 0)
    pos_mese = profile.get('pos_generati_mese', 0)
    
    # Controlla se siamo in un nuovo mese (reset contatore)
    mese_db = profile.get('mese_contatore', 1)
    anno_db = profile.get('anno_contatore', 2024)
    mese_attuale = datetime.now().month
    anno_attuale = datetime.now().year
    
    if mese_db != mese_attuale or anno_db != anno_attuale:
        # Reset contatore mensile
        update_user_profile(user_id, {
            'pos_generati_mese': 0,
            'mese_contatore': mese_attuale,
            'anno_contatore': anno_attuale
        })
        pos_mese = 0
    
    limite = get_pos_limits(piano)
    
    if piano == 'free':
        # Piano free: 1 POS totale per sempre
        if pos_totale >= 1:
            return False, "Hai già utilizzato il tuo POS gratuito. Passa a un piano PRO!", 0
        return True, "Puoi generare il tuo POS gratuito", 1
    else:
        # Piani a pagamento: limite mensile
        remaining = limite - pos_mese
        if remaining <= 0:
            return False, f"Hai raggiunto il limite di {limite} POS per questo mese", 0
        return True, f"Puoi generare ancora {remaining} POS questo mese", remaining


def increment_pos_counter(user_id: str) -> bool:
    """Incrementa il contatore POS dopo una generazione"""
    profile = get_user_profile(user_id)
    if not profile:
        return False
    
    try:
        client = get_supabase_client()
        client.table('profiles').update({
            'pos_generati_totale': profile.get('pos_generati_totale', 0) + 1,
            'pos_generati_mese': profile.get('pos_generati_mese', 0) + 1
        }).eq('id', user_id).execute()
        return True
    except Exception as e:
        print(f"Errore increment_pos_counter: {e}")
        return False


def activate_license(user_id: str, license_key: str, piano: str) -> bool:
    """Attiva una licenza per l'utente"""
    try:
        client = get_supabase_client()
        client.table('profiles').update({
            'piano': piano,
            'license_key': license_key,
            'license_activated_at': datetime.now().isoformat(),
            'pos_generati_mese': 0  # Reset contatore mese
        }).eq('id', user_id).execute()
        return True
    except Exception as e:
        print(f"Errore activate_license: {e}")
        return False


# ============================================================================
# GESTIONE IMPRESE (ANAGRAFICHE)
# ============================================================================

def get_user_imprese(user_id: str) -> list:
    """Recupera tutte le imprese dell'utente"""
    client = get_supabase_client()
    if not client:
        return []
    
    try:
        response = client.table('imprese').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
        return response.data or []
    except Exception as e:
        print(f"Errore get_user_imprese: {e}")
        return []


def get_impresa_by_id(impresa_id: str) -> dict:
    """Recupera un'impresa specifica"""
    client = get_supabase_client()
    if not client:
        return None
    
    try:
        response = client.table('imprese').select('*').eq('id', impresa_id).single().execute()
        return response.data
    except Exception as e:
        print(f"Errore get_impresa_by_id: {e}")
        return None


def save_impresa(user_id: str, impresa_data: dict) -> str:
    """Salva o aggiorna un'impresa. Restituisce l'ID."""
    client = get_supabase_client()
    if not client:
        return None
    
    try:
        impresa_id = impresa_data.pop('id', None)
        impresa_data['user_id'] = user_id
        
        if impresa_id:
            # Update
            response = client.table('imprese').update(impresa_data).eq('id', impresa_id).execute()
        else:
            # Insert
            response = client.table('imprese').insert(impresa_data).execute()
        
        if response.data:
            return response.data[0].get('id')
        return None
    except Exception as e:
        print(f"Errore save_impresa: {e}")
        return None


def delete_impresa(impresa_id: str) -> bool:
    """Elimina un'impresa"""
    client = get_supabase_client()
    if not client:
        return False
    
    try:
        client.table('imprese').delete().eq('id', impresa_id).execute()
        return True
    except Exception as e:
        print(f"Errore delete_impresa: {e}")
        return False


def set_default_impresa(user_id: str, impresa_id: str) -> bool:
    """Imposta un'impresa come predefinita"""
    client = get_supabase_client()
    if not client:
        return False
    
    try:
        # Prima rimuovi il flag da tutte
        client.table('imprese').update({'is_default': False}).eq('user_id', user_id).execute()
        # Poi imposta quella selezionata
        client.table('imprese').update({'is_default': True}).eq('id', impresa_id).execute()
        return True
    except Exception as e:
        print(f"Errore set_default_impresa: {e}")
        return False


def get_default_impresa(user_id: str) -> dict:
    """Recupera l'impresa predefinita dell'utente"""
    client = get_supabase_client()
    if not client:
        return None
    
    try:
        response = client.table('imprese').select('*').eq('user_id', user_id).eq('is_default', True).single().execute()
        return response.data
    except:
        # Se non c'è default, prendi la prima
        imprese = get_user_imprese(user_id)
        return imprese[0] if imprese else None


# ============================================================================
# GESTIONE STORICO POS
# ============================================================================

def save_pos_generato(user_id: str, impresa_id: str, cantiere_data: dict, lavorazioni: list, nome_file: str) -> bool:
    """Salva un POS generato nello storico"""
    client = get_supabase_client()
    if not client:
        return False
    
    try:
        client.table('pos_generati').insert({
            'user_id': user_id,
            'impresa_id': impresa_id,
            'cantiere_indirizzo': cantiere_data.get('indirizzo', ''),
            'cantiere_committente': cantiere_data.get('committente', ''),
            'cantiere_durata': cantiere_data.get('durata', ''),
            'lavorazioni': lavorazioni,
            'nome_file': nome_file
        }).execute()
        return True
    except Exception as e:
        print(f"Errore save_pos_generato: {e}")
        return False


def get_pos_history(user_id: str, limit: int = 20) -> list:
    """Recupera lo storico POS dell'utente"""
    client = get_supabase_client()
    if not client:
        return []
    
    try:
        response = client.table('pos_generati').select('*').eq('user_id', user_id).order('data_generazione', desc=True).limit(limit).execute()
        return response.data or []
    except Exception as e:
        print(f"Errore get_pos_history: {e}")
        return []


# ============================================================================
# GESTIONE LAVORATORI TEMPLATE
# ============================================================================

def get_lavoratori_template(impresa_id: str) -> list:
    """Recupera i lavoratori salvati per un'impresa"""
    client = get_supabase_client()
    if not client:
        return []
    
    try:
        response = client.table('lavoratori_template').select('*').eq('impresa_id', impresa_id).execute()
        return response.data or []
    except Exception as e:
        print(f"Errore get_lavoratori_template: {e}")
        return []


def save_lavoratori_template(impresa_id: str, lavoratori: list) -> bool:
    """Salva i lavoratori come template per un'impresa"""
    client = get_supabase_client()
    if not client:
        return False
    
    try:
        # Prima elimina i vecchi
        client.table('lavoratori_template').delete().eq('impresa_id', impresa_id).execute()
        
        # Poi inserisci i nuovi
        for lav in lavoratori:
            if lav.get('nome'):
                client.table('lavoratori_template').insert({
                    'impresa_id': impresa_id,
                    'nome': lav.get('nome', ''),
                    'mansione': lav.get('mansione', ''),
                    'formazione': lav.get('formazione', ''),
                    'idoneita_sanitaria': lav.get('idoneita', '')
                }).execute()
        return True
    except Exception as e:
        print(f"Errore save_lavoratori_template: {e}")
        return False


# ============================================================================
# GESTIONE ATTREZZATURE TEMPLATE
# ============================================================================

def get_attrezzature_template(impresa_id: str) -> list:
    """Recupera le attrezzature salvate per un'impresa"""
    client = get_supabase_client()
    if not client:
        return []
    
    try:
        response = client.table('attrezzature_template').select('*').eq('impresa_id', impresa_id).execute()
        return response.data or []
    except Exception as e:
        print(f"Errore get_attrezzature_template: {e}")
        return []


def save_attrezzature_template(impresa_id: str, attrezzature: list) -> bool:
    """Salva le attrezzature come template per un'impresa"""
    client = get_supabase_client()
    if not client:
        return False
    
    try:
        # Prima elimina i vecchi
        client.table('attrezzature_template').delete().eq('impresa_id', impresa_id).execute()
        
        # Poi inserisci i nuovi
        for attr in attrezzature:
            if attr.get('nome'):
                client.table('attrezzature_template').insert({
                    'impresa_id': impresa_id,
                    'nome': attr.get('nome', ''),
                    'marca': attr.get('marca', ''),
                    'matricola': attr.get('matricola', ''),
                    'ultima_verifica': attr.get('verifica', '')
                }).execute()
        return True
    except Exception as e:
        print(f"Errore save_attrezzature_template: {e}")
        return False


# ============================================================================
# UTILITY
# ============================================================================

def impresa_to_ditta_dict(impresa: dict) -> dict:
    """Converte un record impresa dal DB al formato ditta usato nell'app"""
    if not impresa:
        return {}
    
    return {
        'ragione_sociale': impresa.get('ragione_sociale', ''),
        'piva_cf': impresa.get('piva_cf', ''),
        'indirizzo': impresa.get('indirizzo', ''),
        'telefono': impresa.get('telefono', ''),
        'datore_lavoro': impresa.get('datore_lavoro', ''),
        'rspp_autonomo': impresa.get('rspp_autonomo', True),
        'rspp': impresa.get('rspp', ''),
        'medico': impresa.get('medico_competente', ''),
        'rls_tipo': impresa.get('rls_tipo', 'non_eletto'),
        'rls_nome': impresa.get('rls_nome', ''),
        'rls_territoriale': impresa.get('rls_territoriale', ''),
        'codice_ateco': impresa.get('codice_ateco', ''),
        'num_dipendenti': impresa.get('num_dipendenti', ''),
        '_impresa_id': impresa.get('id'),  # Riferimento per salvare
        '_addetto_ps': impresa.get('addetto_ps', ''),
        '_addetto_antincendio': impresa.get('addetto_antincendio', '')
    }


def ditta_to_impresa_dict(ditta: dict, addetti: dict = None) -> dict:
    """Converte il formato ditta dell'app al formato impresa per il DB"""
    data = {
        'ragione_sociale': ditta.get('ragione_sociale', ''),
        'piva_cf': ditta.get('piva_cf', ''),
        'indirizzo': ditta.get('indirizzo', ''),
        'telefono': ditta.get('telefono', ''),
        'datore_lavoro': ditta.get('datore_lavoro', ''),
        'rspp_autonomo': ditta.get('rspp_autonomo', True),
        'rspp': ditta.get('rspp', ''),
        'medico_competente': ditta.get('medico', ''),
        'rls_tipo': ditta.get('rls_tipo', 'non_eletto'),
        'rls_nome': ditta.get('rls_nome', ''),
        'rls_territoriale': ditta.get('rls_territoriale', ''),
        'codice_ateco': ditta.get('codice_ateco', ''),
        'num_dipendenti': ditta.get('num_dipendenti', '')
    }
    
    if addetti:
        data['addetto_ps'] = addetti.get('primo_soccorso', '')
        data['addetto_antincendio'] = addetti.get('antincendio', '')
    
    # Se c'è un ID, includilo per l'update
    if ditta.get('_impresa_id'):
        data['id'] = ditta['_impresa_id']
    
    return data
