# 🏗️ CantiereSicuro - Generatore POS

Sistema completo per la generazione di Piani Operativi di Sicurezza conformi al D.Lgs 81/08.

## 📁 Struttura File

```
CantiereSicuro/
├── app.py                 # App principale (generatore POS)
├── main.py                # Entry point con landing + auth
├── auth_manager.py        # Gestione login/registrazione
├── database.py            # Operazioni database Supabase
├── license_manager.py     # Validazione licenze Lemon Squeezy
├── landing.py             # Landing page
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
cp secrets.toml .streamlit/secrets.toml
```

### 4. Avvia l'applicazione

**Opzione A - Solo generatore POS (senza auth):**
```bash
streamlit run app.py
```

**Opzione B - Sistema completo con landing e auth:**
```bash
streamlit run main.py
```

## 💰 Piani e Prezzi

| Piano | Prezzo | POS/mese | Funzionalità |
|-------|--------|----------|--------------|
| **Free** | €0 | 1 totale | POS base, no salvataggio |
| **Base** | €29,99/mese | 5 | Salva anagrafiche, storico |
| **Pro** | €79,99/mese | 20 | AI avanzata, supporto prioritario |
| **Unlimited** | €119,99/mese | ∞ | Tutto illimitato |

## 🔐 Autenticazione

Il sistema usa **Supabase Auth** per:
- Registrazione utenti con email
- Login sicuro
- Reset password via email

## 💳 Pagamenti

I pagamenti sono gestiti da **Lemon Squeezy**:
1. L'utente acquista un piano
2. Riceve una chiave licenza via email
3. Inserisce la chiave nell'app
4. L'app valida la chiave con l'API Lemon Squeezy
5. Il piano viene attivato

## 📄 Licenza

Tutti i diritti riservati © 2025
