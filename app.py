# -*- coding: utf-8 -*-
"""
POS FACILE - Generatore POS D.Lgs 81/08
"""

import streamlit as st
from fpdf import FPDF
from datetime import datetime, date, timedelta
from io import BytesIO
import re
import json

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from pypdf import PdfReader, PdfWriter
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

# ==============================================================================
# CONFIGURAZIONE
# ==============================================================================
st.set_page_config(page_title="POS FACILE", page_icon="🏗️", layout="wide")

st.markdown("""
<style>
    /* ===== RESET FONT SIZE GLOBALE - AGGRESSIVO ===== */
    html, body, [class*="css"] {
        font-size: 18px !important;
    }
    
    /* Main container */
    .main .block-container {
        font-size: 18px !important;
    }
    
    /* Tutti gli elementi di testo */
    p, span, div, label, li, td, th {
        font-size: 18px !important;
        line-height: 1.5 !important;
    }
    
    /* Titoli h3 (### Fase X) */
    h3, .stMarkdown h3 {
        font-size: 28px !important;
        font-weight: 700 !important;
        margin-bottom: 1rem !important;
    }
    
    /* Titoli h5 (##### Sezione) */
    h5, .stMarkdown h5 {
        font-size: 22px !important;
        font-weight: 600 !important;
        margin-top: 1rem !important;
    }
    
    /* INPUT FIELDS - Selettori specifici Streamlit */
    [data-testid="stTextInput"] input,
    [data-testid="textInputRootElement"] input,
    .stTextInput input {
        font-size: 18px !important;
        padding: 14px 12px !important;
        min-height: 50px !important;
    }
    
    /* Text Area */
    [data-testid="stTextArea"] textarea,
    .stTextArea textarea {
        font-size: 18px !important;
        padding: 14px 12px !important;
        line-height: 1.5 !important;
    }
    
    /* Number Input */
    [data-testid="stNumberInput"] input,
    .stNumberInput input {
        font-size: 18px !important;
        padding: 14px 12px !important;
    }
    
    /* LABELS - Sopra gli input */
    [data-testid="stTextInput"] label,
    [data-testid="stTextArea"] label,
    [data-testid="stNumberInput"] label,
    [data-testid="stSelectbox"] label,
    .stTextInput label p,
    .stTextArea label p,
    .stNumberInput label p {
        font-size: 17px !important;
        font-weight: 600 !important;
        margin-bottom: 6px !important;
    }
    
    /* CHECKBOX */
    [data-testid="stCheckbox"] label,
    [data-testid="stCheckbox"] span,
    .stCheckbox label {
        font-size: 18px !important;
    }
    
    /* RADIO BUTTONS */
    [data-testid="stRadio"] label,
    [data-testid="stRadio"] div[role="radiogroup"] label,
    .stRadio label {
        font-size: 18px !important;
    }
    
    /* Placeholder text */
    input::placeholder, textarea::placeholder {
        font-size: 16px !important;
        opacity: 0.7 !important;
    }
    
    /* BOTTONI */
    button, .stButton button, .stFormSubmitButton button, .stDownloadButton button {
        font-size: 18px !important;
        padding: 14px 28px !important;
        font-weight: 600 !important;
        min-height: 50px !important;
    }
    
    /* Info/Warning/Success boxes */
    [data-testid="stAlert"], .stAlert {
        font-size: 17px !important;
    }
    [data-testid="stAlert"] p {
        font-size: 17px !important;
    }
    
    /* Expander */
    [data-testid="stExpander"] summary,
    .streamlit-expanderHeader {
        font-size: 19px !important;
        font-weight: 600 !important;
    }
    
    /* Caption e help text */
    .stCaption, [data-testid="stCaption"], small {
        font-size: 15px !important;
    }
    
    /* ===== SIDEBAR SEMPRE FISSA ===== */
    [data-testid="stSidebar"], 
    [data-testid="stSidebar"] * {
        font-size: 17px !important;
    }
    
    /* Sidebar FISSA - sempre visibile */
    [data-testid="stSidebar"] {
        display: block !important;
        width: 300px !important;
        min-width: 300px !important;
        max-width: 300px !important;
        transform: none !important;
        visibility: visible !important;
        background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%) !important;
        border-right: 1px solid #E5E7EB !important;
    }
    
    [data-testid="stSidebar"][aria-expanded="false"],
    [data-testid="stSidebar"][aria-expanded="true"] {
        display: block !important;
        width: 300px !important;
        min-width: 300px !important;
        max-width: 300px !important;
        margin-left: 0 !important;
        transform: none !important;
        visibility: visible !important;
    }
    
    section[data-testid="stSidebar"] > div {
        width: 300px !important;
        padding-top: 1rem !important;
    }
    
    /* NASCONDI SOLO il pulsante freccia di chiusura sidebar (non i pulsanti normali!) */
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebar"] > div > div > div > div > button:first-child {
        display: none !important;
    }
    
    /* Assicurati che i pulsanti di navigazione nella sidebar siano VISIBILI */
    [data-testid="stSidebar"] .stButton > button {
        display: flex !important;
        visibility: visible !important;
        background: white !important;
        color: #374151 !important;
        border: 1px solid #E5E7EB !important;
        font-size: 0.9rem !important;
        padding: 10px 15px !important;
        min-height: 42px !important;
        width: 100% !important;
        justify-content: flex-start !important;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background: #FFF7ED !important;
        border-color: #FF6600 !important;
        color: #FF6600 !important;
    }
    
    /* Stile per pulsanti fasi completate */
    [data-testid="stSidebar"] .stButton > button[kind="secondary"] {
        display: flex !important;
        visibility: visible !important;
    }
    
    /* Form borders - più visibili */
    [data-testid="stForm"] {
        border: 2px solid #E0E0E0 !important;
        border-radius: 12px !important;
        padding: 20px !important;
    }
    
    /* ===== STILI CUSTOM APP ===== */
    .stApp { 
        background-color: #F5F7FA;
    }
    
    .main-header {
        background: linear-gradient(135deg, #0E1117 0%, #1E3A5F 100%);
        color: white; padding: 1.5rem 2rem; border-radius: 12px;
        margin-bottom: 1.5rem;
    }
    .main-header h1 { color: #FF6600; margin: 0; font-size: 2.4rem !important; }
    .main-header p { color: #B0BEC5; margin: 0.3rem 0 0 0; font-size: 18px !important; }
    
    .card {
        background: white; padding: 1.5rem; border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08); border-left: 4px solid #FF6600; margin-bottom: 1rem;
        font-size: 18px !important;
    }
    .card-ai {
        background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
        border-left: 4px solid #1976D2; padding: 1rem; border-radius: 8px; margin: 1rem 0;
        font-size: 18px !important;
    }
    .card-normativa {
        background: #FFF8E1; border-left: 4px solid #FFA000;
        padding: 1rem; border-radius: 8px; margin: 1rem 0;
        font-size: 18px !important;
    }
    .stButton>button {
        background-color: #FF6600; color: white; font-weight: 600;
        border: none; padding: 0.9rem 1.5rem; border-radius: 8px;
        font-size: 18px !important;
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
    },
    "altro_generico": {
        "nome": "Altra Lavorazione Generica",
        "descrizione_tecnica": "Lavorazione specifica non presente nelle categorie standard. Richiede analisi puntuale dei rischi in base alla situazione di cantiere.",
        "rischi": [
            {"nome": "Rischi specifici dell'attivita", "gravita": "ALTA", "descrizione": "Rischi derivanti dalla natura specifica delle operazioni (Vedi Analisi AI)", "normativa": "Art. 28 D.Lgs 81/08"},
            {"nome": "Interferenze", "gravita": "MEDIA", "descrizione": "Rischi da contatto con altre lavorazioni o personale", "normativa": "Art. 26 D.Lgs 81/08"},
            {"nome": "Movimentazione carichi", "gravita": "MEDIA", "descrizione": "Possibile movimentazione manuale di materiali", "normativa": "Titolo VI D.Lgs 81/08"}
        ],
        "dpi_obbligatori": [
            {"nome": "Scarpe antinfortunistiche", "norma": "EN ISO 20345", "uso": "Sempre"},
            {"nome": "Guanti di protezione", "norma": "EN 388", "uso": "Durante manipolazioni"},
            {"nome": "DPI specifici aggiuntivi", "norma": "Da definire", "uso": "In base all'analisi rischi"}
        ],
        "misure_prevenzione": [
            "Analisi preventiva dei rischi specifici prima dell'inizio lavori",
            "Delimitazione dell'area operativa",
            "Utilizzo di attrezzature conformi e marchiate CE",
            "Coordinamento con il preposto per le fasi critiche",
            "Mantenere ordine e pulizia nell'area di lavoro"
        ],
        "attrezzature": ["Attrezzatura specifica da definire"],
        "formazione_richiesta": ["Formazione specifica per la mansione", "Addestramento attrezzature"]
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
    """
    Analizza la descrizione dei lavori con AI e identifica:
    - Lavorazioni pertinenti
    - Rischi aggiuntivi specifici
    - Note per il RSPP
    - Attrezzature suggerite
    - DPI consigliati
    """
    client = get_openai_client()
    if not client or not descrizione.strip():
        return None
    
    lavorazioni_disponibili = {k: v['nome'] for k, v in DIZIONARIO_LAVORAZIONI.items()}
    
    prompt = f"""Sei un RSPP esperto in sicurezza cantieri (D.Lgs 81/08).
Analizza questa descrizione lavori e identifica TUTTE le lavorazioni pertinenti.

DESCRIZIONE LAVORI:
"{descrizione}"

LAVORAZIONI DISPONIBILI (usa SOLO queste chiavi):
{json.dumps(lavorazioni_disponibili, ensure_ascii=False, indent=2)}

ISTRUZIONI:
1. Identifica TUTTE le lavorazioni che si applicano alla descrizione
2. Aggiungi rischi specifici NON coperti dalle lavorazioni standard
3. Suggerisci note pratiche per il RSPP
4. Indica il livello di complessità (basso/medio/alto)

Rispondi SOLO con questo JSON:
{{
    "lavorazioni_identificate": ["chiave1", "chiave2"],
    "rischi_aggiuntivi": [
        {{"nome": "Nome Rischio", "gravita": "ALTA/MEDIA/BASSA", "descrizione": "Descrizione dettagliata", "misura": "Misura preventiva"}}
    ],
    "note_rspp": "Note e raccomandazioni specifiche per questo cantiere",
    "complessita": "medio",
    "attrezzature_suggerite": ["Attrezzatura 1", "Attrezzatura 2"],
    "dpi_specifici": ["DPI 1", "DPI 2"]
}}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[{"role": "user", "content": prompt}], 
            temperature=0.3, 
            max_tokens=1500
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = re.sub(r'^```json?\n?', '', content)
            content = re.sub(r'\n?```$', '', content)
        return json.loads(content)
    except Exception as e:
        return None


def ai_genera_descrizione_avanzata(tipo_lavoro, indirizzo="", durata=""):
    """
    Genera una descrizione tecnica professionale per il POS
    con più contesto e dettagli.
    """
    client = get_openai_client()
    if not client:
        return ""
    try:
        contesto = f"Cantiere: {indirizzo}" if indirizzo else ""
        durata_info = f"Durata prevista: {durata}" if durata else ""
        
        prompt = f"""Sei un Coordinatore della Sicurezza esperto D.Lgs 81/08.
Genera una DESCRIZIONE TECNICA PROFESSIONALE per un Piano Operativo di Sicurezza (POS).

TIPO LAVORO: {tipo_lavoro}
{contesto}
{durata_info}

REGOLE TASSATIVE:
1. Stile IMPERSONALE e TECNICO (es: "Esecuzione di...", "Realizzazione di...", "Demolizione di...")
2. VIETATO: frasi commerciali, "team di esperti", "alta qualità", "professionisti"
3. Elenca le FASI OPERATIVE principali in ordine cronologico
4. Includi riferimenti a:
   - Tipologia di demolizioni (se presenti)
   - Tipologia di impianti coinvolti
   - Materiali principali
   - Finiture previste
5. Max 100 parole, frasi brevi e tecniche

Rispondi SOLO con la descrizione tecnica, senza introduzioni."""

        response = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[{"role": "user", "content": prompt}], 
            temperature=0.4, 
            max_tokens=300
        )
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
    """
    Pulisce il testo per il PDF mantenendo gli accenti italiani.
    Usa la codifica latin-1 compatibile con i font standard di FPDF.
    """
    if text is None:
        return "N.D."
    text = str(text).strip()
    if not text:
        return "N.D."
    
    # 1. Normalizzazione caratteri speciali che rompono i PDF standard
    replacements = {
        '€': 'EUR', 
        '’': "'", '‘': "'", 
        '“': '"', '”': '"', 
        '–': '-', '…': '...'
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Rimuovi a capo e tabulazioni eccessive
    text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    
    # 2. Gestione Encoding per FPDF (Helvetica standard usa Latin-1/Windows-1252)
    try:
        # Tenta di codificare in latin-1 (supporta accenti italiani). 
        # 'replace' sostituisce caratteri non supportati (es. Emoji, Cinese) con '?'
        text = text.encode('latin-1', 'replace').decode('latin-1')
    except Exception:
        # Fallback estremo
        text = text.encode('ascii', 'ignore').decode('ascii')

    # 3. Pulizia finale spazi
    while "  " in text:
        text = text.replace("  ", " ")
        
    # Limita lunghezza
    if max_len and len(text) > max_len:
        text = text[:max_len-3] + "..."
        
    return text


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


def merge_pdfs_with_allegati(pos_bytes, allegati_dict):
    """
    Unisce il POS generato con i PDF allegati caricati dall'utente.
    
    Args:
        pos_bytes: bytes del PDF POS generato
        allegati_dict: dict con chiavi 'visura', 'durc', 'attestati', etc. e valori file-like objects
    
    Returns:
        bytes del PDF unificato
    """
    if not PYPDF_AVAILABLE:
        # Se pypdf non è disponibile, ritorna solo il POS
        return pos_bytes
    
    writer = PdfWriter()
    
    # Aggiungi il POS come primo documento
    pos_reader = PdfReader(BytesIO(pos_bytes))
    for page in pos_reader.pages:
        writer.add_page(page)
    
    # Ordine degli allegati
    ordine_allegati = [
        ('visura', 'Visura Camerale'),
        ('durc', 'DURC'),
        ('attestati', 'Attestati Formazione'),
        ('idoneita', 'Idoneità Sanitarie'),
        ('libretti', 'Libretti Attrezzature'),
        ('sds', 'Schede SDS'),
        ('pimus', 'Pi.M.U.S. / Manuali'),
        ('dpi', 'Verbali Consegna DPI'),
        ('altro', 'Altri Allegati')
    ]
    
    # Aggiungi ogni allegato
    for chiave, nome in ordine_allegati:
        if chiave in allegati_dict and allegati_dict[chiave] is not None:
            file_obj = allegati_dict[chiave]
            try:
                # Leggi il file
                file_obj.seek(0)
                allegato_reader = PdfReader(file_obj)
                for page in allegato_reader.pages:
                    writer.add_page(page)
            except Exception as e:
                # Se un allegato non è valido, lo saltiamo
                st.warning(f"⚠️ Impossibile allegare {nome}: {str(e)}")
                continue
    
    # Scrivi il PDF unificato
    output = BytesIO()
    writer.write(output)
    output.seek(0)
    return output.read()


def crea_copertina_allegati():
    """Crea una pagina di separazione per gli allegati"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 24)
    pdf.set_y(100)
    pdf.cell(190, 20, 'ALLEGATI', ln=1, align='C')
    pdf.set_font('Helvetica', '', 12)
    pdf.cell(190, 10, 'Documentazione a corredo del POS', ln=1, align='C')
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
    # Header principale senza pulsanti toggle (sidebar fissa)
    st.markdown('<div class="main-header"><h1>🏗️ POS FACILE</h1><p>Generatore POS - D.Lgs 81/08</p></div>', unsafe_allow_html=True)


def render_sidebar():
    """Sidebar professionale con info SaaS"""
    with st.sidebar:
        # === BRANDING ===
        st.markdown("""
        <div style="text-align: center; padding: 15px 0; border-bottom: 1px solid #E5E7EB; margin-bottom: 20px;">
            <h2 style="color: #1a1a2e; margin: 0; font-size: 1.5rem;">🏗️ POS FACILE</h2>
            <p style="color: #FF6600; margin: 5px 0 0 0; font-size: 0.9rem; font-weight: 600;">Generatore POS con AI</p>
        </div>
        """, unsafe_allow_html=True)
        
        # === INFO PIANO SAAS ===
        # Recupera info dal session_state se disponibili (integrazione con license_manager)
        piano = st.session_state.get('user_plan', 'Free')
        pos_usati = st.session_state.get('pos_used_this_month', 0)
        pos_limite = st.session_state.get('pos_limit', 1)
        user_email = st.session_state.get('user_email', '')
        
        # Colori per piano
        piano_colors = {
            'Free': '#6B7280',
            'Starter': '#3B82F6',
            'Professional': '#FF6600',
            'Unlimited': '#10B981'
        }
        piano_color = piano_colors.get(piano, '#6B7280')
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {piano_color}15, {piano_color}05); 
                    border: 1px solid {piano_color}40; 
                    border-radius: 12px; 
                    padding: 15px; 
                    margin-bottom: 20px;">
            <p style="margin: 0 0 5px 0; color: #64748B; font-size: 0.8rem;">PIANO ATTIVO</p>
            <p style="margin: 0; color: {piano_color}; font-size: 1.3rem; font-weight: 700;">
                {'⭐ ' if piano == 'Professional' else ''}{'🚀 ' if piano == 'Unlimited' else ''}{piano.upper()}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # POS Rimanenti
        if piano != 'Unlimited':
            pos_rimanenti = max(0, pos_limite - pos_usati)
            percent_used = min(pos_usati / pos_limite, 1.0) if pos_limite > 0 else 0
            
            st.markdown(f"""
            <div style="background: #F8FAFC; border-radius: 10px; padding: 12px; margin-bottom: 15px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span style="color: #64748B; font-size: 0.85rem;">POS questo mese</span>
                    <span style="color: #1a1a2e; font-weight: 700;">{pos_usati}/{pos_limite}</span>
                </div>
                <div style="background: #E2E8F0; border-radius: 10px; height: 8px; overflow: hidden;">
                    <div style="background: {'#EF4444' if percent_used >= 0.9 else '#FF6600'}; 
                                width: {percent_used * 100}%; 
                                height: 100%; 
                                border-radius: 10px;"></div>
                </div>
                <p style="margin: 8px 0 0 0; color: {'#EF4444' if pos_rimanenti == 0 else '#10B981'}; 
                          font-size: 0.85rem; font-weight: 600;">
                    {'⚠️ Limite raggiunto!' if pos_rimanenti == 0 else f'✅ {pos_rimanenti} POS rimanenti'}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if pos_rimanenti == 0:
                if st.button("⬆️ Passa a Professional", use_container_width=True, type="primary"):
                    st.session_state.show_upgrade = True
        else:
            st.markdown("""
            <div style="background: #ECFDF5; border-radius: 10px; padding: 12px; margin-bottom: 15px; text-align: center;">
                <p style="margin: 0; color: #10B981; font-weight: 700;">🚀 POS ILLIMITATI</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # === PROGRESSO WIZARD ===
        st.markdown("##### 📋 Progresso")
        st.progress(min(st.session_state.step / 5, 1.0))
        st.caption(f"Fase {st.session_state.step} di 5")
        
        st.markdown("---")
        
        # === NAVIGAZIONE FASI ===
        st.markdown("##### 🧭 Navigazione")
        for num, label in [("1", "Dati Impresa"), ("2", "Organigramma"), ("3", "Dati Cantiere"), ("4", "Analisi Rischi"), ("5", "Genera POS")]:
            step_num = int(num)
            icon = "✅" if step_num < st.session_state.step else ("▶️" if step_num == st.session_state.step else "⬜")
            is_current = step_num == st.session_state.step
            
            # Stile per step corrente
            if is_current:
                st.markdown(f"""
                <div style="background: #FFF7ED; border: 1px solid #FF6600; border-radius: 8px; 
                            padding: 8px 12px; margin: 5px 0;">
                    <span style="color: #FF6600; font-weight: 600;">{icon} {num}. {label}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                if st.button(f"{icon} {num}. {label}", key=f"nav_{num}", use_container_width=True):
                    if step_num <= st.session_state.step + 1:
                        st.session_state.step = step_num
                        st.rerun()
        
        st.markdown("---")
        
        # === ASSISTENTE AI ===
        st.markdown("##### 🤖 Assistente AI")
        domanda = st.text_input("Chiedi:", placeholder="Es: Quando serve il POS?", key="ai_q", label_visibility="collapsed")
        if st.button("💬 Chiedi all'AI", key="ask", use_container_width=True) and domanda:
            with st.spinner("Elaboro..."):
                risposta = ai_assistente(domanda)
                st.info(risposta)
        
        st.markdown("---")
        
        # === AZIONI UTENTE ===
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🏠 Home", use_container_width=True, help="Torna alla landing page"):
                # Reset per tornare alla home
                st.session_state.show_auth = False
                st.session_state.authenticated = False
                st.rerun()
        with col2:
            if st.button("🚪 Esci", use_container_width=True, help="Logout"):
                # Logout
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        
        # === FOOTER SIDEBAR ===
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align: center; padding-top: 10px; border-top: 1px solid #E5E7EB;">
            <p style="color: #94A3B8; font-size: 0.75rem; margin: 0;">
                POS FACILE v2.0<br>
                <a href="#" style="color: #FF6600; text-decoration: none;">Supporto</a> • 
                <a href="#" style="color: #FF6600; text-decoration: none;">Guida</a>
            </p>
        </div>
        """, unsafe_allow_html=True)


def render_step1():
    st.markdown("### Fase 1: Dati Impresa")
    
    # ==========================================================================
    # CARICAMENTO/SALVATAGGIO ANAGRAFICHE
    # ==========================================================================
    db_available = False
    imprese_salvate = []
    user_id = st.session_state.get('user_id', '')
    
    try:
        from database import get_user_imprese, get_impresa_by_id, impresa_to_ditta_dict, get_lavoratori_template, get_attrezzature_template, save_impresa, save_lavoratori_template, save_attrezzature_template, ditta_to_impresa_dict
        db_available = True
        
        if user_id:
            imprese_salvate = get_user_imprese(user_id)
    except ImportError:
        pass
    except Exception as e:
        print(f"Errore caricamento anagrafiche: {e}")
    
    # Mostra sempre la sezione Anagrafiche
    if db_available and user_id:
        if imprese_salvate:
            # CI SONO IMPRESE SALVATE
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%); 
                        border-radius: 12px; padding: 20px; margin-bottom: 20px; color: white;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 1.5rem;">💾</span>
                    <div>
                        <h4 style="margin: 0; color: white;">Anagrafiche Salvate ({len(imprese_salvate)})</h4>
                        <p style="margin: 5px 0 0 0; opacity: 0.9; font-size: 0.9rem;">
                            Seleziona un'impresa per caricare automaticamente tutti i dati
                        </p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([3, 1])
            with col1:
                opzioni = ["-- Seleziona un'impresa salvata --"] + [
                    f"{imp['ragione_sociale']} ({imp.get('piva_cf', 'N/D')})" for imp in imprese_salvate
                ]
                impresa_sel = st.selectbox(
                    "Impresa:",
                    options=opzioni,
                    key="select_impresa_salvata",
                    label_visibility="collapsed"
                )
            
            with col2:
                if st.button("📥 Carica", use_container_width=True, key="btn_carica_impresa"):
                    if impresa_sel != opzioni[0]:
                        idx = opzioni.index(impresa_sel) - 1
                        impresa_id = imprese_salvate[idx]['id']
                        impresa = get_impresa_by_id(impresa_id)
                        
                        if impresa:
                            st.session_state.ditta = impresa_to_ditta_dict(impresa)
                            
                            lavoratori_db = get_lavoratori_template(impresa_id)
                            if lavoratori_db:
                                st.session_state.lavoratori = [
                                    {'nome': l.get('nome', ''), 'mansione': l.get('mansione', ''), 'formazione': l.get('formazione', '')}
                                    for l in lavoratori_db
                                ]
                            
                            attrezzature_db = get_attrezzature_template(impresa_id)
                            if attrezzature_db:
                                st.session_state.attrezzature = [
                                    {'nome': a.get('nome', ''), 'marca': a.get('marca', ''), 'matricola': a.get('matricola', ''), 'verifica': a.get('ultima_verifica', '')}
                                    for a in attrezzature_db
                                ]
                            
                            if impresa.get('addetto_ps') or impresa.get('addetto_antincendio'):
                                st.session_state.addetti['primo_soccorso'] = impresa.get('addetto_ps', '')
                                st.session_state.addetti['antincendio'] = impresa.get('addetto_antincendio', '')
                            
                            st.success(f"✅ Dati caricati: **{impresa.get('ragione_sociale')}**")
                            st.rerun()
                    else:
                        st.warning("Seleziona un'impresa dal menu")
        else:
            # NESSUNA IMPRESA SALVATA
            st.markdown("""
            <div style="background: linear-gradient(135deg, #6B7280 0%, #4B5563 100%); 
                        border-radius: 12px; padding: 20px; margin-bottom: 20px; color: white;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 1.5rem;">💾</span>
                    <div>
                        <h4 style="margin: 0; color: white;">Nessuna Anagrafica Salvata</h4>
                        <p style="margin: 5px 0 0 0; opacity: 0.9; font-size: 0.9rem;">
                            Compila i dati e clicca "💾 Salva Impresa" per riutilizzarli nei prossimi POS
                        </p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
    
    # ==========================================================================
    # FORM DATI IMPRESA
    # ==========================================================================
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
        
        # Checkbox per salvare l'impresa
        st.markdown("---")
        salva_impresa_check = st.checkbox(
            "💾 Salva questa impresa per riutilizzarla nei prossimi POS",
            value=False,
            help="I dati dell'impresa verranno salvati e potrai caricarli automaticamente la prossima volta"
        )
        
        if st.form_submit_button("Avanti →", use_container_width=True):
            if ragione and piva and datore and indirizzo:
                if not rspp_auto and not rspp_esterno:
                    st.error("⚠️ Inserisci il nome del RSPP esterno")
                elif rls_tipo == 'interno_eletto' and not rls_nome:
                    st.error("⚠️ Inserisci il nome del RLS interno eletto")
                elif rls_tipo == 'territoriale' and not rls_territoriale:
                    st.error("⚠️ Inserisci l'ente RLST di riferimento")
                else:
                    # Salva in session_state
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
                    
                    # Salva nel database se checkbox selezionato
                    if salva_impresa_check:
                        if not db_available:
                            st.error("❌ Database non disponibile - import fallito")
                        elif not user_id:
                            st.error(f"❌ User ID mancante: '{user_id}'")
                        else:
                            try:
                                st.info(f"🔍 User ID dalla sessione: `{user_id}`")
                                impresa_data = ditta_to_impresa_dict(st.session_state.ditta, st.session_state.addetti)
                                st.info(f"📤 Dati da salvare: {impresa_data.get('ragione_sociale')}, P.IVA: {impresa_data.get('piva_cf')}")
                                
                                # Provo a salvare con log dettagliato
                                from database import get_supabase_client
                                client = get_supabase_client()
                                
                                if not client:
                                    st.error("❌ Client Supabase non disponibile")
                                else:
                                    st.info("✅ Client Supabase OK")
                                    
                                    # Provo inserimento diretto con più dettagli
                                    impresa_data['user_id'] = user_id
                                    try:
                                        response = client.table('imprese').insert(impresa_data).execute()
                                        st.info(f"📋 Response: {response}")
                                        if response.data:
                                            saved_id = response.data[0].get('id')
                                            st.success(f"✅ Impresa salvata! ID: {saved_id}")
                                            st.session_state.step = 2
                                            import time
                                            time.sleep(2)
                                            st.rerun()
                                        else:
                                            st.error(f"❌ Nessun dato nella response: {response}")
                                    except Exception as insert_err:
                                        st.error(f"❌ Errore INSERT: {str(insert_err)}")
                                        
                            except Exception as e:
                                st.error(f"❌ Errore generale: {str(e)}")
                                import traceback
                                st.code(traceback.format_exc())
                    else:
                        # Se non salva, passa direttamente alla fase 2
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
    """
    Fase 3: Dati Cantiere
    
    MODIFICHE IMPLEMENTATE:
    1. Magic Writer AI POTENZIATO con UI professionale
    2. Contatori attrezzature/sostanze spostati nelle rispettive sezioni
    """
    st.markdown("### Fase 3: Dati Cantiere")
    
    # ==========================================================================
    # MAGIC WRITER AI POTENZIATO
    # ==========================================================================
    client = get_openai_client()
    if client:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #FF6600 0%, #FF8533 100%); 
                    border-radius: 16px; padding: 25px; margin-bottom: 25px; color: white;">
            <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 15px;">
                <span style="font-size: 2.5rem;">✨</span>
                <div>
                    <h3 style="margin: 0; color: white; font-size: 1.4rem;">Magic Writer AI</h3>
                    <p style="margin: 5px 0 0 0; opacity: 0.9; font-size: 0.95rem;">
                        Genera automaticamente la descrizione tecnica professionale per il POS
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Tipi di lavoro comuni
        tipi_lavoro_comuni = [
            "-- Seleziona un tipo comune oppure scrivi sotto --",
            "Ristrutturazione completa appartamento",
            "Rifacimento bagno completo",
            "Rifacimento impianto elettrico",
            "Rifacimento impianto idraulico",
            "Demolizione e ricostruzione tramezzi",
            "Cappotto termico esterno",
            "Rifacimento copertura/tetto",
            "Nuova pavimentazione",
            "Tinteggiatura completa",
            "Manutenzione facciata",
            "Lavori di scavo e fondazioni"
        ]
        
        col1, col2 = st.columns([3, 1])
        with col1:
            tipo_comune = st.selectbox(
                "Tipo di lavoro comune",
                tipi_lavoro_comuni,
                key="select_tipo_lavoro",
                label_visibility="collapsed"
            )
        
        # Input personalizzato
        tipo_lavoro = st.text_input(
            "Oppure descrivi brevemente il tipo di lavoro",
            value="" if tipo_comune == tipi_lavoro_comuni[0] else tipo_comune,
            placeholder="Es: Ristrutturazione completa bagno con sostituzione sanitari, rifacimento impianto idraulico e posa nuovi rivestimenti",
            key="tipo_ai_input"
        )
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            genera_btn = st.button(
                "✨ GENERA DESCRIZIONE CON AI", 
                type="primary", 
                use_container_width=True, 
                key="btn_genera_desc_ai"
            )
        
        if genera_btn:
            testo_da_usare = tipo_lavoro if tipo_lavoro else (tipo_comune if tipo_comune != tipi_lavoro_comuni[0] else "")
            
            if testo_da_usare:
                with st.spinner("✨ Generazione descrizione tecnica professionale..."):
                    # Usa la funzione avanzata con contesto
                    indirizzo = st.session_state.cantiere.get('indirizzo', '')
                    durata = st.session_state.cantiere.get('durata', '')
                    desc = ai_genera_descrizione_avanzata(testo_da_usare, indirizzo, durata)
                    
                    if desc:
                        st.session_state.cantiere['descrizione'] = desc
                        st.success("✅ Descrizione generata! Scorri sotto per visualizzarla e modificarla.")
                        st.rerun()
                    else:
                        st.error("❌ Errore nella generazione. Verifica la chiave API.")
            else:
                st.warning("⚠️ Seleziona un tipo di lavoro o inserisci una descrizione")
        
        # Mostra anteprima se già generata
        if st.session_state.cantiere.get('descrizione'):
            st.markdown("##### 📝 Anteprima Descrizione Generata")
            st.info(st.session_state.cantiere['descrizione'])
            if st.button("🔄 Rigenera", key="btn_rigenera_desc"):
                st.session_state.cantiere['descrizione'] = ''
                st.rerun()
    else:
        # Istruzioni per configurare l'API OpenAI
        st.markdown("""
        <div style="background: linear-gradient(135deg, #FF6600 0%, #FF8533 100%); 
                    border-radius: 16px; padding: 25px; margin-bottom: 25px; color: white;">
            <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 15px;">
                <span style="font-size: 2.5rem;">✨</span>
                <div>
                    <h3 style="margin: 0; color: white; font-size: 1.4rem;">Magic Writer AI</h3>
                    <p style="margin: 5px 0 0 0; opacity: 0.9; font-size: 0.95rem;">
                        Genera automaticamente la descrizione tecnica professionale per il POS
                    </p>
                </div>
            </div>
            <div style="background: rgba(255,255,255,0.15); border-radius: 8px; padding: 12px; margin-top: 10px;">
                <p style="margin: 0; font-size: 0.9rem;">
                    🔑 <strong>Configura l'API OpenAI</strong> per abilitare questa funzione.<br>
                    Aggiungi <code style="background: rgba(0,0,0,0.2); padding: 2px 6px; border-radius: 4px;">OPENAI_API_KEY</code> 
                    in <code style="background: rgba(0,0,0,0.2); padding: 2px 6px; border-radius: 4px;">.streamlit/secrets.toml</code>
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # ==========================================================================
    # INIZIALIZZAZIONE CONTATORI
    # ==========================================================================
    if 'num_attrezzature' not in st.session_state:
        st.session_state.num_attrezzature = len(st.session_state.attrezzature) if st.session_state.attrezzature else 2
    if 'num_sostanze' not in st.session_state:
        st.session_state.num_sostanze = len(st.session_state.sostanze) if st.session_state.sostanze else 0
    
    # ==========================================================================
    # CONTATORI NELLE RISPETTIVE SEZIONI (FUORI DAL FORM)
    # ==========================================================================
    
    st.markdown("---")
    
    # Sezione Attrezzature - Header con titolo a sinistra e contatore a destra
    col_title_attr, col_num_attr = st.columns([4, 1])
    with col_title_attr:
        st.markdown("##### 🔧 Attrezzature di Cantiere")
    with col_num_attr:
        num_attr = st.number_input(
            "Numero attrezzature",
            min_value=0,
            max_value=15,
            value=st.session_state.num_attrezzature,
            key="num_attr_input",
            label_visibility="collapsed",
            help="Numero di attrezzature da inserire"
        )
        st.session_state.num_attrezzature = int(num_attr)
    
    # Sezione Sostanze - Header con titolo a sinistra e contatore a destra
    col_title_sost, col_num_sost = st.columns([4, 1])
    with col_title_sost:
        st.markdown("##### 🧪 Sostanze Pericolose")
    with col_num_sost:
        num_sost = st.number_input(
            "Numero sostanze",
            min_value=0,
            max_value=15,
            value=st.session_state.num_sostanze,
            key="num_sost_input",
            label_visibility="collapsed",
            help="Numero di sostanze pericolose da inserire"
        )
        st.session_state.num_sostanze = int(num_sost)
    
    st.markdown("---")
    
    # ==========================================================================
    # FORM PRINCIPALE
    # ==========================================================================
    with st.form("f3"):
        st.markdown("##### 📍 Localizzazione e Tempi")
        indirizzo = st.text_input(
            "Indirizzo completo cantiere *",
            value=st.session_state.cantiere['indirizzo'],
            placeholder="Via, numero civico, CAP, Città (Provincia)"
        )
        
        c1, c2, c3 = st.columns(3)
        with c1:
            committente = st.text_input(
                "Committente",
                value=st.session_state.cantiere['committente'],
                placeholder="Nome / Ragione Sociale"
            )
        with c2:
            durata = st.text_input(
                "Durata lavori *",
                value=st.session_state.cantiere['durata'],
                placeholder="Es: 15 giorni"
            )
        with c3:
            data_inizio = st.text_input(
                "Data inizio",
                value=st.session_state.cantiere.get('data_inizio', date.today().strftime('%d/%m/%Y'))
            )
        
        st.markdown("##### ⏰ Organizzazione Turni")
        c1, c2 = st.columns(2)
        with c1:
            orario = st.text_input(
                "Orario di lavoro",
                value=st.session_state.cantiere.get('orario_lavoro', '08:00-12:00 / 13:00-17:00'),
                placeholder="08:00-12:00 / 13:00-17:00"
            )
        with c2:
            giorni = st.text_input(
                "Giorni lavorativi",
                value=st.session_state.cantiere.get('giorni_lavoro', 'Lunedi - Venerdi'),
                placeholder="Lunedi - Venerdi"
            )
        
        st.markdown("##### 🚑 Emergenze")
        ospedale = st.text_input(
            "Ospedale/Pronto Soccorso più vicino",
            value=st.session_state.cantiere.get('ospedale_vicino', ''),
            placeholder="Es: Ospedale San Raffaele - Via Olgettina 60, Milano (3 km)"
        )
        
        st.markdown("##### 📝 Descrizione Opere")
        # Il valore viene pre-popolato dal Magic Writer AI se usato
        descrizione = st.text_area(
            "Descrizione dettagliata lavori *",
            value=st.session_state.cantiere['descrizione'],
            height=120,
            help="Descrivi le fasi lavorative principali. Usa il Magic Writer AI sopra per generare automaticamente!"
        )
        
        # ==== TABELLA ATTREZZATURE (dentro il form) ====
        attrezzature_temp = []
        if st.session_state.num_attrezzature > 0:
            st.markdown("---")
            st.caption("🔧 **Dettaglio Attrezzature** - Compila i dati per ogni attrezzatura")
            
            # Header tabella
            hcols = st.columns([3, 2, 2, 2])
            with hcols[0]:
                st.caption("Attrezzatura")
            with hcols[1]:
                st.caption("Marca/Modello")
            with hcols[2]:
                st.caption("Matricola")
            with hcols[3]:
                st.caption("Ultima verifica")
            
            # Valori di default per le prime attrezzature
            attr_default = [
                {'nome': 'Martello demolitore', 'marca': '', 'matricola': '', 'verifica': ''},
                {'nome': 'Smerigliatrice angolare', 'marca': '', 'matricola': '', 'verifica': ''}
            ]
            
            for i in range(st.session_state.num_attrezzature):
                cols = st.columns([3, 2, 2, 2])
                
                # Recupera valori esistenti o default
                def_nome = st.session_state.attrezzature[i]['nome'] if i < len(st.session_state.attrezzature) else (attr_default[i]['nome'] if i < len(attr_default) else '')
                def_marca = st.session_state.attrezzature[i].get('marca', '') if i < len(st.session_state.attrezzature) else ''
                def_matr = st.session_state.attrezzature[i].get('matricola', '') if i < len(st.session_state.attrezzature) else ''
                def_ver = st.session_state.attrezzature[i].get('verifica', '') if i < len(st.session_state.attrezzature) else ''
                
                with cols[0]:
                    a_nome = st.text_input(f"att_nome_{i}", value=def_nome, key=f"an_{i}", placeholder="Nome attrezzatura", label_visibility="collapsed")
                with cols[1]:
                    a_marca = st.text_input(f"att_marca_{i}", value=def_marca, key=f"am_{i}", placeholder="Marca/Modello", label_visibility="collapsed")
                with cols[2]:
                    a_matr = st.text_input(f"att_matr_{i}", value=def_matr, key=f"at_{i}", placeholder="N. matricola", label_visibility="collapsed")
                with cols[3]:
                    a_ver = st.text_input(f"att_ver_{i}", value=def_ver, key=f"av_{i}", placeholder="GG/MM/AAAA", label_visibility="collapsed")
                
                if a_nome:
                    attrezzature_temp.append({
                        'nome': a_nome,
                        'marca': a_marca,
                        'matricola': a_matr,
                        'verifica': a_ver
                    })
        
        # ==== TABELLA SOSTANZE (dentro il form) ====
        sostanze_temp = []
        if st.session_state.num_sostanze > 0:
            st.markdown("---")
            st.caption("🧪 **Dettaglio Sostanze Pericolose** - Le SDS devono essere disponibili in cantiere")
            
            # Header tabella
            hcols = st.columns([3, 2, 3])
            with hcols[0]:
                st.caption("Prodotto")
            with hcols[1]:
                st.caption("Produttore")
            with hcols[2]:
                st.caption("Frasi H (pericolo)")
            
            for i in range(st.session_state.num_sostanze):
                cols = st.columns([3, 2, 3])
                
                # Recupera valori esistenti
                def_nome = st.session_state.sostanze[i]['nome'] if i < len(st.session_state.sostanze) else ''
                def_prod = st.session_state.sostanze[i].get('produttore', '') if i < len(st.session_state.sostanze) else ''
                def_h = st.session_state.sostanze[i].get('frasi_h', '') if i < len(st.session_state.sostanze) else ''
                
                with cols[0]:
                    s_nome = st.text_input(f"sost_nome_{i}", value=def_nome, key=f"sn_{i}", placeholder="Nome commerciale", label_visibility="collapsed")
                with cols[1]:
                    s_prod = st.text_input(f"sost_prod_{i}", value=def_prod, key=f"sp_{i}", placeholder="Produttore", label_visibility="collapsed")
                with cols[2]:
                    s_h = st.text_input(f"sost_h_{i}", value=def_h, key=f"sh_{i}", placeholder="Es: H315, H319, H335", label_visibility="collapsed")
                
                if s_nome:
                    sostanze_temp.append({
                        'nome': s_nome,
                        'produttore': s_prod,
                        'frasi_h': s_h
                    })
        
        # ==== PULSANTI NAVIGAZIONE ====
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
    """
    Fase 4: Analisi Rischi con AI Avanzata
    - Analisi intelligente della descrizione
    - Selezione automatica lavorazioni
    - Visualizzazione rischi aggiuntivi
    - Note RSPP e suggerimenti
    """
    st.markdown("### Fase 4: Analisi Rischi")
    
    client = get_openai_client()
    descrizione = st.session_state.cantiere.get('descrizione', '')
    
    # === SEZIONE AI ANALYSIS ===
    if client:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 16px; padding: 25px; margin-bottom: 25px; color: white;">
            <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 15px;">
                <span style="font-size: 2.5rem;">🤖</span>
                <div>
                    <h3 style="margin: 0; color: white; font-size: 1.4rem;">Analisi Rischi con AI</h3>
                    <p style="margin: 5px 0 0 0; opacity: 0.9; font-size: 0.95rem;">
                        L'intelligenza artificiale analizza la descrizione dei lavori e identifica automaticamente rischi e lavorazioni
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if descrizione:
            # Mostra anteprima descrizione
            with st.expander("📝 Descrizione lavori da analizzare", expanded=False):
                st.info(descrizione)
            
            # Pulsante analisi
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                analizza_btn = st.button(
                    "🔍 ANALIZZA CON INTELLIGENZA ARTIFICIALE", 
                    type="primary", 
                    use_container_width=True,
                    key="btn_analizza_ai"
                )
            
            if analizza_btn:
                with st.spinner("🤖 Analisi in corso... L'AI sta identificando rischi e lavorazioni..."):
                    risultato = ai_analizza_descrizione(descrizione)
                    if risultato:
                        st.session_state.rischi_ai = risultato
                        lavorazioni_trovate = risultato.get('lavorazioni_identificate', [])
                        
                        # Seleziona automaticamente le lavorazioni trovate
                        for key in DIZIONARIO_LAVORAZIONI.keys():
                            is_sel = key in lavorazioni_trovate
                            st.session_state.lavorazioni_selezionate[key] = is_sel
                            st.session_state[f"cb_{key}"] = is_sel
                        
                        st.session_state.ai_analisi_fatta = True
                        st.rerun()
                    else:
                        st.error("❌ Errore durante l'analisi. Verifica la chiave API OpenAI.")
            
            # === RISULTATI ANALISI AI ===
            if st.session_state.get('ai_analisi_fatta') and st.session_state.get('rischi_ai'):
                rischi_ai = st.session_state.rischi_ai
                lavorazioni_trovate = rischi_ai.get('lavorazioni_identificate', [])
                rischi_aggiuntivi = rischi_ai.get('rischi_aggiuntivi', [])
                note_rspp = rischi_ai.get('note_rspp', '')
                complessita = rischi_ai.get('complessita', 'medio')
                attrezzature_sugg = rischi_ai.get('attrezzature_suggerite', [])
                dpi_specifici = rischi_ai.get('dpi_specifici', [])
                
                # Badge complessità
                complessita_colors = {
                    'basso': '#10B981',
                    'medio': '#F59E0B', 
                    'alto': '#EF4444'
                }
                comp_color = complessita_colors.get(complessita, '#F59E0B')
                
                st.markdown(f"""
                <div style="background: #ECFDF5; border: 1px solid #10B981; border-radius: 12px; 
                            padding: 20px; margin: 20px 0;">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px;">
                        <div>
                            <span style="color: #10B981; font-size: 1.5rem;">✅</span>
                            <strong style="font-size: 1.2rem; color: #065F46;">Analisi completata!</strong>
                        </div>
                        <div style="display: flex; gap: 15px; flex-wrap: wrap;">
                            <span style="background: #FF6600; color: white; padding: 5px 15px; border-radius: 20px; font-weight: 600;">
                                {len(lavorazioni_trovate)} Lavorazioni
                            </span>
                            <span style="background: #3B82F6; color: white; padding: 5px 15px; border-radius: 20px; font-weight: 600;">
                                {len(rischi_aggiuntivi)} Rischi Extra
                            </span>
                            <span style="background: {comp_color}; color: white; padding: 5px 15px; border-radius: 20px; font-weight: 600;">
                                Complessità: {complessita.upper()}
                            </span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Mostra rischi aggiuntivi se presenti
                if rischi_aggiuntivi:
                    st.markdown("#### ⚠️ Rischi Aggiuntivi Identificati")
                    for i, rischio in enumerate(rischi_aggiuntivi):
                        gravita = rischio.get('gravita', 'MEDIA')
                        gravita_color = {'ALTA': '#EF4444', 'MEDIA': '#F59E0B', 'BASSA': '#10B981'}.get(gravita, '#F59E0B')
                        
                        st.markdown(f"""
                        <div style="background: white; border-left: 4px solid {gravita_color}; 
                                    padding: 15px; margin: 10px 0; border-radius: 0 8px 8px 0;
                                    box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <strong style="color: #1a1a2e;">{rischio.get('nome', 'Rischio')}</strong>
                                <span style="background: {gravita_color}; color: white; padding: 3px 10px; 
                                             border-radius: 15px; font-size: 0.8rem; font-weight: 600;">
                                    {gravita}
                                </span>
                            </div>
                            <p style="margin: 8px 0 0 0; color: #64748B; font-size: 0.9rem;">
                                {rischio.get('descrizione', '')}
                            </p>
                            {f'<p style="margin: 8px 0 0 0; color: #10B981; font-size: 0.85rem;"><strong>✓ Misura:</strong> {rischio.get("misura", "")}</p>' if rischio.get('misura') else ''}
                        </div>
                        """, unsafe_allow_html=True)
                
                # Note RSPP
                if note_rspp:
                    st.markdown("#### 📋 Note per il RSPP")
                    st.info(note_rspp)
                
                # Suggerimenti
                col1, col2 = st.columns(2)
                with col1:
                    if attrezzature_sugg:
                        st.markdown("##### 🔧 Attrezzature Suggerite")
                        for attr in attrezzature_sugg:
                            st.markdown(f"• {attr}")
                with col2:
                    if dpi_specifici:
                        st.markdown("##### 🦺 DPI Specifici")
                        for dpi in dpi_specifici:
                            st.markdown(f"• {dpi}")
                
                # Pulsante per rigenerare
                if st.button("🔄 Rigenera Analisi", key="btn_rigenera"):
                    st.session_state.ai_analisi_fatta = False
                    st.session_state.rischi_ai = None
                    st.rerun()
        else:
            st.warning("⚠️ **Descrizione mancante** - Torna alla Fase 3 e compila la descrizione dei lavori per attivare l'analisi AI")
    else:
        # Istruzioni dettagliate per configurare l'API OpenAI
        st.markdown("""
        <div style="background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%); 
                    border-radius: 16px; padding: 25px; margin-bottom: 25px; color: white;">
            <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 15px;">
                <span style="font-size: 2.5rem;">🔑</span>
                <div>
                    <h3 style="margin: 0; color: white; font-size: 1.4rem;">Configura l'AI per Analisi Automatica</h3>
                    <p style="margin: 5px 0 0 0; opacity: 0.9; font-size: 0.95rem;">
                        Aggiungi la chiave API OpenAI per abilitare l'analisi automatica dei rischi
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("📋 Come configurare l'API OpenAI", expanded=True):
            st.markdown("""
            **1. Crea il file secrets.toml:**
            
            Nella cartella `.streamlit` del progetto, crea/modifica il file `secrets.toml`:
            
            ```toml
            OPENAI_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxx"
            ```
            
            **2. Ottieni la chiave API:**
            - Vai su [platform.openai.com](https://platform.openai.com)
            - Crea un account o accedi
            - Vai in **API Keys** e crea una nuova chiave
            
            **3. Riavvia Streamlit:**
            ```bash
            streamlit run main.py
            ```
            
            L'AI analizzerà automaticamente la descrizione dei lavori e selezionerà le lavorazioni pertinenti!
            """)
    
    st.markdown("---")
    
    # === SELEZIONE MANUALE LAVORAZIONI ===
    st.markdown("#### ✅ Seleziona Lavorazioni")
    st.caption("Le lavorazioni vengono selezionate automaticamente dall'AI, ma puoi modificarle manualmente")
    
    cols = st.columns(2)
    for i, (key, data) in enumerate(DIZIONARIO_LAVORAZIONI.items()):
        with cols[i % 2]:
            default_val = st.session_state.get(f"cb_{key}", st.session_state.lavorazioni_selezionate.get(key, False))
            checked = st.checkbox(data['nome'], value=default_val, key=f"cb_{key}")
            st.session_state.lavorazioni_selezionate[key] = checked
    
    selected = [k for k, v in st.session_state.lavorazioni_selezionate.items() if v]
    
    # === ANTEPRIMA LAVORAZIONI SELEZIONATE ===
    if selected:
        st.markdown("---")
        st.markdown(f"#### 📋 Dettaglio Lavorazioni Selezionate ({len(selected)})")
        
        for key in selected:
            data = DIZIONARIO_LAVORAZIONI[key]
            with st.expander(f"📋 {data['nome']}", expanded=False):
                st.markdown(f"**Descrizione:** {data['descrizione_tecnica']}")
                
                # Rischi
                st.markdown("**Rischi principali:**")
                for rischio in data.get('rischi', [])[:3]:
                    gravita_color = {'ALTA': '🔴', 'MEDIA': '🟡', 'BASSA': '🟢'}.get(rischio['gravita'], '🟡')
                    st.markdown(f"- {gravita_color} **{rischio['nome']}** ({rischio['gravita']})")
                
                # DPI
                st.markdown("**DPI obbligatori:**")
                dpi_list = ", ".join([d['nome'] for d in data.get('dpi_obbligatori', [])[:4]])
                st.markdown(f"_{dpi_list}_")
    
    st.markdown("---")
    
    # === NAVIGAZIONE ===
    c1, c2 = st.columns(2)
    with c1:
        if st.button("← Indietro", use_container_width=True):
            st.session_state.step = 3
            st.rerun()
    with c2:
        if st.button("Avanti →", use_container_width=True, disabled=(len(selected) == 0), type="primary"):
            st.session_state.step = 5
            st.rerun()
    
    if not selected:
        st.warning("⚠️ Seleziona almeno una lavorazione per continuare")


def render_step5():
    st.markdown("### Fase 5: Generazione POS")
    
    # ==========================================================================
    # VERIFICA LIMITE POS - FONDAMENTALE PER MONETIZZAZIONE
    # ==========================================================================
    try:
        from database import can_generate_pos, increment_pos_counter, save_pos_generato, save_impresa, save_lavoratori_template, save_attrezzature_template, ditta_to_impresa_dict
        db_available = True
    except ImportError:
        db_available = False
    
    user_id = st.session_state.get('user_id', '')
    
    # Verifica limite POS
    can_generate = True
    pos_message = ""
    pos_rimanenti = 1
    
    if db_available and user_id:
        can_generate, pos_message, pos_rimanenti = can_generate_pos(user_id)
    
    # Mostra stato abbonamento
    if can_generate:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #10B981 0%, #059669 100%); 
                    border-radius: 12px; padding: 20px; margin-bottom: 20px; color: white;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h4 style="margin: 0; color: white;">✅ Puoi generare il POS</h4>
                    <p style="margin: 5px 0 0 0; opacity: 0.9;">{pos_message}</p>
                </div>
                <div style="text-align: right;">
                    <span style="font-size: 2rem; font-weight: bold;">{pos_rimanenti}</span>
                    <p style="margin: 0; font-size: 0.8rem; opacity: 0.8;">POS disponibili</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%); 
                    border-radius: 12px; padding: 20px; margin-bottom: 20px; color: white;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h4 style="margin: 0; color: white;">🚫 Limite POS Raggiunto</h4>
                    <p style="margin: 5px 0 0 0; opacity: 0.9;">{pos_message}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Link diretti ai checkout (Fallback hardcoded per garantire il funzionamento)
        LINK_STARTER = "https://posfacile.lemonsqueezy.com/checkout/buy/6154ced3-2892-45fa-a7ef-f08f97c24635"
        LINK_PRO = "https://posfacile.lemonsqueezy.com/checkout/buy/ff234bb0-1d0b-433c-8fbb-a63e907755e6"
        LINK_UNLIMITED = "https://posfacile.lemonsqueezy.com/checkout/buy/59eda380-a79c-45aa-9cba-6962a249a71d"

        # Pulsanti upgrade
        st.markdown("#### 🚀 Passa a un piano superiore")
        col1, col2, col3 = st.columns(3)
        
        # Recupera link dai secrets o usa quelli diretti come fallback sicuro
        checkout_starter = st.secrets.get("CHECKOUT_STARTER", LINK_STARTER)
        checkout_professional = st.secrets.get("CHECKOUT_PROFESSIONAL", LINK_PRO)
        checkout_unlimited = st.secrets.get("CHECKOUT_UNLIMITED", LINK_UNLIMITED)

        with col1:
            st.markdown(f'<a href="{checkout_starter}" target="_blank" style="text-decoration:none;"><div style="background:#3B82F6;color:white;padding:15px;border-radius:10px;text-align:center;font-weight:600;box-shadow: 0 4px 6px rgba(0,0,0,0.1);transition: transform 0.2s;">⭐ Starter - €9,99/mese<br><small>3 POS/mese</small></div></a>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<a href="{checkout_professional}" target="_blank" style="text-decoration:none;"><div style="background:#FF6600;color:white;padding:15px;border-radius:10px;text-align:center;font-weight:600;box-shadow: 0 4px 6px rgba(0,0,0,0.1);transition: transform 0.2s;">💎 Professional - €24,99/mese<br><small>10 POS/mese</small></div></a>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<a href="{checkout_unlimited}" target="_blank" style="text-decoration:none;"><div style="background:#10B981;color:white;padding:15px;border-radius:10px;text-align:center;font-weight:600;box-shadow: 0 4px 6px rgba(0,0,0,0.1);transition: transform 0.2s;">🚀 Unlimited - €49,99/mese<br><small>POS illimitati</small></div></a>', unsafe_allow_html=True)
        
        st.markdown("---")
        if st.button("← Torna indietro", use_container_width=True):
            st.session_state.step = 4
            st.rerun()
        return  # BLOCCA - non può generare
    
    # ==========================================================================
    # RIEPILOGO DATI
    # ==========================================================================
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
    
    # ==========================================================================
    # OPZIONE SALVATAGGIO ANAGRAFICA
    # ==========================================================================
    st.markdown("---")
    st.markdown("### 💾 Salva Anagrafica per Riutilizzo")
    
    salva_anagrafica = st.checkbox(
        "Salva i dati dell'impresa per POS futuri",
        value=True,
        help="I dati dell'impresa, dipendenti e attrezzature saranno salvati e potrai riutilizzarli senza reinserirli"
    )
    
    # ==================== SEZIONE ALLEGATI ====================
    st.markdown("---")
    st.markdown("### 📎 Allegati Documentali (Opzionale)")
    st.info("📌 Carica i documenti PDF da allegare al POS. Verranno uniti in un unico file pronto per l'invio via PEC.")
    
    # Verifica se pypdf è disponibile
    if not PYPDF_AVAILABLE:
        st.warning("⚠️ La libreria `pypdf` non è installata. Gli allegati non saranno uniti al POS. Installa con: `pip install pypdf`")
    
    # File uploaders organizzati in colonne
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📄 Documenti Aziendali**")
        allegato_visura = st.file_uploader(
            "Visura Camerale", 
            type=['pdf'], 
            key="upload_visura",
            help="Visura camerale aggiornata"
        )
        allegato_durc = st.file_uploader(
            "DURC", 
            type=['pdf'], 
            key="upload_durc",
            help="Documento Unico di Regolarità Contributiva"
        )
        allegato_attestati = st.file_uploader(
            "Attestati Formazione", 
            type=['pdf'], 
            key="upload_attestati",
            help="Attestati formazione lavoratori (Art. 37)"
        )
        allegato_idoneita = st.file_uploader(
            "Idoneità Sanitarie", 
            type=['pdf'], 
            key="upload_idoneita",
            help="Certificati idoneità alla mansione"
        )
    
    with col2:
        st.markdown("**🔧 Documenti Tecnici**")
        allegato_libretti = st.file_uploader(
            "Libretti Attrezzature", 
            type=['pdf'], 
            key="upload_libretti",
            help="Libretti d'uso e manutenzione"
        )
        allegato_sds = st.file_uploader(
            "Schede SDS Sostanze", 
            type=['pdf'], 
            key="upload_sds",
            help="Schede Dati di Sicurezza"
        )
        allegato_dpi = st.file_uploader(
            "Verbali Consegna DPI", 
            type=['pdf'], 
            key="upload_dpi",
            help="Verbali di consegna DPI firmati"
        )
        allegato_altro = st.file_uploader(
            "Altri Allegati", 
            type=['pdf'], 
            key="upload_altro",
            help="Eventuali altri documenti"
        )
    
    # Conta allegati caricati
    allegati = {
        'visura': allegato_visura,
        'durc': allegato_durc,
        'attestati': allegato_attestati,
        'idoneita': allegato_idoneita,
        'libretti': allegato_libretti,
        'sds': allegato_sds,
        'dpi': allegato_dpi,
        'altro': allegato_altro
    }
    num_allegati = sum(1 for v in allegati.values() if v is not None)
    
    if num_allegati > 0:
        st.success(f"✅ **{num_allegati} allegat{'o' if num_allegati == 1 else 'i'} caricat{'o' if num_allegati == 1 else 'i'}** - Verranno uniti al POS")
    
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
        # Testo pulsante dinamico in base agli allegati
        btn_text = f"📄 GENERA POS COMPLETO ({num_allegati} allegati)" if num_allegati > 0 else "📄 GENERA POS"
        
        if st.button(btn_text, use_container_width=True, disabled=(not disclaimer), type="primary"):
            with st.spinner("Generazione PDF professionale..."):
                try:
                    # Genera il POS
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
                    
                    # Se ci sono allegati e pypdf è disponibile, unisci i PDF
                    if num_allegati > 0 and PYPDF_AVAILABLE:
                        with st.spinner(f"Unione {num_allegati} allegati..."):
                            pdf_bytes = merge_pdfs_with_allegati(pdf_bytes, allegati)
                        st.success(f"✅ POS generato con {num_allegati} allegati!")
                        nome_file = f"POS_COMPLETO_{date.today().strftime('%Y%m%d')}.pdf"
                    else:
                        st.success("✅ POS generato con successo!")
                        nome_file = f"POS_{date.today().strftime('%Y%m%d')}.pdf"
                    
                    # ============================================================
                    # INCREMENTA CONTATORE POS (FONDAMENTALE PER MONETIZZAZIONE!)
                    # ============================================================
                    if db_available and user_id:
                        try:
                            # Incrementa contatore
                            increment_pos_counter(user_id)
                            
                            # Salva nel log storico
                            impresa_id = st.session_state.ditta.get('_impresa_id', None)
                            save_pos_generato(
                                user_id, 
                                impresa_id,
                                st.session_state.cantiere,
                                selected,
                                nome_file
                            )
                            
                            # Salva anagrafica se richiesto
                            if salva_anagrafica:
                                # Converti ditta nel formato database
                                impresa_data = ditta_to_impresa_dict(st.session_state.ditta, st.session_state.addetti)
                                saved_id = save_impresa(user_id, impresa_data)
                                
                                if saved_id:
                                    # Salva lavoratori e attrezzature collegati
                                    save_lavoratori_template(saved_id, st.session_state.lavoratori)
                                    save_attrezzature_template(saved_id, st.session_state.attrezzature)
                                    st.info("💾 Anagrafica salvata! Potrai riutilizzarla per i prossimi POS.")
                        except Exception as e:
                            # Non bloccare il download se c'è errore nel contatore
                            print(f"Errore contatore/salvataggio: {e}")
                    
                    # Mostra download button
                    st.download_button(
                        "📥 SCARICA PDF" + (" CON ALLEGATI" if num_allegati > 0 else ""), 
                        pdf_bytes, 
                        nome_file, 
                        "application/pdf", 
                        use_container_width=True
                    )
                    
                    # Messaggio post-generazione
                    if db_available and user_id:
                        new_can, new_msg, new_remaining = can_generate_pos(user_id)
                        if new_remaining > 0:
                            st.info(f"📊 Ti rimangono ancora **{new_remaining} POS** disponibili.")
                        elif not new_can:
                            st.warning("⚠️ Hai esaurito i POS disponibili. Passa a un piano superiore per continuare!")
                    
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

