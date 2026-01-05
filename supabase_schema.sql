-- ============================================================================
-- CANTIERE SICURO - SCHEMA DATABASE SUPABASE
-- Esegui questo SQL nel SQL Editor di Supabase
-- ============================================================================

-- 1. TABELLA PROFILI UTENTI (estende auth.users)
CREATE TABLE public.profiles (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    nome TEXT,
    cognome TEXT,
    telefono TEXT,
    
    -- Piano abbonamento
    piano TEXT DEFAULT 'free' CHECK (piano IN ('free', 'base', 'pro', 'unlimited')),
    license_key TEXT,
    license_activated_at TIMESTAMPTZ,
    
    -- Contatori
    pos_generati_totale INTEGER DEFAULT 0,
    pos_generati_mese INTEGER DEFAULT 0,
    mese_contatore INTEGER DEFAULT EXTRACT(MONTH FROM NOW()),
    anno_contatore INTEGER DEFAULT EXTRACT(YEAR FROM NOW()),
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. TABELLA IMPRESE (anagrafiche salvate)
CREATE TABLE public.imprese (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    
    -- Dati anagrafici
    ragione_sociale TEXT NOT NULL,
    piva_cf TEXT NOT NULL,
    indirizzo TEXT,
    telefono TEXT,
    codice_ateco TEXT,
    num_dipendenti TEXT,
    
    -- Figure sicurezza
    datore_lavoro TEXT,
    rspp_autonomo BOOLEAN DEFAULT TRUE,
    rspp TEXT,
    medico_competente TEXT,
    
    -- RLS
    rls_tipo TEXT DEFAULT 'non_eletto' CHECK (rls_tipo IN ('interno_eletto', 'non_eletto', 'territoriale')),
    rls_nome TEXT,
    rls_territoriale TEXT,
    
    -- Addetti emergenza
    addetto_ps TEXT,
    addetto_antincendio TEXT,
    
    -- Flags
    is_default BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. TABELLA STORICO POS GENERATI
CREATE TABLE public.pos_generati (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    impresa_id UUID REFERENCES public.imprese(id) ON DELETE SET NULL,
    
    -- Dati cantiere
    cantiere_indirizzo TEXT NOT NULL,
    cantiere_committente TEXT,
    cantiere_durata TEXT,
    lavorazioni TEXT[], -- Array di lavorazioni selezionate
    
    -- Metadata
    nome_file TEXT,
    data_generazione TIMESTAMPTZ DEFAULT NOW()
);

-- 4. TABELLA LAVORATORI (opzionale, per salvare template)
CREATE TABLE public.lavoratori_template (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    impresa_id UUID REFERENCES public.imprese(id) ON DELETE CASCADE NOT NULL,
    
    nome TEXT NOT NULL,
    mansione TEXT,
    formazione TEXT,
    idoneita_sanitaria TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. TABELLA ATTREZZATURE (opzionale, per salvare template)
CREATE TABLE public.attrezzature_template (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    impresa_id UUID REFERENCES public.imprese(id) ON DELETE CASCADE NOT NULL,
    
    nome TEXT NOT NULL,
    marca TEXT,
    matricola TEXT,
    ultima_verifica TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- FUNZIONI E TRIGGER
-- ============================================================================

-- Funzione per aggiornare updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger per profiles
CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger per imprese
CREATE TRIGGER update_imprese_updated_at
    BEFORE UPDATE ON public.imprese
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Funzione per creare profilo automaticamente alla registrazione
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email)
    VALUES (NEW.id, NEW.email);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger per creare profilo alla registrazione
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();

-- Funzione per resettare contatore mensile
CREATE OR REPLACE FUNCTION reset_monthly_counter()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.mese_contatore != EXTRACT(MONTH FROM NOW()) OR 
       NEW.anno_contatore != EXTRACT(YEAR FROM NOW()) THEN
        NEW.pos_generati_mese = 0;
        NEW.mese_contatore = EXTRACT(MONTH FROM NOW());
        NEW.anno_contatore = EXTRACT(YEAR FROM NOW());
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_monthly_reset
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW
    EXECUTE FUNCTION reset_monthly_counter();

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) - IMPORTANTE PER SICUREZZA
-- ============================================================================

-- Abilita RLS su tutte le tabelle
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.imprese ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.pos_generati ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.lavoratori_template ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.attrezzature_template ENABLE ROW LEVEL SECURITY;

-- Policy per profiles: utente può vedere/modificare solo il proprio profilo
CREATE POLICY "Users can view own profile" ON public.profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.profiles
    FOR UPDATE USING (auth.uid() = id);

-- Policy per imprese: utente può gestire solo le proprie
CREATE POLICY "Users can manage own imprese" ON public.imprese
    FOR ALL USING (auth.uid() = user_id);

-- Policy per pos_generati: utente può vedere solo i propri
CREATE POLICY "Users can manage own pos" ON public.pos_generati
    FOR ALL USING (auth.uid() = user_id);

-- Policy per lavoratori_template
CREATE POLICY "Users can manage own lavoratori" ON public.lavoratori_template
    FOR ALL USING (
        auth.uid() = (SELECT user_id FROM public.imprese WHERE id = impresa_id)
    );

-- Policy per attrezzature_template
CREATE POLICY "Users can manage own attrezzature" ON public.attrezzature_template
    FOR ALL USING (
        auth.uid() = (SELECT user_id FROM public.imprese WHERE id = impresa_id)
    );

-- ============================================================================
-- INDICI PER PERFORMANCE
-- ============================================================================

CREATE INDEX idx_imprese_user_id ON public.imprese(user_id);
CREATE INDEX idx_pos_generati_user_id ON public.pos_generati(user_id);
CREATE INDEX idx_pos_generati_data ON public.pos_generati(data_generazione DESC);
CREATE INDEX idx_lavoratori_impresa ON public.lavoratori_template(impresa_id);
CREATE INDEX idx_attrezzature_impresa ON public.attrezzature_template(impresa_id);

-- ============================================================================
-- FATTO! Ora il database è pronto.
-- ============================================================================
