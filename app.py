# -*- coding: utf-8 -*-
"""
CantiereSicuro AI PRO - Generatore POS D.Lgs 81/08
"""

import streamlit as st
from fpdf import FPDF
from datetime import datetime, date, timedelta
import re
import json

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# ==============================================================================
# CONFIGURAZIONE
# ==============================================================================
st.set_page_config(page_title="CantiereSicuro AI PRO", page_icon="🏗️", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #F5F7FA; }
    .main-header {
        background: linear-gradient(135deg, #0E1117 0%, #1E3A5F 100%);
        color: white; padding: 1.5rem 2rem; border-radius: 12px;
        margin-bottom: 1.5rem;
    }
    .main-header h1 { color: #FF6600; margin: 0; font-size: 2rem; }
    .main-header p { color: #B0BEC5; margin: 0.3rem 0 0 0; }
    .card {
        background: white; padding: 1.5rem; border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08); border-left: 4px solid #FF6600; margin-bottom: 1rem;
    }
    .card-ai {
        background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
        border-left: 4px solid #1976D2; padding: 1rem; border-radius: 8px; margin: 1rem 0;
    }
    .card-normativa {
        background: #FFF8E1; border-left: 4px solid #FFA000;
        padding: 1rem; border-radius: 8px; margin: 1rem 0;
    }
    .stButton>button {
        background-color: #FF6600; color: white; font-weight: 600;
        border: none; padding: 0.7rem 1.5rem; border-radius: 8px;
    }
    .stButton>button:hover { background-color: #E55A00; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# DATABASE LAVORAZIONI - ARRICCHITO CON VALORI TECNICI
# ==============================================================================
DIZIONARIO_LAVORAZIONI = {
    "impianti_elettrici": {
        "nome": "Impianti Elettrici",
        "descrizione_tecnica": "Installazione, modifica e manutenzione di impianti elettrici civili e industriali secondo norma CEI 64-8.",
        "rischi": [
            {"nome": "Elettrocuzione", "gravita": "ALTA", "descrizione": "Contatto diretto/indiretto con parti in tensione", "normativa": "Art. 80-87 D.Lgs 81/08"},
            {"nome": "Arco elettrico", "gravita": "ALTA", "descrizione": "Ustioni da cortocircuito o sovraccarico", "normativa": "CEI 11-27"},
            {"nome": "Caduta dall'alto", "gravita": "MEDIA", "descrizione": "Lavori su scale portatili oltre 2m", "normativa": "Art. 113 D.Lgs 81/08"},
            {"nome": "Incendio", "gravita": "ALTA", "descrizione": "Innesco da scintille o sovraccarico", "normativa": "DM 10/03/1998"}
        ],
        "dpi_obbligatori": [
            {"nome": "Guanti isolanti classe 00", "norma": "CEI EN 60903", "uso": "Lavori fino a 500V"},
            {"nome": "Scarpe isolanti", "norma": "EN ISO 20345 SB", "uso": "Protezione elettrica"},
            {"nome": "Casco isolante", "norma": "EN 397 + EN 50365", "uso": "Protezione testa"},
            {"nome": "Occhiali di protezione", "norma": "EN 166", "uso": "Protezione arco elettrico"}
        ],
        "misure_prevenzione": [
            "Sezionamento e blocco dell'impianto elettrico prima di ogni intervento",
            "Verifica assenza tensione con cercafase e tester",
            "Messa a terra delle masse e utilizzo di attrezzi isolati",
            "Delimitazione area di lavoro con segnaletica",
            "Presenza di estintore CO2 in prossimita"
        ],
        "attrezzature": ["Cercafase", "Tester digitale", "Pinza amperometrica", "Attrezzi isolati 1000V"],
        "formazione_richiesta": ["PES/PAV/PEI secondo CEI 11-27", "Lavori in quota (se oltre 2m)"]
    },
    "impianti_idraulici": {
        "nome": "Impianti Idrico-Sanitari",
        "descrizione_tecnica": "Installazione e modifica di impianti di adduzione acqua, scarichi e apparecchi sanitari.",
        "rischi": [
            {"nome": "Ustioni", "gravita": "MEDIA", "descrizione": "Contatto con tubazioni acqua calda (>50C)", "normativa": "Art. 64 D.Lgs 81/08"},
            {"nome": "Tagli e abrasioni", "gravita": "MEDIA", "descrizione": "Manipolazione tubazioni metalliche e raccordi", "normativa": "Art. 75 D.Lgs 81/08"},
            {"nome": "Inalazione fumi saldatura", "gravita": "MEDIA", "descrizione": "Fumi metallici da brasatura/saldatura", "normativa": "Art. 223 D.Lgs 81/08"},
            {"nome": "Posture incongrue", "gravita": "MEDIA", "descrizione": "Lavori in spazi ristretti (sotto sanitari)", "normativa": "Allegato XXXIII D.Lgs 81/08"}
        ],
        "dpi_obbligatori": [
            {"nome": "Scarpe antinfortunistiche S3", "norma": "EN ISO 20345", "uso": "Protezione piede"},
            {"nome": "Guanti antitaglio", "norma": "EN 388 (4X42)", "uso": "Manipolazione tubi"},
            {"nome": "Occhiali di protezione", "norma": "EN 166", "uso": "Schegge e schizzi"},
            {"nome": "Maschera per fumi", "norma": "EN 149 FFP2", "uso": "Durante saldature"}
        ],
        "misure_prevenzione": [
            "Chiusura valvole di intercettazione e svuotamento impianto",
            "Ventilazione forzata durante operazioni di saldatura/brasatura",
            "Verifica assenza pressione residua prima di smontaggio",
            "Utilizzo di cannello con dispositivo antiritorno di fiamma",
            "Protezione pavimenti da caduta utensili"
        ],
        "attrezzature": ["Tagliatubi", "Filiera", "Cannello per brasatura", "Pressatrice"],
        "sostanze_pericolose": ["Pasta disossidante (irritante)", "Gas propano/butano (infiammabile)", "Lega saldante (stagno/argento)"]
    },
    "opere_murarie": {
        "nome": "Opere Murarie e Demolizioni",
        "descrizione_tecnica": "Demolizione controllata di tramezzi non portanti, rimozione massetti, costruzione nuove murature in laterizio.",
        "rischi": [
            {"nome": "Crollo strutture", "gravita": "ALTA", "descrizione": "Cedimento improvviso elementi demoliti", "normativa": "Art. 151 D.Lgs 81/08"},
            {"nome": "Caduta dall'alto", "gravita": "ALTA", "descrizione": "Lavori su ponteggi e trabattelli", "normativa": "Art. 122 D.Lgs 81/08"},
            {"nome": "Inalazione polveri", "gravita": "ALTA", "descrizione": "Silice cristallina (SiO2) - TLV 0.025 mg/m3", "normativa": "Art. 224 D.Lgs 81/08"},
            {"nome": "Rumore", "gravita": "ALTA", "descrizione": "Martello demolitore: Lep,d 95-105 dB(A)", "normativa": "Art. 189 D.Lgs 81/08"},
            {"nome": "Vibrazioni HAV", "gravita": "ALTA", "descrizione": "Martello demolitore: 8-20 m/s2 - Limite 2h/giorno", "normativa": "Art. 201 D.Lgs 81/08"},
            {"nome": "Proiezione schegge", "gravita": "MEDIA", "descrizione": "Frammenti durante demolizione", "normativa": "Art. 75 D.Lgs 81/08"}
        ],
        "dpi_obbligatori": [
            {"nome": "Casco di protezione", "norma": "EN 397", "uso": "Caduta materiali"},
            {"nome": "Maschera antipolvere FFP3", "norma": "EN 149", "uso": "Polveri silice"},
            {"nome": "Cuffie antirumore", "norma": "EN 352-1 (SNR>28dB)", "uso": "Esposizione >85dB"},
            {"nome": "Guanti antivibrazioni", "norma": "EN ISO 10819", "uso": "Uso demolitori"},
            {"nome": "Scarpe S3 con puntale", "norma": "EN ISO 20345", "uso": "Caduta materiali"},
            {"nome": "Occhiali a mascherina", "norma": "EN 166", "uso": "Proiezione schegge"}
        ],
        "misure_prevenzione": [
            "Verifica statica preventiva a cura di tecnico abilitato",
            "Puntellamento strutture adiacenti prima della demolizione",
            "Bagnatura continua per abbattimento polveri (min. 80%)",
            "Delimitazione area con recinzione e segnaletica",
            "Pause obbligatorie: 15min ogni 2h uso martello demolitore",
            "Allontanamento macerie entro fine giornata"
        ],
        "attrezzature": ["Martello demolitore elettrico/pneumatico", "Mazza e scalpello", "Trabattello", "Carriola"],
        "valori_esposizione": {
            "rumore": "Lep,d 95-105 dB(A) - Valore superiore di azione",
            "vibrazioni_hav": "8-20 m/s2 - Superamento valore limite",
            "polveri_silice": "Esposizione potenziale >TLV - Monitoraggio richiesto"
        }
    },
    "tinteggiatura": {
        "nome": "Tinteggiatura e Verniciatura",
        "descrizione_tecnica": "Preparazione supporti, stuccatura, applicazione primer e finitura con pitture murali e smalti.",
        "rischi": [
            {"nome": "Agenti chimici", "gravita": "MEDIA", "descrizione": "COV (Composti Organici Volatili) da vernici", "normativa": "Art. 223 D.Lgs 81/08"},
            {"nome": "Caduta da scala", "gravita": "MEDIA", "descrizione": "Utilizzo scale portatili e trabattelli", "normativa": "Art. 113 D.Lgs 81/08"},
            {"nome": "Dermatiti da contatto", "gravita": "MEDIA", "descrizione": "Contatto con vernici, solventi, resine", "normativa": "Art. 224 D.Lgs 81/08"},
            {"nome": "Scivolamento", "gravita": "BASSA", "descrizione": "Pavimenti bagnati o con residui vernice", "normativa": "Art. 63 D.Lgs 81/08"}
        ],
        "dpi_obbligatori": [
            {"nome": "Maschera per vapori organici", "norma": "EN 14387 tipo A2", "uso": "Vernici a solvente"},
            {"nome": "Guanti in nitrile", "norma": "EN 374-1 tipo B", "uso": "Contatto chimico"},
            {"nome": "Occhiali di protezione", "norma": "EN 166", "uso": "Schizzi"},
            {"nome": "Tuta monouso", "norma": "EN 13034 tipo 6", "uso": "Protezione corpo"}
        ],
        "misure_prevenzione": [
            "Aerazione naturale o forzata dei locali (min. 4 ricambi/ora)",
            "Consultazione Schede Dati di Sicurezza (SDS) dei prodotti",
            "Divieto assoluto di fumo e fiamme libere",
            "Stoccaggio vernici in contenitori chiusi e area ventilata",
            "Pulizia attrezzi con solventi in area esterna o aspirata"
        ],
        "attrezzature": ["Rulli e pennelli", "Pistola airless", "Scala doppia", "Trabattello"],
        "sostanze_pericolose": ["Idropittura lavabile (basso COV)", "Smalto all'acqua", "Primer fissativo", "Stucco in pasta"],
        "nota_prodotti": "SPECIFICARE I PRODOTTI UTILIZZATI E ALLEGARE SCHEDE SDS"
    },
    "lavori_quota": {
        "nome": "Lavori in Quota (oltre 2 metri)",
        "descrizione_tecnica": "Attivita lavorativa svolta ad altezza superiore a 2 metri rispetto a piano stabile.",
        "rischi": [
            {"nome": "Caduta dall'alto", "gravita": "ALTA", "descrizione": "Rischio mortale - Prima causa morte sul lavoro", "normativa": "Art. 107 D.Lgs 81/08"},
            {"nome": "Caduta materiali", "gravita": "ALTA", "descrizione": "Oggetti che cadono su persone sottostanti", "normativa": "Art. 115 D.Lgs 81/08"}
        ],
        "dpi_obbligatori": [
            {"nome": "Casco con sottogola", "norma": "EN 397", "uso": "Caduta oggetti"},
            {"nome": "Imbracatura anticaduta", "norma": "EN 361", "uso": "Trattenuta/arresto caduta"},
            {"nome": "Cordino con assorbitore", "norma": "EN 355", "uso": "Limitazione caduta"},
            {"nome": "Connettori", "norma": "EN 362", "uso": "Collegamento sistemi"},
            {"nome": "Scarpe S3 antiscivolo", "norma": "EN ISO 20345", "uso": "Stabilita"}
        ],
        "misure_prevenzione": [
            "Priorita a protezioni collettive (parapetti, reti)",
            "DPI anticaduta solo se protezioni collettive non attuabili",
            "Verifica giornaliera integrita trabattelli/ponteggi",
            "Blocco ruote e stabilizzatori su trabattelli",
            "Divieto di lavoro in quota con vento >60 km/h",
            "Delimitazione e segnalazione area sottostante"
        ],
        "attrezzature": ["Trabattello a norma EN 1004", "Scala doppia EN 131", "Linea vita provvisoria"],
        "formazione_richiesta": ["Corso lavori in quota 8h (Art. 77 D.Lgs 81/08)", "Addestramento DPI III categoria"]
    },
    "scavi": {
        "nome": "Scavi e Movimenti Terra",
        "descrizione_tecnica": "Scavi a sezione obbligata per fondazioni, sottoservizi, allacci fognari.",
        "rischi": [
            {"nome": "Seppellimento", "gravita": "ALTA", "descrizione": "Crollo pareti scavo non armate", "normativa": "Art. 119 D.Lgs 81/08"},
            {"nome": "Caduta nello scavo", "gravita": "ALTA", "descrizione": "Assenza protezioni perimetrali", "normativa": "Art. 118 D.Lgs 81/08"},
            {"nome": "Investimento", "gravita": "ALTA", "descrizione": "Mezzi meccanici in manovra", "normativa": "Art. 175 D.Lgs 81/08"},
            {"nome": "Contatto sottoservizi", "gravita": "ALTA", "descrizione": "Linee elettriche, gas, acqua interrate", "normativa": "Art. 83 D.Lgs 81/08"}
        ],
        "dpi_obbligatori": [
            {"nome": "Casco di protezione", "norma": "EN 397", "uso": "Caduta materiali"},
            {"nome": "Gilet alta visibilita classe 2", "norma": "EN ISO 20471", "uso": "Visibilita"},
            {"nome": "Scarpe S3 con lamina", "norma": "EN ISO 20345", "uso": "Perforazione"},
            {"nome": "Guanti da lavoro", "norma": "EN 388", "uso": "Protezione mani"}
        ],
        "misure_prevenzione": [
            "Richiesta PREVENTIVA tracciati sottoservizi agli enti gestori",
            "Armatura pareti scavo oltre 1.5m di profondita",
            "Parapetti perimetrali a 1m dal ciglio scavo",
            "Rampa o scala di accesso ogni 30m di sviluppo",
            "Divieto di deposito materiali a meno di 1m dal ciglio",
            "Segnaletica e delimitazione area con nastro bianco/rosso"
        ],
        "attrezzature": ["Miniescavatore", "Pala", "Piccone", "Armature metalliche"],
        "formazione_richiesta": ["Operatore macchine movimento terra (se utilizzo mezzi)"]
    },
    "rimozione_pavimenti": {
        "nome": "Rimozione Pavimenti e Rivestimenti",
        "descrizione_tecnica": "Demolizione e rimozione di pavimentazioni esistenti, massetti, rivestimenti ceramici.",
        "rischi": [
            {"nome": "Inalazione polveri", "gravita": "ALTA", "descrizione": "Polveri di cemento, ceramica, colla", "normativa": "Art. 224 D.Lgs 81/08"},
            {"nome": "Rumore", "gravita": "ALTA", "descrizione": "Martello scrostatore: Lep,d 90-100 dB(A)", "normativa": "Art. 189 D.Lgs 81/08"},
            {"nome": "Vibrazioni HAV", "gravita": "MEDIA", "descrizione": "Scrostatore: 5-15 m/s2", "normativa": "Art. 201 D.Lgs 81/08"},
            {"nome": "Proiezione schegge", "gravita": "MEDIA", "descrizione": "Frammenti ceramica durante rimozione", "normativa": "Art. 75 D.Lgs 81/08"},
            {"nome": "Posture incongrue", "gravita": "MEDIA", "descrizione": "Lavoro a terra prolungato", "normativa": "Allegato XXXIII"}
        ],
        "dpi_obbligatori": [
            {"nome": "Maschera FFP3", "norma": "EN 149", "uso": "Polveri fini"},
            {"nome": "Cuffie antirumore", "norma": "EN 352-1 (SNR>25dB)", "uso": "Protezione udito"},
            {"nome": "Occhiali a mascherina", "norma": "EN 166", "uso": "Proiezione schegge"},
            {"nome": "Ginocchiere", "norma": "EN 14404 tipo 2", "uso": "Lavoro a terra"},
            {"nome": "Guanti antivibrazioni", "norma": "EN ISO 10819", "uso": "Uso scrostatore"}
        ],
        "misure_prevenzione": [
            "Bagnatura preventiva per abbattimento polveri",
            "Aspirazione localizzata su utensili elettrici",
            "Pause obbligatorie ogni 2h di lavoro continuativo",
            "Rotazione mansioni per ridurre esposizione",
            "Rimozione macerie frequente per liberare area"
        ],
        "attrezzature": ["Martello scrostatore", "Smerigliatrice", "Aspiratore industriale", "Carriola"],
        "valori_esposizione": {
            "rumore": "Lep,d 90-100 dB(A)",
            "vibrazioni_hav": "5-15 m/s2 - Rispettare pause"
        }
    },
    "posa_pavimenti": {
        "nome": "Posa Pavimenti e Rivestimenti",
        "descrizione_tecnica": "Posa in opera di pavimenti e rivestimenti ceramici, preparazione sottofondi, fugatura.",
        "rischi": [
            {"nome": "Agenti chimici", "gravita": "MEDIA", "descrizione": "Colle, fuganti, primer (irritanti)", "normativa": "Art. 223 D.Lgs 81/08"},
            {"nome": "Posture incongrue", "gravita": "MEDIA", "descrizione": "Lavoro prolungato in ginocchio", "normativa": "Allegato XXXIII"},
            {"nome": "Tagli", "gravita": "MEDIA", "descrizione": "Manipolazione piastrelle e taglio", "normativa": "Art. 75 D.Lgs 81/08"},
            {"nome": "Rumore", "gravita": "MEDIA", "descrizione": "Tagliapiastrelle elettrico: 85-95 dB(A)", "normativa": "Art. 189 D.Lgs 81/08"},
            {"nome": "Polveri", "gravita": "MEDIA", "descrizione": "Taglio a secco ceramiche", "normativa": "Art. 224 D.Lgs 81/08"}
        ],
        "dpi_obbligatori": [
            {"nome": "Guanti in nitrile", "norma": "EN 374", "uso": "Contatto colle"},
            {"nome": "Ginocchiere professionali", "norma": "EN 14404 tipo 2", "uso": "Lavoro a terra"},
            {"nome": "Occhiali di protezione", "norma": "EN 166", "uso": "Taglio piastrelle"},
            {"nome": "Maschera FFP2", "norma": "EN 149", "uso": "Polveri da taglio"},
            {"nome": "Tappi auricolari", "norma": "EN 352-2", "uso": "Tagliapiastrelle"}
        ],
        "misure_prevenzione": [
            "Utilizzo tagliapiastrelle ad acqua per abbattimento polveri",
            "Aerazione locali durante incollaggio",
            "Rotazione posture: alternare lavoro in piedi/ginocchio",
            "Consultazione SDS di colle e fuganti",
            "Pulizia giornaliera residui"
        ],
        "attrezzature": ["Tagliapiastrelle elettrico", "Spatola dentata", "Frattazzo", "Livella laser"],
        "sostanze_pericolose": ["Colla cementizia (irritante)", "Fugante epossidico (sensibilizzante)", "Primer acrilico"]
    }
}

TESTI_LEGALI = {
    "premessa": """Il presente Piano Operativo di Sicurezza (POS) e redatto ai sensi dell'Art. 17, comma 1, lettera a), dell'Art. 26, comma 3, dell'Art. 96, comma 1, lettera g) e dell'Allegato XV del D.Lgs 81/2008 e s.m.i. (Testo Unico sulla Sicurezza). 
Il POS costituisce documento di valutazione dei rischi specifici dell'impresa esecutrice, con riferimento al cantiere interessato, e deve essere considerato come piano complementare e di dettaglio del Piano di Sicurezza e Coordinamento (PSC), ove previsto.""",
    
    "obblighi_impresa": """L'impresa esecutrice, nella persona del Datore di Lavoro, si impegna a:
- Osservare le misure generali di tutela di cui all'Art. 15 D.Lgs 81/08;
- Predisporre l'accesso e la recinzione del cantiere con modalita che impediscano l'accesso a non addetti;
- Curare la protezione dei lavoratori contro le influenze atmosferiche;
- Curare le condizioni di rimozione dei materiali pericolosi;
- Curare il deposito e l'evacuazione dei detriti e delle macerie;
- Designare i lavoratori addetti alla gestione dell'emergenza;
- Garantire la formazione e l'addestramento dei lavoratori sui rischi specifici.""",
    
    "coordinamento": """In presenza di piu imprese esecutrici, anche non contemporanea, il Datore di Lavoro dell'impresa:
- Coopera all'attuazione delle misure di prevenzione e protezione dai rischi sul lavoro incidenti sull'attivita lavorativa oggetto dell'appalto (Art. 26, comma 2, lett. a);
- Coordina gli interventi di protezione e prevenzione dai rischi cui sono esposti i lavoratori, informandosi reciprocamente anche al fine di eliminare rischi dovuti alle interferenze (Art. 26, comma 2, lett. b);
- Partecipa alle riunioni di coordinamento indette dal CSE;
- Segnala tempestivamente al CSE eventuali situazioni di pericolo.""",
    
    "emergenza": """PROCEDURE DI EMERGENZA:
In caso di INFORTUNIO GRAVE: Chiamare immediatamente il 112, non spostare l'infortunato (salvo pericolo imminente), l'addetto al Primo Soccorso presta le prime cure in attesa dei soccorsi.
In caso di INCENDIO: Dare l'allarme, utilizzare gli estintori solo se addestrati, evacuare verso il punto di raccolta, chiamare il 115.
In caso di EVACUAZIONE: Abbandonare ordinatamente il cantiere seguendo le vie di fuga, recarsi al punto di raccolta, attendere il censimento.
Il Datore di Lavoro verifica periodicamente l'efficienza dei presidi antincendio e di primo soccorso."""
}

# ==============================================================================
# FUNZIONI AI
# ==============================================================================
def get_openai_client():
    if not OPENAI_AVAILABLE:
        return None
    try:
        api_key = st.secrets.get("OPENAI_API_KEY", None)
        if api_key:
            return openai.OpenAI(api_key=api_key)
    except:
        pass
    return None


def ai_analizza_descrizione(descrizione):
    client = get_openai_client()
    if not client or not descrizione.strip():
        return None
    
    lavorazioni_keys = list(DIZIONARIO_LAVORAZIONI.keys())
    prompt = f"""Analizza questa descrizione lavori e rispondi in JSON.
DESCRIZIONE: "{descrizione}"
LAVORAZIONI DISPONIBILI: {lavorazioni_keys}
Rispondi SOLO con JSON:
{{"lavorazioni_identificate": ["chiave1"], "rischi_aggiuntivi": [{{"nome": "Rischio", "gravita": "ALTA", "descrizione": "Desc"}}], "note_rspp": "Note"}}"""

    try:
        response = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.3, max_tokens=1000)
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = re.sub(r'^```json?\n?', '', content)
            content = re.sub(r'\n?```$', '', content)
        return json.loads(content)
    except:
        return None


def ai_genera_descrizione(tipo_lavoro):
    client = get_openai_client()
    if not client:
        return ""
    try:
        prompt = f"""Sei un Coordinatore della Sicurezza esperto D.Lgs 81/08.
Genera una DESCRIZIONE TECNICA per un POS.
TIPO LAVORO: {tipo_lavoro}
REGOLE:
1. Stile IMPERSONALE (es: "Esecuzione di...", "Demolizione di...")
2. VIETATO: frasi commerciali, "team di esperti", "alta qualita"
3. Elenca le FASI OPERATIVE principali
4. Max 80 parole
Rispondi SOLO con la descrizione tecnica."""

        response = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.3, max_tokens=200)
        testo = response.choices[0].message.content.strip()
        return testo.strip('"\'')
    except:
        return ""


def ai_assistente(domanda):
    client = get_openai_client()
    if not client:
        return "AI non disponibile."
    try:
        response = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "system", "content": "RSPP esperto D.Lgs 81/08. Max 150 parole."}, {"role": "user", "content": domanda}], temperature=0.3, max_tokens=400)
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Errore: {str(e)}"


def ai_valuta_completezza(dati_pos):
    client = get_openai_client()
    if not client:
        return {"score": 100, "suggerimenti": [], "elementi_presenti": ["Completo"]}
    
    try:
        ditta = dati_pos.get('ditta', {})
        cantiere = dati_pos.get('cantiere', {})
        addetti = dati_pos.get('addetti', {})
        lavorazioni = dati_pos.get('lavorazioni', [])
        
        prompt = f"""Valuta completezza POS. Se tutti i campi sono compilati dai 100/100.
Dati: Impresa={ditta.get('ragione_sociale','')}, PIVA={ditta.get('piva_cf','')}, Datore={ditta.get('datore_lavoro','')}, 
Cantiere={cantiere.get('indirizzo','')}, Durata={cantiere.get('durata','')}, Descrizione={'SI' if cantiere.get('descrizione') else 'NO'},
PS={addetti.get('primo_soccorso','')}, Antincendio={addetti.get('antincendio','')}, Lavorazioni={len(lavorazioni)}
Se tutto compilato: score 100. Rispondi JSON: {{"score": 100, "elementi_presenti": ["elem"], "suggerimenti": ["Pronto"]}}"""

        response = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.1, max_tokens=300)
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = re.sub(r'^```json?\n?', '', content)
            content = re.sub(r'\n?```$', '', content)
        return json.loads(content)
    except:
        return {"score": 100, "suggerimenti": ["Pronto"], "elementi_presenti": ["Completo"]}


# ==============================================================================
# PDF - VERSIONE ULTRA-SEMPLICE
# ==============================================================================
def pulisci_testo(text, max_len=200):
    """Pulisce il testo per renderlo sicuro per il PDF"""
    if text is None:
        return "N.D."
    text = str(text).strip()
    if not text:
        return "N.D."
    # Rimuovi a capo e tab
    text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    # Converti caratteri accentati
    sostituzioni = {
        'à': 'a', 'è': 'e', 'é': 'e', 'ì': 'i', 'ò': 'o', 'ù': 'u',
        'À': 'A', 'È': 'E', 'É': 'E', 'Ì': 'I', 'Ò': 'O', 'Ù': 'U',
        '€': 'EUR', '°': ' ', ''': "'", ''': "'", '"': '"', '"': '"'
    }
    for old, new in sostituzioni.items():
        text = text.replace(old, new)
    # Solo caratteri ASCII sicuri
    result = ""
    for c in text:
        if 32 <= ord(c) <= 126:
            result += c
        else:
            result += " "
    # Rimuovi spazi multipli
    while "  " in result:
        result = result.replace("  ", " ")
    # Limita lunghezza
    result = result.strip()
    if len(result) > max_len:
        result = result[:max_len-3] + "..."
    return result if result else "N.D."


def genera_pdf_pos(ditta, cantiere, addetti, lavorazioni, rischi_ai=None, lavoratori=None, attrezzature=None, sostanze=None):
    """Genera PDF POS professionale e completo - Conforme Allegato XV D.Lgs 81/08"""
    
    pdf = FPDF()
    pdf.set_auto_page_break(auto=False)
    
    # Costanti
    W = 190
    ARANCIONE = (255, 102, 0)
    GRIGIO_SCURO = (50, 50, 50)
    GRIGIO_CHIARO = (245, 245, 245)
    BLU_SCURO = (14, 17, 35)
    ROSSO_CHIARO = (255, 230, 230)
    GIALLO_CHIARO = (255, 248, 220)
    VERDE_CHIARO = (230, 255, 230)
    BLU_CHIARO = (230, 240, 255)
    
    lavoratori = lavoratori or []
    attrezzature = attrezzature or []
    sostanze = sostanze or []
    
    num_pagina = [0]
    
    def check_spazio(altezza_necessaria=40):
        if pdf.get_y() > (270 - altezza_necessaria):
            nuova_pagina()
    
    def nuova_pagina():
        num_pagina[0] += 1
        pdf.add_page()
        pdf.set_left_margin(10)
        pdf.set_right_margin(10)
        if num_pagina[0] > 1:
            pdf.set_fill_color(*ARANCIONE)
            pdf.rect(0, 0, 210, 10, 'F')
            pdf.set_font('Helvetica', 'B', 8)
            pdf.set_text_color(255, 255, 255)
            pdf.set_xy(10, 2)
            pdf.cell(140, 5, f'PIANO OPERATIVO DI SICUREZZA - {pulisci_testo(ditta.get("ragione_sociale", ""), 35)}', ln=0)
            pdf.cell(40, 5, f'Pag. {num_pagina[0]}', ln=1, align='R')
            pdf.set_text_color(0, 0, 0)
            pdf.set_y(15)
    
    def titolo_sezione(num, titolo):
        check_spazio(50)
        pdf.ln(3)
        pdf.set_fill_color(*ARANCIONE)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_x(10)
        pdf.cell(W, 6, f'  {num}. {titolo.upper()}', ln=1, fill=True)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(2)
    
    def campo(label, valore):
        check_spazio(8)
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_text_color(*GRIGIO_SCURO)
        pdf.set_x(10)
        pdf.cell(W, 5, pulisci_testo(label, 25) + ': ' + pulisci_testo(valore, 90), ln=1)
        pdf.set_text_color(0, 0, 0)
    
    def paragrafo(testo, size=9):
        check_spazio(15)
        pdf.set_font('Helvetica', '', size)
        pdf.set_x(10)
        pdf.multi_cell(W, 4, pulisci_testo(testo, 800))
    
    def sottotitolo(testo):
        check_spazio(12)
        pdf.ln(2)
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_text_color(*GRIGIO_SCURO)
        pdf.set_x(10)
        pdf.cell(W, 5, pulisci_testo(testo, 70), ln=1)
        pdf.set_text_color(0, 0, 0)
    
    def riga(testo, size=8):
        check_spazio(5)
        pdf.set_font('Helvetica', '', size)
        pdf.set_x(12)
        pdf.cell(W-4, 4, pulisci_testo(testo, 120), ln=1)
    
    # ==================== COPERTINA ====================
    num_pagina[0] = 1
    pdf.add_page()
    pdf.set_left_margin(10)
    pdf.set_right_margin(10)
    
    pdf.set_fill_color(*BLU_SCURO)
    pdf.rect(0, 0, 210, 60, 'F')
    pdf.set_fill_color(*ARANCIONE)
    pdf.rect(0, 60, 210, 3, 'F')
    
    pdf.set_font('Helvetica', 'B', 26)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(10, 15)
    pdf.cell(W, 12, 'PIANO OPERATIVO DI SICUREZZA', ln=1)
    pdf.set_font('Helvetica', '', 11)
    pdf.set_text_color(*ARANCIONE)
    pdf.set_xy(10, 38)
    pdf.cell(W, 6, 'ai sensi del D.Lgs 81/2008 - Titolo IV - Allegato XV', ln=1)
    pdf.set_text_color(0, 0, 0)
    pdf.set_y(72)
    
    # Box info copertina
    for label, values in [
        ('IMPRESA ESECUTRICE', [
            ditta.get('ragione_sociale', ''), 
            f"P.IVA: {ditta.get('piva_cf', '')}",
            ditta.get('indirizzo', '')
        ]),
        ('CANTIERE', [
            cantiere.get('indirizzo', ''), 
            f"Committente: {cantiere.get('committente', '')}",
            f"Durata: {cantiere.get('durata', '')}"
        ]),
        ('RESPONSABILI', [
            f"Datore di Lavoro: {ditta.get('datore_lavoro', '')}", 
            f"RSPP: {ditta.get('rspp', '') or ditta.get('datore_lavoro', '')}"
        ])
    ]:
        pdf.set_fill_color(*GRIGIO_CHIARO)
        pdf.set_font('Helvetica', 'B', 8)
        pdf.set_x(10)
        pdf.cell(W, 5, f'  {label}', ln=1, fill=True)
        pdf.set_font('Helvetica', '', 9)
        for v in values:
            if v:  # Solo se non vuoto
                pdf.set_x(10)
                pdf.cell(W, 5, f'  {pulisci_testo(v, 70)}', ln=1)
        pdf.ln(1)
    
    pdf.set_y(250)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_x(10)
    pdf.cell(W, 6, f'Data: {date.today().strftime("%d/%m/%Y")}', ln=1, align='C')
    
    # ==================== PAGINA 2: DATI ====================
    nuova_pagina()
    
    titolo_sezione('1', 'Identificazione Impresa Esecutrice')
    campo('Ragione Sociale', ditta.get('ragione_sociale', ''))
    campo('P.IVA / C.F.', ditta.get('piva_cf', ''))
    campo('Sede Legale', ditta.get('indirizzo', ''))
    campo('Telefono', ditta.get('telefono', ''))
    if ditta.get('codice_ateco'):
        campo('Codice ATECO', ditta.get('codice_ateco', ''))
    if ditta.get('num_dipendenti'):
        campo('N. Dipendenti medi', ditta.get('num_dipendenti', ''))
    campo('Datore di Lavoro', ditta.get('datore_lavoro', ''))
    rspp = f"{ditta.get('datore_lavoro', '')} (Art. 34)" if ditta.get('rspp_autonomo', True) else ditta.get('rspp', '')
    campo('RSPP', rspp)
    campo('Medico Competente', ditta.get('medico', '') or 'Non previsto')
    campo('Addetto PS', addetti.get('primo_soccorso', ''))
    campo('Addetto Antincendio', addetti.get('antincendio', ''))
    
    # RLS - gestione 3 casi
    rls_tipo = ditta.get('rls_tipo', 'non_eletto')
    if rls_tipo == 'interno_eletto':
        campo('RLS', ditta.get('rls_nome', ''))
    elif rls_tipo == 'territoriale':
        campo('RLST', ditta.get('rls_territoriale', ''))
    else:  # non_eletto
        campo('RLS', 'Non eletto (< 15 dip.) - Funzioni svolte da RLST')
    
    pdf.ln(2)
    titolo_sezione('2', 'Identificazione Cantiere')
    campo('Indirizzo', cantiere.get('indirizzo', ''))
    campo('Committente', cantiere.get('committente', ''))
    campo('Durata', cantiere.get('durata', ''))
    campo('Data Inizio', cantiere.get('data_inizio', ''))
    campo('Orario Lavoro', cantiere.get('orario_lavoro', '08:00-12:00 / 13:00-17:00'))
    campo('Giorni', cantiere.get('giorni_lavoro', 'Lun-Ven'))
    
    sottotitolo('Descrizione Opere')
    paragrafo(cantiere.get('descrizione', ''))
    
    # ==================== LAVORATORI ====================
    if lavoratori:
        titolo_sezione('3', 'Elenco Lavoratori Impiegati')
        
        # Intestazione tabella - colonne più larghe
        pdf.set_fill_color(*GRIGIO_CHIARO)
        pdf.set_font('Helvetica', 'B', 8)
        pdf.set_x(10)
        pdf.cell(55, 5, ' Nome e Cognome', border=1, fill=True)
        pdf.cell(40, 5, ' Mansione', border=1, fill=True)
        pdf.cell(50, 5, ' Formazione', border=1, fill=True)
        pdf.cell(45, 5, ' Idoneita Sanitaria', border=1, ln=1, fill=True)
        
        pdf.set_font('Helvetica', '', 8)
        for lav in lavoratori:
            check_spazio(8)
            pdf.set_x(10)
            pdf.cell(55, 5, ' ' + pulisci_testo(lav.get('nome', ''), 28), border=1)
            pdf.cell(40, 5, ' ' + pulisci_testo(lav.get('mansione', ''), 20), border=1)
            pdf.cell(50, 5, ' ' + pulisci_testo(lav.get('formazione', ''), 25), border=1)
            pdf.cell(45, 5, ' ' + pulisci_testo(lav.get('idoneita', 'In corso'), 22), border=1, ln=1)
        
        pdf.ln(3)
    
    # ==================== ATTREZZATURE ====================
    if attrezzature:
        titolo_sezione('4', 'Attrezzature di Cantiere')
        
        pdf.set_fill_color(*GRIGIO_CHIARO)
        pdf.set_font('Helvetica', 'B', 8)
        pdf.set_x(10)
        pdf.cell(60, 5, ' Attrezzatura', border=1, fill=True)
        pdf.cell(50, 5, ' Marca/Modello', border=1, fill=True)
        pdf.cell(40, 5, ' Matricola', border=1, fill=True)
        pdf.cell(40, 5, ' Ultima Verifica', border=1, ln=1, fill=True)
        
        pdf.set_font('Helvetica', '', 8)
        for attr in attrezzature:
            check_spazio(8)
            pdf.set_x(10)
            pdf.cell(60, 5, ' ' + pulisci_testo(attr.get('nome', ''), 30), border=1)
            pdf.cell(50, 5, ' ' + pulisci_testo(attr.get('marca', ''), 25), border=1)
            pdf.cell(40, 5, ' ' + pulisci_testo(attr.get('matricola', 'N.D.'), 20), border=1)
            pdf.cell(40, 5, ' ' + pulisci_testo(attr.get('verifica', 'Conforme'), 20), border=1, ln=1)
        
        pdf.ln(2)
        pdf.set_font('Helvetica', 'I', 7)
        pdf.set_x(10)
        pdf.cell(W, 4, 'I libretti d\'uso e manutenzione sono disponibili in cantiere.', ln=1)
        pdf.ln(2)
    
    # ==================== SOSTANZE ====================
    if sostanze:
        titolo_sezione('5', 'Sostanze Pericolose Utilizzate')
        
        pdf.set_fill_color(*GIALLO_CHIARO)
        pdf.set_font('Helvetica', 'B', 8)
        pdf.set_x(10)
        pdf.cell(70, 5, ' Prodotto', border=1, fill=True)
        pdf.cell(50, 5, ' Produttore', border=1, fill=True)
        pdf.cell(70, 5, ' Frasi H (Pericolo)', border=1, ln=1, fill=True)
        
        pdf.set_font('Helvetica', '', 8)
        for sost in sostanze:
            check_spazio(8)
            pdf.set_x(10)
            pdf.cell(70, 5, ' ' + pulisci_testo(sost.get('nome', ''), 28), border=1)
            pdf.cell(50, 5, ' ' + pulisci_testo(sost.get('produttore', ''), 20), border=1)
            pdf.cell(70, 5, ' ' + pulisci_testo(sost.get('frasi_h', 'Vedere SDS'), 28), border=1, ln=1)
        
        pdf.ln(2)
        pdf.set_font('Helvetica', 'I', 7)
        pdf.set_x(10)
        pdf.cell(W, 4, 'Le Schede Dati di Sicurezza (SDS) sono disponibili in cantiere e sono state consegnate ai lavoratori.', ln=1)
        pdf.ln(2)
    
    # ==================== ORGANIZZAZIONE ====================
    num_sez = 6 if sostanze else (5 if attrezzature else (4 if lavoratori else 3))
    titolo_sezione(str(num_sez), 'Organizzazione del Cantiere')
    
    sottotitolo('Premessa Normativa')
    paragrafo(TESTI_LEGALI['premessa'])
    
    sottotitolo("Obblighi dell'Impresa")
    paragrafo(TESTI_LEGALI['obblighi_impresa'])
    
    sottotitolo('Documentazione in Cantiere')
    docs = ["POS vidimato", "PSC (se previsto)", "DUVRI (se previsto)", "Registro infortuni", 
            "Libretti attrezzature", "SDS prodotti", "Attestati formazione", "Idoneita sanitarie"]
    for doc in docs:
        riga('- ' + doc)
    
    # ==================== CRONOPROGRAMMA ====================
    if lavorazioni:
        num_sez += 1
        titolo_sezione(str(num_sez), 'Cronoprogramma Lavori')
        
        pdf.set_font('Helvetica', 'I', 7)
        pdf.set_x(10)
        pdf.cell(W, 4, 'Sequenza indicativa delle fasi lavorative (da adattare in base all\'avanzamento effettivo):', ln=1)
        pdf.ln(2)
        
        # Header tabella
        pdf.set_fill_color(*GRIGIO_CHIARO)
        pdf.set_font('Helvetica', 'B', 8)
        pdf.set_x(10)
        pdf.cell(10, 5, ' #', border=1, fill=True)
        pdf.cell(80, 5, ' Fase Lavorativa', border=1, fill=True)
        pdf.cell(50, 5, ' Periodo Indicativo', border=1, fill=True)
        pdf.cell(50, 5, ' Note', border=1, ln=1, fill=True)
        
        pdf.set_font('Helvetica', '', 8)
        durata_totale = cantiere.get('durata', '30 giorni')
        # Estrai numero giorni dalla durata
        match = re.search(r'(\d+)', durata_totale)
        giorni_totali = int(match.group(1)) if match else 30
        
        giorni_per_fase = max(3, giorni_totali // len(lavorazioni)) if lavorazioni else 5
        giorno_corrente = 1
        
        for idx, lav_key in enumerate(lavorazioni):
            if lav_key not in DIZIONARIO_LAVORAZIONI:
                continue
            dati = DIZIONARIO_LAVORAZIONI[lav_key]
            nome_fase = pulisci_testo(dati.get('nome', ''), 38)
            
            giorno_fine = min(giorno_corrente + giorni_per_fase - 1, giorni_totali)
            periodo = f"Giorno {giorno_corrente} - {giorno_fine}"
            
            check_spazio(8)
            pdf.set_x(10)
            pdf.cell(10, 5, f' {idx+1}', border=1)
            pdf.cell(80, 5, ' ' + nome_fase, border=1)
            pdf.cell(50, 5, ' ' + periodo, border=1)
            pdf.cell(50, 5, ' ', border=1, ln=1)
            
            giorno_corrente = giorno_fine + 1
        
        pdf.ln(2)
        pdf.set_font('Helvetica', 'I', 7)
        pdf.set_x(10)
        pdf.cell(W, 4, 'Nota: Le fasi possono sovrapporsi. Il cronoprogramma effettivo sara concordato con il CSE (ove previsto).', ln=1)
    
    # ==================== VALUTAZIONE RISCHI ====================
    num_sez += 1
    titolo_sezione(str(num_sez), 'Valutazione dei Rischi')
    
    for lav_key in lavorazioni:
        if lav_key not in DIZIONARIO_LAVORAZIONI:
            continue
        dati = DIZIONARIO_LAVORAZIONI[lav_key]
        
        check_spazio(70)
        pdf.ln(2)
        
        pdf.set_fill_color(*GRIGIO_CHIARO)
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_x(10)
        pdf.cell(W, 5, ' ' + pulisci_testo(dati.get('nome', ''), 55), ln=1, fill=True)
        
        pdf.set_font('Helvetica', 'I', 7)
        pdf.set_text_color(100, 100, 100)
        pdf.set_x(10)
        pdf.multi_cell(W, 3, pulisci_testo(dati.get('descrizione_tecnica', ''), 200))
        pdf.set_text_color(0, 0, 0)
        
        if dati.get('valori_esposizione'):
            pdf.set_fill_color(255, 250, 230)
            pdf.set_font('Helvetica', 'B', 7)
            pdf.set_x(10)
            pdf.cell(W, 4, ' VALORI ESPOSIZIONE', ln=1, fill=True)
            pdf.set_font('Helvetica', '', 7)
            for t, v in dati['valori_esposizione'].items():
                pdf.set_x(12)
                pdf.cell(W-4, 3, f'{t.upper()}: {v}', ln=1)
        
        # Rischi
        check_spazio(30)
        pdf.set_fill_color(*ARANCIONE)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Helvetica', 'B', 7)
        pdf.set_x(10)
        pdf.cell(W, 4, ' RISCHI', ln=1, fill=True)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Helvetica', '', 7)
        
        for r in dati.get('rischi', []):
            check_spazio(5)
            grav = r.get('gravita', 'M')[0]
            colore = ROSSO_CHIARO if grav == 'A' else (GIALLO_CHIARO if grav == 'M' else VERDE_CHIARO)
            pdf.set_fill_color(*colore)
            txt = f" [{grav}] {pulisci_testo(r.get('nome', ''), 25)}: {pulisci_testo(r.get('descrizione', ''), 60)}"
            norm = r.get('normativa', '')
            if norm:
                txt += f" ({pulisci_testo(norm, 25)})"
            pdf.set_x(10)
            pdf.cell(W, 4, txt[:120], ln=1, fill=True)
        
        # DPI
        check_spazio(25)
        pdf.set_fill_color(*BLU_CHIARO)
        pdf.set_font('Helvetica', 'B', 7)
        pdf.set_x(10)
        pdf.cell(W, 4, ' DPI OBBLIGATORI', ln=1, fill=True)
        pdf.set_font('Helvetica', '', 7)
        for dpi in dati.get('dpi_obbligatori', []):
            check_spazio(4)
            if isinstance(dpi, dict):
                txt = f"  - {pulisci_testo(dpi.get('nome', ''), 30)} [{pulisci_testo(dpi.get('norma', ''), 22)}]"
            else:
                txt = f"  - {pulisci_testo(str(dpi), 60)}"
            pdf.set_x(10)
            pdf.cell(W, 3, txt[:100], ln=1)
        
        # Misure
        check_spazio(25)
        pdf.set_fill_color(*VERDE_CHIARO)
        pdf.set_font('Helvetica', 'B', 7)
        pdf.set_x(10)
        pdf.cell(W, 4, ' MISURE PREVENZIONE', ln=1, fill=True)
        pdf.set_font('Helvetica', '', 7)
        for m in dati.get('misure_prevenzione', []):
            check_spazio(4)
            pdf.set_x(10)
            pdf.cell(W, 3, f"  - {pulisci_testo(str(m), 90)}", ln=1)
        
        pdf.ln(2)
    
    # Rischi AI - CON FILTRO ANTI-DUPLICATI
    if rischi_ai and rischi_ai.get('rischi_aggiuntivi'):
        # Raccogli tutti i nomi dei rischi già presenti nelle lavorazioni selezionate
        rischi_esistenti = set()
        keywords_esistenti = set()
        for lav_key in lavorazioni:
            if lav_key in DIZIONARIO_LAVORAZIONI:
                for r in DIZIONARIO_LAVORAZIONI[lav_key].get('rischi', []):
                    nome_lower = (r.get('nome', '') or '').lower()
                    rischi_esistenti.add(nome_lower)
                    # Estrai parole chiave
                    for kw in ['caduta', 'rumore', 'polveri', 'vibrazioni', 'chimico', 'elettrico', 
                               'schegge', 'ustioni', 'tagli', 'crollo', 'inalazione', 'dermatiti',
                               'posture', 'scivolamento', 'urti', 'abrasioni']:
                        if kw in nome_lower:
                            keywords_esistenti.add(kw)
        
        # Filtra rischi AI rimuovendo duplicati
        rischi_filtrati = []
        for r in rischi_ai['rischi_aggiuntivi']:
            nome_ai = (r.get('nome', '') or '').lower()
            desc_ai = (r.get('descrizione', '') or '').lower()
            
            # Verifica se è un duplicato
            is_duplicato = False
            for kw in keywords_esistenti:
                if kw in nome_ai or kw in desc_ai[:50]:  # Controlla nome e inizio descrizione
                    is_duplicato = True
                    break
            
            if not is_duplicato:
                rischi_filtrati.append(r)
        
        # Mostra solo se ci sono rischi non duplicati
        if rischi_filtrati:
            check_spazio(40)
            pdf.ln(2)
            pdf.set_fill_color(100, 150, 220)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font('Helvetica', 'B', 8)
            pdf.set_x(10)
            pdf.cell(W, 5, ' RISCHI AGGIUNTIVI SPECIFICI DEL CANTIERE', ln=1, fill=True)
            pdf.set_text_color(0, 0, 0)
            
            pdf.set_font('Helvetica', 'I', 7)
            pdf.set_x(10)
            pdf.cell(W, 4, 'Rischi specifici identificati dall\'analisi della descrizione lavori:', ln=1)
            
            pdf.set_font('Helvetica', '', 7)
            for r in rischi_filtrati:
                check_spazio(6)
                grav = (r.get('gravita', 'M') or 'M')[0]
                colore = ROSSO_CHIARO if grav == 'A' else (GIALLO_CHIARO if grav == 'M' else VERDE_CHIARO)
                pdf.set_fill_color(*colore)
                pdf.set_x(10)
                pdf.multi_cell(W, 4, f" [{grav}] {pulisci_testo(r.get('nome', ''), 35)}: {pulisci_testo(r.get('descrizione', ''), 120)}", fill=True)
        
        # Note RSPP sempre visibili se presenti
        if rischi_ai.get('note_rspp'):
            pdf.ln(1)
            pdf.set_font('Helvetica', 'I', 7)
            pdf.set_x(10)
            pdf.multi_cell(W, 3, 'Note RSPP: ' + pulisci_testo(rischi_ai.get('note_rspp', ''), 200))
    
    # ==================== COORDINAMENTO ====================
    num_sez += 1
    titolo_sezione(str(num_sez), 'Coordinamento')
    paragrafo(TESTI_LEGALI['coordinamento'])
    
    # ==================== EMERGENZE ====================
    num_sez += 1
    titolo_sezione(str(num_sez), 'Gestione Emergenze')
    paragrafo(TESTI_LEGALI['emergenza'])
    
    pdf.ln(2)
    check_spazio(45)
    pdf.set_fill_color(255, 235, 235)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_x(10)
    pdf.cell(W, 5, ' NUMERI EMERGENZA', ln=1, fill=True)
    pdf.set_font('Helvetica', 'B', 10)
    for num, desc in [('112', 'EMERGENZE'), ('115', 'VV.FF.'), ('118', 'SOCCORSO')]:
        pdf.set_x(10)
        pdf.cell(W, 5, f'   {num} - {desc}', ln=1)
    
    # Ospedale più vicino - con multi_cell per testi lunghi
    ospedale = cantiere.get('ospedale_vicino', '')
    if ospedale:
        pdf.set_font('Helvetica', 'B', 8)
        pdf.set_x(10)
        pdf.multi_cell(W, 4, f'PRONTO SOCCORSO: {pulisci_testo(ospedale, 150)}')
    
    pdf.set_font('Helvetica', 'B', 8)
    pdf.set_x(10)
    pdf.cell(W, 5, 'PUNTO RACCOLTA: Ingresso cantiere', ln=1)
    
    # ==================== CHECKLIST ALLEGATI ====================
    num_sez += 1
    titolo_sezione(str(num_sez), 'Checklist Allegati')
    
    # Verifica SEPARATA per ponteggi fissi vs trabattelli (Art. 136 D.Lgs 81/08)
    ha_ponteggio_fisso = any('ponteggio' in (a.get('nome', '') or '').lower() and 'trabattello' not in (a.get('nome', '') or '').lower() for a in attrezzature)
    ha_trabattello = any('trabattello' in (a.get('nome', '') or '').lower() for a in attrezzature)
    
    # Pi.M.U.S. solo per ponteggi fissi (Art. 136), per trabattelli basta il manuale
    if ha_ponteggio_fisso:
        pimus_doc = "Pi.M.U.S. (ponteggi fissi Art. 136)"
        pimus_stato = "Da allegare"
    elif ha_trabattello:
        pimus_doc = "Manuale d'uso trabattello"
        pimus_stato = "Da allegare"
    else:
        pimus_doc = "Pi.M.U.S. / Manuale trabattello"
        pimus_stato = "N.A."
    
    pdf.set_font('Helvetica', '', 8)
    allegati = [
        ("Visura camerale", "Da allegare"),
        ("DURC in corso di validita", "Da allegare"),
        ("Attestati formazione lavoratori", "Da allegare"),
        ("Idoneita sanitarie", "Da allegare"),
        ("Libretti attrezzature", "Da allegare"),
        ("Schede SDS sostanze", "Da allegare" if sostanze else "N.A."),
        (pimus_doc, pimus_stato),
        ("Verbale consegna DPI", "Da allegare")
    ]
    
    pdf.set_fill_color(*GRIGIO_CHIARO)
    pdf.set_font('Helvetica', 'B', 8)
    pdf.set_x(10)
    pdf.cell(120, 5, ' Documento', border=1, fill=True)
    pdf.cell(70, 5, ' Stato', border=1, ln=1, fill=True)
    
    pdf.set_font('Helvetica', '', 8)
    for doc, stato in allegati:
        pdf.set_x(10)
        pdf.cell(120, 5, ' [ ] ' + doc, border=1)
        pdf.cell(70, 5, ' ' + stato, border=1, ln=1)
    
    # ==================== FIRME ====================
    num_sez += 1
    titolo_sezione(str(num_sez), 'Dichiarazione e Firme')
    
    pdf.set_font('Helvetica', '', 8)
    pdf.set_x(10)
    pdf.multi_cell(W, 4, "Il sottoscritto DICHIARA che il presente POS e conforme all'Allegato XV D.Lgs 81/08, che i lavoratori sono informati/formati sui rischi specifici, e che i DPI saranno forniti e ne sara verificato l'utilizzo.")
    
    pdf.ln(6)
    check_spazio(50)
    
    # Due colonne firme
    pdf.set_fill_color(*GRIGIO_CHIARO)
    pdf.set_font('Helvetica', 'B', 8)
    pdf.set_x(10)
    pdf.cell(90, 5, ' IL DATORE DI LAVORO', fill=True)
    pdf.cell(10, 5, '')
    
    # Intestazione firma RLS in base al tipo
    rls_tipo = ditta.get('rls_tipo', 'non_eletto')
    if rls_tipo == 'interno_eletto':
        pdf.cell(90, 5, ' PER PRESA VISIONE RLS', ln=1, fill=True)
        firma_rls_nome = ditta.get('rls_nome', '')
    elif rls_tipo == 'territoriale':
        pdf.cell(90, 5, ' PER PRESA VISIONE RLST', ln=1, fill=True)
        firma_rls_nome = ditta.get('rls_territoriale', '')
    else:  # non_eletto
        pdf.cell(90, 5, ' PER PRESA VISIONE (RLS)', ln=1, fill=True)
        firma_rls_nome = 'Non eletto - Funzioni RLST'
    
    pdf.ln(12)
    pdf.set_x(10)
    pdf.cell(90, 5, ' _____________________________')
    pdf.cell(10, 5, '')
    pdf.cell(90, 5, ' _____________________________', ln=1)
    
    pdf.set_font('Helvetica', 'I', 7)
    pdf.set_x(10)
    pdf.cell(90, 4, f" ({pulisci_testo(ditta.get('datore_lavoro', ''), 30)})")
    pdf.cell(10, 4, '')
    pdf.cell(90, 4, f" ({pulisci_testo(firma_rls_nome, 35)})", ln=1)
    
    pdf.ln(8)
    pdf.set_font('Helvetica', '', 9)
    pdf.set_x(10)
    pdf.cell(W, 5, f"Data: {date.today().strftime('%d/%m/%Y')}                    Luogo: {pulisci_testo(cantiere.get('indirizzo', ''), 50)}", ln=1)
    
    # Data revisione
    pdf.ln(5)
    pdf.set_font('Helvetica', 'B', 8)
    pdf.set_x(10)
    data_rev = (date.today() + timedelta(days=365)).strftime('%d/%m/%Y')
    pdf.cell(W, 5, f"PROSSIMA REVISIONE POS: {data_rev} (o in caso di modifiche significative)", ln=1)
    
    # ==================== VERBALE PRESA VISIONE LAVORATORI ====================
    if lavoratori:
        nuova_pagina()
        num_sez += 1
        titolo_sezione(str(num_sez), 'Verbale di Presa Visione e Consegna DPI')
        
        pdf.set_font('Helvetica', '', 8)
        pdf.set_x(10)
        pdf.multi_cell(W, 4, "I sottoscritti lavoratori dichiarano di aver preso visione del presente Piano Operativo di Sicurezza, di essere stati informati sui rischi specifici delle lavorazioni e sulle misure di prevenzione e protezione adottate, e di aver ricevuto i Dispositivi di Protezione Individuale (DPI) necessari per lo svolgimento delle attivita lavorative.")
        
        pdf.ln(3)
        pdf.set_font('Helvetica', 'I', 7)
        pdf.set_x(10)
        pdf.cell(W, 4, 'Riferimento normativo: Art. 36, 37, 77 e 78 D.Lgs 81/08', ln=1)
        
        pdf.ln(4)
        
        # Tabella firme lavoratori
        pdf.set_fill_color(*GRIGIO_CHIARO)
        pdf.set_font('Helvetica', 'B', 7)
        pdf.set_x(10)
        pdf.cell(45, 6, ' Nome e Cognome', border=1, fill=True)
        pdf.cell(30, 6, ' Mansione', border=1, fill=True)
        pdf.cell(40, 6, ' Firma Presa Visione', border=1, fill=True)
        pdf.cell(40, 6, ' Firma Ricevuta DPI', border=1, fill=True)
        pdf.cell(35, 6, ' Data', border=1, ln=1, fill=True)
        
        pdf.set_font('Helvetica', '', 8)
        for lav in lavoratori:
            check_spazio(12)
            pdf.set_x(10)
            pdf.cell(45, 10, ' ' + pulisci_testo(lav.get('nome', ''), 22), border=1)
            pdf.cell(30, 10, ' ' + pulisci_testo(lav.get('mansione', ''), 14), border=1)
            pdf.cell(40, 10, ' ', border=1)  # Spazio per firma presa visione
            pdf.cell(40, 10, ' ', border=1)  # Spazio per firma DPI
            pdf.cell(35, 10, ' ___/___/______', border=1, ln=1)
        
        # Righe vuote per eventuali lavoratori aggiuntivi
        righe_extra = max(0, 5 - len(lavoratori))
        for _ in range(righe_extra):
            check_spazio(12)
            pdf.set_x(10)
            pdf.cell(45, 10, ' ', border=1)
            pdf.cell(30, 10, ' ', border=1)
            pdf.cell(40, 10, ' ', border=1)
            pdf.cell(40, 10, ' ', border=1)
            pdf.cell(35, 10, ' ___/___/______', border=1, ln=1)
        
        pdf.ln(5)
        pdf.set_font('Helvetica', 'I', 7)
        pdf.set_x(10)
        pdf.multi_cell(W, 3, "NOTA: La firma del presente verbale attesta l'avvenuta informazione e formazione sui contenuti del POS e la consegna dei DPI. Il lavoratore si impegna ad utilizzare correttamente i DPI forniti e a segnalare eventuali anomalie al preposto o al Datore di Lavoro.")
        
        pdf.ln(5)
        pdf.set_font('Helvetica', '', 8)
        pdf.set_x(10)
        pdf.cell(W, 5, f"Luogo: {pulisci_testo(cantiere.get('indirizzo', ''), 60)}", ln=1)
        
        # Spazio per firma del Datore che attesta la consegna
        pdf.ln(8)
        pdf.set_fill_color(*GRIGIO_CHIARO)
        pdf.set_font('Helvetica', 'B', 8)
        pdf.set_x(10)
        pdf.cell(95, 5, ' IL DATORE DI LAVORO (per consegna DPI)', ln=1, fill=True)
        pdf.ln(10)
        pdf.set_x(10)
        pdf.cell(95, 5, ' _________________________________', ln=1)
        pdf.set_font('Helvetica', 'I', 7)
        pdf.set_x(10)
        pdf.cell(95, 4, f" ({pulisci_testo(ditta.get('datore_lavoro', ''), 35)})", ln=1)
    
    return bytes(pdf.output())


# ==============================================================================
# SESSION STATE
# ==============================================================================
def init_session():
    defaults = {
        'step': 1,
        'ditta': {
            'ragione_sociale': '', 
            'piva_cf': '', 
            'indirizzo': '', 
            'telefono': '', 
            'datore_lavoro': '', 
            'rspp_autonomo': True, 
            'rspp': '', 
            'medico': '',
            'rls_tipo': 'non_eletto',  # 'interno_eletto', 'non_eletto', 'territoriale'
            'rls_nome': '',
            'rls_territoriale': '',
            'durc_valido': True,
            'durc_scadenza': '',
            'codice_ateco': '',
            'num_dipendenti': ''
        },
        'cantiere': {
            'indirizzo': '', 
            'committente': '', 
            'data_inizio': '', 
            'durata': '', 
            'descrizione': '',
            'prodotti_chimici': '',
            'attrezzature_specifiche': '',
            'orario_lavoro': '08:00 - 12:00 / 13:00 - 17:00',
            'giorni_lavoro': 'Lunedi - Venerdi',
            'ospedale_vicino': '',
            'fasi_lavoro': []  # Lista di dict: {fase, durata_giorni}
        },
        'addetti': {'primo_soccorso': '', 'antincendio': ''},
        'lavoratori': [],
        'attrezzature': [],
        'sostanze': [],
        'lavorazioni_selezionate': {},
        'rischi_ai': None,
        'disclaimer_ok': False,
        'ai_analisi_fatta': False
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
    # Aggiorna struttura esistente con nuovi campi
    # Migrazione da vecchio formato rls_interno (bool) a rls_tipo (string)
    if 'rls_tipo' not in st.session_state.ditta:
        # Migra dal vecchio formato
        if st.session_state.ditta.get('rls_interno', True):
            if st.session_state.ditta.get('rls_nome', ''):
                st.session_state.ditta['rls_tipo'] = 'interno_eletto'
            else:
                st.session_state.ditta['rls_tipo'] = 'non_eletto'
        else:
            st.session_state.ditta['rls_tipo'] = 'territoriale'
        st.session_state.ditta['rls_nome'] = st.session_state.ditta.get('rls_nome', '')
        st.session_state.ditta['rls_territoriale'] = st.session_state.ditta.get('rls_territoriale', '')
    if 'durc_valido' not in st.session_state.ditta:
        st.session_state.ditta['durc_valido'] = True
        st.session_state.ditta['durc_scadenza'] = ''
    if 'codice_ateco' not in st.session_state.ditta:
        st.session_state.ditta['codice_ateco'] = ''
        st.session_state.ditta['num_dipendenti'] = ''
    if 'orario_lavoro' not in st.session_state.cantiere:
        st.session_state.cantiere['orario_lavoro'] = '08:00 - 12:00 / 13:00 - 17:00'
        st.session_state.cantiere['giorni_lavoro'] = 'Lunedi - Venerdi'
    if 'ospedale_vicino' not in st.session_state.cantiere:
        st.session_state.cantiere['ospedale_vicino'] = ''
        st.session_state.cantiere['fasi_lavoro'] = []
    if 'prodotti_chimici' not in st.session_state.cantiere:
        st.session_state.cantiere['prodotti_chimici'] = ''
        st.session_state.cantiere['attrezzature_specifiche'] = ''
    if 'lavoratori' not in st.session_state:
        st.session_state.lavoratori = []
    if 'attrezzature' not in st.session_state:
        st.session_state.attrezzature = []
    if 'sostanze' not in st.session_state:
        st.session_state.sostanze = []
    if not st.session_state.lavorazioni_selezionate:
        st.session_state.lavorazioni_selezionate = {k: False for k in DIZIONARIO_LAVORAZIONI.keys()}


# ==============================================================================
# UI
# ==============================================================================
def render_header():
    st.markdown('<div class="main-header"><h1>🏗️ CantiereSicuro AI PRO</h1><p>Generatore POS - D.Lgs 81/08</p></div>', unsafe_allow_html=True)


def render_sidebar():
    with st.sidebar:
        st.markdown("## 🏗️ CantiereSicuro")
        st.markdown("---")
        st.progress(min(st.session_state.step / 5, 1.0))
        st.caption(f"Fase {st.session_state.step} di 5")
        st.markdown("---")
        for num, label in [("1", "Dati Impresa"), ("2", "Organigramma"), ("3", "Dati Cantiere"), ("4", "Analisi Rischi"), ("5", "Genera POS")]:
            step_num = int(num)
            icon = "✅" if step_num < st.session_state.step else ("▶️" if step_num == st.session_state.step else "⬜")
            if st.button(f"{icon} {num}. {label}", key=f"nav_{num}", use_container_width=True):
                if step_num <= st.session_state.step + 1:
                    st.session_state.step = step_num
                    st.rerun()
        st.markdown("---")
        st.markdown("### 🤖 Assistente")
        domanda = st.text_input("Chiedi:", placeholder="Es: Quando serve il POS?", key="ai_q")
        if st.button("Chiedi", key="ask") and domanda:
            with st.spinner("..."):
                st.info(ai_assistente(domanda))


def render_step1():
    st.markdown("### Fase 1: Dati Impresa")
    st.markdown('<div class="card-normativa"><strong>📋 Riferimento:</strong> Art. 89-90, Allegato XV del D.Lgs 81/08</div>', unsafe_allow_html=True)
    
    # Checkbox RSPP
    rspp_auto = st.checkbox("✅ Datore di Lavoro = RSPP (Art. 34 D.Lgs 81/08)", value=st.session_state.ditta['rspp_autonomo'], key="rspp_check", help="Per aziende fino a 30 dipendenti in settori a basso rischio")
    
    # Radio RLS - FUORI dal form per aggiornamento immediato
    st.markdown("---")
    st.markdown("##### 🛡️ Rappresentante Lavoratori Sicurezza (RLS)")
    
    rls_options = {
        'interno_eletto': '👤 RLS Interno eletto',
        'non_eletto': '📋 RLS non eletto (azienda < 15 dipendenti)',
        'territoriale': '🏛️ RLST - Rappresentante Territoriale'
    }
    
    # Determina l'indice corrente
    current_rls = st.session_state.ditta.get('rls_tipo', 'non_eletto')
    rls_keys = list(rls_options.keys())
    current_index = rls_keys.index(current_rls) if current_rls in rls_keys else 1
    
    rls_tipo = st.radio(
        "Seleziona la situazione RLS della tua azienda:",
        options=rls_keys,
        format_func=lambda x: rls_options[x],
        index=current_index,
        key="rls_tipo_radio",
        horizontal=False
    )
    st.session_state.ditta['rls_tipo'] = rls_tipo
    
    with st.form("f1"):
        st.markdown("##### 🏢 Dati Anagrafici Impresa")
        c1, c2 = st.columns(2)
        with c1:
            ragione = st.text_input("Ragione Sociale *", value=st.session_state.ditta['ragione_sociale'])
            piva = st.text_input("P.IVA / CF *", value=st.session_state.ditta['piva_cf'])
            indirizzo = st.text_input("Sede Legale *", value=st.session_state.ditta['indirizzo'], placeholder="Via, CAP, Città (Prov)")
        with c2:
            telefono = st.text_input("Telefono", value=st.session_state.ditta['telefono'])
            codice_ateco = st.text_input("Codice ATECO", value=st.session_state.ditta.get('codice_ateco', ''), placeholder="Es: 41.20.00", help="Codice attività economica")
            num_dipendenti = st.text_input("N. Dipendenti medi annui", value=st.session_state.ditta.get('num_dipendenti', ''), placeholder="Es: 5")
        
        st.markdown("##### 👥 Figure della Sicurezza")
        c1, c2 = st.columns(2)
        with c1:
            datore = st.text_input("Datore di Lavoro *", value=st.session_state.ditta['datore_lavoro'])
        with c2:
            medico = st.text_input("Medico Competente", value=st.session_state.ditta['medico'], help="Obbligatorio se prevista sorveglianza sanitaria")
        
        # RSPP esterno
        rspp_esterno = ""
        if not rspp_auto:
            rspp_esterno = st.text_input("RSPP Esterno *", value=st.session_state.ditta.get('rspp', ''))
        
        # Campi RLS condizionali in base alla selezione
        st.markdown("---")
        rls_nome = ""
        rls_territoriale = ""
        
        if rls_tipo == 'interno_eletto':
            st.info("👤 **RLS Interno eletto** - Inserisci il nome del Rappresentante dei Lavoratori per la Sicurezza")
            rls_nome = st.text_input("Nome e Cognome RLS *", value=st.session_state.ditta.get('rls_nome', ''), placeholder="Es: Mario Rossi")
        elif rls_tipo == 'non_eletto':
            st.info("📋 **RLS non eletto** - Per aziende con meno di 15 dipendenti che non hanno eletto un RLS interno. Le funzioni sono svolte dal Rappresentante Territoriale (RLST) dell'organismo paritetico di riferimento.")
        elif rls_tipo == 'territoriale':
            st.info("🏛️ **RLST** - L'azienda si avvale del Rappresentante dei Lavoratori per la Sicurezza Territoriale")
            rls_territoriale = st.text_input("Ente RLST di riferimento *", value=st.session_state.ditta.get('rls_territoriale', ''), placeholder="Es: RLST Edilizia - FENEAL UIL Lombardia")
        
        if st.form_submit_button("Avanti →", use_container_width=True):
            if ragione and piva and datore and indirizzo:
                if not rspp_auto and not rspp_esterno:
                    st.error("⚠️ Inserisci il nome del RSPP esterno")
                elif rls_tipo == 'interno_eletto' and not rls_nome:
                    st.error("⚠️ Inserisci il nome del RLS interno eletto")
                elif rls_tipo == 'territoriale' and not rls_territoriale:
                    st.error("⚠️ Inserisci l'ente RLST di riferimento")
                else:
                    st.session_state.ditta = {
                        'ragione_sociale': ragione, 
                        'piva_cf': piva, 
                        'indirizzo': indirizzo, 
                        'telefono': telefono, 
                        'datore_lavoro': datore, 
                        'rspp_autonomo': rspp_auto, 
                        'rspp': rspp_esterno, 
                        'medico': medico,
                        'rls_tipo': rls_tipo,
                        'rls_nome': rls_nome,
                        'rls_territoriale': rls_territoriale,
                        'codice_ateco': codice_ateco,
                        'num_dipendenti': num_dipendenti
                    }
                    st.session_state.step = 2
                    st.rerun()
            else:
                st.error("⚠️ Compila i campi obbligatori (Ragione Sociale, P.IVA, Sede, Datore)")


def render_step2():
    st.markdown("### Fase 2: Organizzazione e Lavoratori")
    st.markdown('<div class="card-normativa"><strong>📋 Rif:</strong> Art. 18, 43 D.Lgs 81/08</div>', unsafe_allow_html=True)
    
    # Inizializza num_lavoratori in session_state se non esiste
    if 'num_lavoratori' not in st.session_state:
        st.session_state.num_lavoratori = max(1, len(st.session_state.lavoratori)) if st.session_state.lavoratori else 1
    
    st.markdown("##### 🚨 Addetti Emergenze")
    st.info("💡 Se lavori da solo, inserisci il tuo nome in entrambi i campi")
    
    # Sezione Lavoratori FUORI dal form per permettere update dinamico
    st.markdown("---")
    st.markdown("##### 👷 Lavoratori in Cantiere")
    st.caption("Inserisci nome, mansione e formazione di ogni lavoratore")
    
    # Numero lavoratori FUORI dal form - triggera rerun immediato
    num_lav = st.number_input(
        "Numero lavoratori", 
        min_value=1, 
        max_value=15, 
        value=st.session_state.num_lavoratori,
        key="num_lav_input"
    )
    st.session_state.num_lavoratori = int(num_lav)
    
    # Intestazione colonne
    header_cols = st.columns([3, 2, 2, 2])
    with header_cols[0]:
        st.markdown("**Nome e Cognome**")
    with header_cols[1]:
        st.markdown("**Mansione**")
    with header_cols[2]:
        st.markdown("**Formazione**")
    with header_cols[3]:
        st.markdown("**Scad. Idoneità**")
    
    mansioni_list = ["Muratore", "Elettricista", "Idraulico", "Imbianchino", "Manovale", "Capocantiere", "Piastrellista", "Carpentiere", "Altro"]
    form_list = ["Art. 37 - 16h", "Art. 37 - 8h", "Art. 37 - 32h", "Preposto", "Dirigente"]
    
    with st.form("f2"):
        # Addetti emergenze
        c1, c2 = st.columns(2)
        with c1:
            ps = st.text_input("👨‍⚕️ Addetto Primo Soccorso *", value=st.session_state.addetti['primo_soccorso'] or st.session_state.ditta['datore_lavoro'])
        with c2:
            ai_add = st.text_input("🧯 Addetto Antincendio *", value=st.session_state.addetti['antincendio'] or st.session_state.ditta['datore_lavoro'])
        
        st.markdown("---")
        
        # Righe lavoratori
        lavoratori_temp = []
        for i in range(st.session_state.num_lavoratori):
            # Valori default
            def_nome = st.session_state.lavoratori[i]['nome'] if i < len(st.session_state.lavoratori) else (st.session_state.ditta['datore_lavoro'] if i == 0 else '')
            def_mans = st.session_state.lavoratori[i].get('mansione', 'Muratore') if i < len(st.session_state.lavoratori) else 'Muratore'
            def_form = st.session_state.lavoratori[i].get('formazione', 'Art. 37 - 16h') if i < len(st.session_state.lavoratori) else 'Art. 37 - 16h'
            def_idon = st.session_state.lavoratori[i].get('idoneita', '') if i < len(st.session_state.lavoratori) else ''
            
            cols = st.columns([3, 2, 2, 2])
            with cols[0]:
                nome = st.text_input(f"Nome lav. {i+1}", value=def_nome, key=f"ln_{i}", placeholder="Nome Cognome", label_visibility="collapsed")
            with cols[1]:
                idx_m = mansioni_list.index(def_mans) if def_mans in mansioni_list else 0
                mansione = st.selectbox(f"Mansione {i+1}", mansioni_list, index=idx_m, key=f"lm_{i}", label_visibility="collapsed")
            with cols[2]:
                idx_f = form_list.index(def_form) if def_form in form_list else 0
                formazione = st.selectbox(f"Formazione {i+1}", form_list, index=idx_f, key=f"lf_{i}", label_visibility="collapsed")
            with cols[3]:
                idoneita = st.text_input(f"Idoneità {i+1}", value=def_idon, key=f"li_{i}", placeholder="GG/MM/AAAA", label_visibility="collapsed")
            
            if nome:
                lavoratori_temp.append({'nome': nome, 'mansione': mansione, 'formazione': formazione, 'idoneita': idoneita})
        
        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            if st.form_submit_button("← Indietro", use_container_width=True):
                st.session_state.step = 1
                st.rerun()
        with c2:
            if st.form_submit_button("Avanti →", use_container_width=True):
                st.session_state.addetti = {'primo_soccorso': ps, 'antincendio': ai_add}
                st.session_state.lavoratori = lavoratori_temp if lavoratori_temp else [{'nome': ps, 'mansione': 'Operaio', 'formazione': 'Art. 37 - 16h', 'idoneita': ''}]
                st.session_state.step = 3
                st.rerun()


def render_step3():
    st.markdown("### Fase 3: Dati Cantiere")
    client = get_openai_client()
    if client:
        st.markdown('<div class="card-ai"><strong>🤖 AI:</strong> Genera descrizione tecnica delle opere</div>', unsafe_allow_html=True)
        c1, c2 = st.columns([3, 1])
        with c1:
            tipo = st.text_input("Tipo lavoro", placeholder="Es: Ristrutturazione bagno completo", key="tipo_ai")
        with c2:
            st.write(""); st.write("")
            if st.button("✨ Genera") and tipo:
                with st.spinner("Generazione descrizione tecnica..."):
                    desc = ai_genera_descrizione(tipo)
                    if desc:
                        st.session_state.cantiere['descrizione'] = desc
                        st.rerun()
    
    # Inizializza contatori in session_state
    if 'num_attrezzature' not in st.session_state:
        st.session_state.num_attrezzature = len(st.session_state.attrezzature) if st.session_state.attrezzature else 2
    if 'num_sostanze' not in st.session_state:
        st.session_state.num_sostanze = len(st.session_state.sostanze) if st.session_state.sostanze else 0
    
    # Selettori numero FUORI dal form
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### 🔧 Attrezzature")
        num_attr = st.number_input("Numero attrezzature", min_value=0, max_value=10, value=st.session_state.num_attrezzature, key="num_attr_input")
        st.session_state.num_attrezzature = int(num_attr)
    with col2:
        st.markdown("##### 🧪 Sostanze Pericolose")
        num_sost = st.number_input("Numero sostanze", min_value=0, max_value=10, value=st.session_state.num_sostanze, key="num_sost_input")
        st.session_state.num_sostanze = int(num_sost)
    
    with st.form("f3"):
        st.markdown("##### 📍 Localizzazione e Tempi")
        indirizzo = st.text_input("Indirizzo completo cantiere *", value=st.session_state.cantiere['indirizzo'], placeholder="Via, numero civico, CAP, Città (Provincia)")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            committente = st.text_input("Committente", value=st.session_state.cantiere['committente'], placeholder="Nome / Ragione Sociale")
        with c2:
            durata = st.text_input("Durata lavori *", value=st.session_state.cantiere['durata'], placeholder="Es: 15 giorni")
        with c3:
            data_inizio = st.text_input("Data inizio", value=st.session_state.cantiere.get('data_inizio', date.today().strftime('%d/%m/%Y')))
        
        st.markdown("##### ⏰ Organizzazione Turni")
        c1, c2 = st.columns(2)
        with c1:
            orario = st.text_input("Orario di lavoro", value=st.session_state.cantiere.get('orario_lavoro', '08:00-12:00 / 13:00-17:00'), placeholder="08:00-12:00 / 13:00-17:00")
        with c2:
            giorni = st.text_input("Giorni lavorativi", value=st.session_state.cantiere.get('giorni_lavoro', 'Lunedi - Venerdi'), placeholder="Lunedi - Venerdi")
        
        st.markdown("##### 🚑 Emergenze")
        ospedale = st.text_input("Ospedale/Pronto Soccorso più vicino", value=st.session_state.cantiere.get('ospedale_vicino', ''), placeholder="Es: Ospedale San Raffaele - Via Olgettina 60, Milano (3 km)")
        
        st.markdown("##### 📝 Descrizione Opere")
        descrizione = st.text_area("Descrizione dettagliata lavori *", value=st.session_state.cantiere['descrizione'], height=120, help="Descrivi le fasi lavorative principali")
        
        # Attrezzature
        attrezzature_temp = []
        if st.session_state.num_attrezzature > 0:
            st.markdown("---")
            st.markdown("**🔧 Attrezzature di Cantiere**")
            # Header
            hcols = st.columns([3, 2, 2, 2])
            with hcols[0]:
                st.caption("Attrezzatura")
            with hcols[1]:
                st.caption("Marca/Modello")
            with hcols[2]:
                st.caption("Matricola")
            with hcols[3]:
                st.caption("Ultima verifica")
            
            attr_default = [
                {'nome': 'Martello demolitore', 'marca': '', 'matricola': '', 'verifica': ''},
                {'nome': 'Smerigliatrice', 'marca': '', 'matricola': '', 'verifica': ''}
            ]
            for i in range(st.session_state.num_attrezzature):
                cols = st.columns([3, 2, 2, 2])
                def_nome = st.session_state.attrezzature[i]['nome'] if i < len(st.session_state.attrezzature) else (attr_default[i]['nome'] if i < len(attr_default) else '')
                def_marca = st.session_state.attrezzature[i].get('marca', '') if i < len(st.session_state.attrezzature) else ''
                def_matr = st.session_state.attrezzature[i].get('matricola', '') if i < len(st.session_state.attrezzature) else ''
                def_ver = st.session_state.attrezzature[i].get('verifica', '') if i < len(st.session_state.attrezzature) else ''
                
                with cols[0]:
                    a_nome = st.text_input(f"att_nome_{i}", value=def_nome, key=f"an_{i}", placeholder="Nome", label_visibility="collapsed")
                with cols[1]:
                    a_marca = st.text_input(f"att_marca_{i}", value=def_marca, key=f"am_{i}", placeholder="Marca", label_visibility="collapsed")
                with cols[2]:
                    a_matr = st.text_input(f"att_matr_{i}", value=def_matr, key=f"at_{i}", placeholder="Matricola", label_visibility="collapsed")
                with cols[3]:
                    a_ver = st.text_input(f"att_ver_{i}", value=def_ver, key=f"av_{i}", placeholder="GG/MM/AA", label_visibility="collapsed")
                
                if a_nome:
                    attrezzature_temp.append({'nome': a_nome, 'marca': a_marca, 'matricola': a_matr, 'verifica': a_ver})
        
        # Sostanze
        sostanze_temp = []
        if st.session_state.num_sostanze > 0:
            st.markdown("---")
            st.markdown("**🧪 Sostanze Pericolose** (SDS obbligatorie in cantiere)")
            # Header
            hcols = st.columns([3, 2, 3])
            with hcols[0]:
                st.caption("Prodotto")
            with hcols[1]:
                st.caption("Produttore")
            with hcols[2]:
                st.caption("Frasi H (pericolo)")
            
            for i in range(st.session_state.num_sostanze):
                cols = st.columns([3, 2, 3])
                def_nome = st.session_state.sostanze[i]['nome'] if i < len(st.session_state.sostanze) else ''
                def_prod = st.session_state.sostanze[i].get('produttore', '') if i < len(st.session_state.sostanze) else ''
                def_h = st.session_state.sostanze[i].get('frasi_h', '') if i < len(st.session_state.sostanze) else ''
                
                with cols[0]:
                    s_nome = st.text_input(f"sost_nome_{i}", value=def_nome, key=f"sn_{i}", placeholder="Nome commerciale", label_visibility="collapsed")
                with cols[1]:
                    s_prod = st.text_input(f"sost_prod_{i}", value=def_prod, key=f"sp_{i}", placeholder="Produttore", label_visibility="collapsed")
                with cols[2]:
                    s_h = st.text_input(f"sost_h_{i}", value=def_h, key=f"sh_{i}", placeholder="Es: H315, H319", label_visibility="collapsed")
                
                if s_nome:
                    sostanze_temp.append({'nome': s_nome, 'produttore': s_prod, 'frasi_h': s_h})
        
        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            if st.form_submit_button("← Indietro", use_container_width=True):
                st.session_state.step = 2
                st.rerun()
        with c2:
            if st.form_submit_button("Avanti →", use_container_width=True):
                if indirizzo and descrizione and durata:
                    st.session_state.cantiere = {
                        'indirizzo': indirizzo, 
                        'committente': committente, 
                        'data_inizio': data_inizio, 
                        'durata': durata, 
                        'descrizione': descrizione,
                        'orario_lavoro': orario,
                        'giorni_lavoro': giorni,
                        'ospedale_vicino': ospedale,
                        'prodotti_chimici': '',
                        'attrezzature_specifiche': ''
                    }
                    st.session_state.attrezzature = attrezzature_temp
                    st.session_state.sostanze = sostanze_temp
                    st.session_state.step = 4
                    st.rerun()
                else:
                    st.error("⚠️ Compila i campi obbligatori (Indirizzo, Durata, Descrizione)")


def render_step4():
    st.markdown("### Fase 4: Analisi Rischi")
    client = get_openai_client()
    descrizione = st.session_state.cantiere.get('descrizione', '')
    
    if client and descrizione:
        st.markdown('<div class="card-ai"><strong>🤖 Analisi AI</strong></div>', unsafe_allow_html=True)
        if st.button("🔍 ANALIZZA CON AI", type="primary", use_container_width=True):
            with st.spinner("Analizzo..."):
                risultato = ai_analizza_descrizione(descrizione)
                if risultato:
                    st.session_state.rischi_ai = risultato
                    lavorazioni_trovate = risultato.get('lavorazioni_identificate', [])
                    for key in DIZIONARIO_LAVORAZIONI.keys():
                        is_sel = key in lavorazioni_trovate
                        st.session_state.lavorazioni_selezionate[key] = is_sel
                        st.session_state[f"cb_{key}"] = is_sel
                    st.session_state.ai_analisi_fatta = True
                    st.rerun()
                    
        if st.session_state.ai_analisi_fatta and st.session_state.rischi_ai:
            lav = st.session_state.rischi_ai.get('lavorazioni_identificate', [])
            st.success(f"✅ Trovate {len(lav)} lavorazioni")
    
    st.markdown("---")
    st.markdown("#### ✅ Seleziona Lavorazioni")
    
    cols = st.columns(2)
    for i, (key, data) in enumerate(DIZIONARIO_LAVORAZIONI.items()):
        with cols[i % 2]:
            default_val = st.session_state.get(f"cb_{key}", st.session_state.lavorazioni_selezionate.get(key, False))
            checked = st.checkbox(data['nome'], value=default_val, key=f"cb_{key}")
            st.session_state.lavorazioni_selezionate[key] = checked
    
    selected = [k for k, v in st.session_state.lavorazioni_selezionate.items() if v]
    
    if selected:
        st.markdown("---")
        st.markdown(f"#### 📋 Anteprima ({len(selected)})")
        for key in selected:
            data = DIZIONARIO_LAVORAZIONI[key]
            with st.expander(f"📋 {data['nome']}", expanded=False):
                st.write(data['descrizione_tecnica'])
    
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("← Indietro", use_container_width=True):
            st.session_state.step = 3
            st.rerun()
    with c2:
        if st.button("Avanti →", use_container_width=True, disabled=(len(selected) == 0)):
            st.session_state.step = 5
            st.rerun()
    
    if not selected:
        st.warning("⚠️ Seleziona almeno una lavorazione")


def render_step5():
    st.markdown("### Fase 5: Generazione POS")
    selected = [k for k, v in st.session_state.lavorazioni_selezionate.items() if v]
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**🏢 Impresa:**")
        st.write(f"**{st.session_state.ditta['ragione_sociale']}**")
        st.write(f"P.IVA: {st.session_state.ditta['piva_cf']}")
        st.write(f"Lavoratori: {len(st.session_state.lavoratori)}")
    with c2:
        st.markdown("**🏗️ Cantiere:**")
        st.write(f"**{st.session_state.cantiere['indirizzo']}**")
        st.write(f"Lavorazioni: {len(selected)}")
        st.write(f"Attrezzature: {len(st.session_state.attrezzature)}")
    
    # Riepilogo
    with st.expander("📋 Riepilogo Completo", expanded=False):
        st.markdown("**Lavoratori:**")
        for lav in st.session_state.lavoratori:
            st.write(f"- {lav['nome']} ({lav['mansione']}) - {lav['formazione']}")
        if st.session_state.attrezzature:
            st.markdown("**Attrezzature:**")
            for attr in st.session_state.attrezzature:
                st.write(f"- {attr['nome']} {attr.get('marca', '')}")
        if st.session_state.sostanze:
            st.markdown("**Sostanze:**")
            for sost in st.session_state.sostanze:
                st.write(f"- {sost['nome']} ({sost.get('frasi_h', 'N.D.')})")
    
    # Valutazione AI
    st.markdown("---")
    client = get_openai_client()
    if client:
        st.markdown('<div class="card-ai"><strong>🤖 Verifica Documento</strong></div>', unsafe_allow_html=True)
        if st.button("✅ Verifica Completezza", use_container_width=True):
            with st.spinner("Verifico..."):
                val = ai_valuta_completezza({'ditta': st.session_state.ditta, 'cantiere': st.session_state.cantiere, 'addetti': st.session_state.addetti, 'lavorazioni': selected})
                score = val.get('score', 100)
                st.progress(score / 100)
                if score >= 95:
                    st.success(f"🎉 **PERFETTO! {score}/100** - Documento completo!")
                elif score >= 85:
                    st.success(f"✅ **OTTIMO! {score}/100**")
                else:
                    st.warning(f"⚠️ **{score}/100** - Verifica i dati")
    
    st.markdown("---")
    st.markdown('<div class="card" style="background:#FFF3E0;border-left-color:#FF9800;"><strong>⚠️ DICHIARAZIONE</strong><br>Il documento deve essere verificato e firmato dal Datore di Lavoro.</div>', unsafe_allow_html=True)
    
    disclaimer = st.checkbox("Dichiaro che i dati sono veritieri", value=st.session_state.disclaimer_ok)
    st.session_state.disclaimer_ok = disclaimer
    
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("← Indietro", use_container_width=True):
            st.session_state.step = 4
            st.rerun()
    with c2:
        if st.button("📄 GENERA POS", use_container_width=True, disabled=(not disclaimer), type="primary"):
            with st.spinner("Generazione PDF professionale..."):
                try:
                    pdf_bytes = genera_pdf_pos(
                        st.session_state.ditta,
                        st.session_state.cantiere,
                        st.session_state.addetti,
                        selected,
                        st.session_state.rischi_ai,
                        st.session_state.lavoratori,
                        st.session_state.attrezzature,
                        st.session_state.sostanze
                    )
                    st.success("✅ POS generato con successo!")
                    nome_file = f"POS_{date.today().strftime('%Y%m%d')}.pdf"
                    st.download_button("📥 SCARICA PDF", pdf_bytes, nome_file, "application/pdf", use_container_width=True)
                except Exception as e:
                    st.error(f"Errore: {str(e)}")


# ==============================================================================
# MAIN
# ==============================================================================
def main():
    init_session()
    render_header()
    render_sidebar()
    
    if st.session_state.step == 1:
        render_step1()
    elif st.session_state.step == 2:
        render_step2()
    elif st.session_state.step == 3:
        render_step3()
    elif st.session_state.step == 4:
        render_step4()
    elif st.session_state.step == 5:
        render_step5()


if __name__ == "__main__":
    main()