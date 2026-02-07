# 🏗️ POS FACILE - Generatore POS con AI

Sistema completo per la generazione di Piani Operativi di Sicurezza conformi al D.Lgs 81/08, progettato per geometri, ingegneri e consulenti sicurezza.

## 📁 Struttura File

```
POSFacile/
├── app.py                 # App principale (generatore POS a 5 fasi)
├── main.py                # Entry point con landing + auth
├── landing.py             # Landing page (versione alternativa)
├── auth_manager.py        # Gestione login/registrazione (Supabase Auth)
├── database.py            # Operazioni database Supabase
├── license_manager.py     # Validazione licenze Lemon Squeezy
├── requirements.txt       # Dipendenze Python
├── supabase_schema.sql    # Schema database (da eseguire su Supabase)
└── .streamlit/
    └── secrets.toml       # Credenziali (NON committare!)
```

## 🚀 Setup Iniziale

### 1. Installa le dipendenze

```bash
pip install -r requirements.txt
```

### 2. Configura Supabase

1. Vai su Supabase SQL Editor
2. Crea una **New Query**
3. Incolla il contenuto di `supabase_schema.sql`
4. Clicca **Run** per eseguire

### 3. Configura i Secrets

Crea la cartella `.streamlit` e il file `secrets.toml`:

```bash
mkdir -p .streamlit
```

Contenuto di `.streamlit/secrets.toml`:

```toml
SUPABASE_URL = "https://xxx.supabase.co"
SUPABASE_ANON_KEY = "eyJ..."
OPENAI_API_KEY = "sk-..."

[lemon_squeezy]
api_key = "..."

CHECKOUT_STARTER = "https://posfacile.lemonsqueezy.com/checkout/buy/..."
CHECKOUT_PROFESSIONAL = "https://posfacile.lemonsqueezy.com/checkout/buy/..."
CHECKOUT_UNLIMITED = "https://posfacile.lemonsqueezy.com/checkout/buy/..."
```

### 4. Avvia l'applicazione

```bash
streamlit run main.py
```

## 💰 Piani e Prezzi

| Piano | Prezzo | POS/mese | Target |
|-------|--------|----------|--------|
| **Free** | €0 | 1 totale | Prova su cantiere reale |
| **Starter** | €9,99/mese | 3 | Professionista occasionale |
| **Professional** | €24,99/mese | 10 | Geometra / consulente attivo |
| **Unlimited** | €49,99/mese | ∞ | Studio tecnico / alto volume |

## 🎯 Target

Professionisti della sicurezza in cantiere: geometri, ingegneri civili/edili, RSPP, CSP/CSE, consulenti sicurezza. Chi redige POS per conto delle imprese esecutrici.

## 🔐 Autenticazione

Supabase Auth: registrazione con email, login, reset password.

## 💳 Pagamenti

Lemon Squeezy: acquisto piano → chiave licenza via email → attivazione nell'app.

## 📄 Licenza

Tutti i diritti riservati © 2026 POS FACILE
