import copy
from supabase import create_client

URL = "https://hzfqsliadkzekdpxtvnd.supabase.co"
KEY = "sb_publishable_sn6GdpLbig5pNpf-YqwPfg_9T2ATotO"
supabase = create_client(URL, KEY)


def login_utente(email: str, password: str):
    res = supabase.auth.sign_in_with_password({"email": email, "password": password})
    return res.user

def registra_utente(email: str, password: str):
    res = supabase.auth.sign_up({"email": email.strip().lower(), "password": password})
    if not res.user:
        raise ValueError("Impossibile completare la registrazione.")
    if not res.session:
        # Succede se l'email esiste già oppure se 'Confirm email' è ancora attivo su Supabase
        raise ValueError("Registrazione inviata: verifica che l'email non sia già registrata o conferma l'indirizzo.")
    return res.user

def get_barche_e_permessi(user_id: str):
    barche = supabase.table("barche").select("*").execute().data
    cond = supabase.table("condivisioni").select("barca_id, permesso").eq("utente_id", user_id).execute().data
    permessi = {row["barca_id"]: row["permesso"] for row in cond}
    return barche, permessi


def get_templates():
    return supabase.table("classi_template").select("id, nome_classe, dati_template").execute().data


def crea_nuova_barca(owner_id: str, template: dict, nome_barca: str, numero_velico: str):
    dati_iniziali = copy.deepcopy(template["dati_template"])
    nuova = {
        "owner_id": owner_id,
        "classe_id": template["id"],
        "nome_barca": nome_barca.strip(),
        "numero_velico": numero_velico.strip() if numero_velico else "",
        "dati_regolazioni": dati_iniziali,
    }
    res = supabase.table("barche").insert(nuova).execute()
    return res.data[0]


def aggiorna_regolazioni(barca_id: str, dati_regolazioni: dict):
    supabase.table("barche").update({"dati_regolazioni": dati_regolazioni}).eq("id", barca_id).execute()


def get_condivisioni_barca(barca_id: str):
    # Recupera le condivisioni attive associando l'email dalla tabella profili
    conds = supabase.table("condivisioni").select("id, utente_id, permesso").eq("barca_id", barca_id).execute().data
    risultato = []
    for c in conds:
        prof = supabase.table("profili").select("email").eq("id", c["utente_id"]).execute().data
        email = prof[0]["email"] if prof else "Utente sconosciuto"
        risultato.append({"id": c["id"], "utente_id": c["utente_id"], "email": email, "permesso": c["permesso"]})
    return risultato


def condividi_barca_con_email(barca_id: str, email_invitato: str, permesso: str):
    # Cerca l'utente tramite email
    prof = supabase.table("profili").select("id").eq("email", email_invitato.strip().lower()).execute().data
    if not prof:
        raise ValueError("Nessun utente registrato trovato con questa email.")
    
    utente_id = prof[0]["id"]
    record = {
        "barca_id": barca_id,
        "utente_id": utente_id,
        "permesso": permesso,
    }
    supabase.table("condivisioni").upsert(record, on_conflict="barca_id,utente_id").execute()


def rimuovi_condivisione(condivisione_id: str):
    supabase.table("condivisioni").delete().eq("id", condivisione_id).execute()