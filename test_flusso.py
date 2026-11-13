from supabase import create_client

URL = "https://hzfqsliadkzekdpxtvnd.supabase.co"
KEY = "sb_publishable_sn6GdpLbig5pNpf-YqwPfg_9T2ATotO"

supabase = create_client(URL, KEY)

email_test = "armatore.meteor@esempio.it"
password_test = "PasswordSicura123!"

# 1. Login diretto (l'utente esiste già!)
auth_res = supabase.auth.sign_in_with_password({"email": email_test, "password": password_test})
user_id = auth_res.user.id
print("Login effettuato! ID Utente:", user_id)

# 2. Scarichiamo il template del Meteor dal database
template = supabase.table("classi_template").select("*").eq("id", "meteor").single().execute()
dati_base = template.data["dati_template"]

# 3. L'utente personalizza un dato prima di salvare (es. tensione sartie alte con vento medio a 25)
dati_base["matrice_vento"][1]["sartie_alte_v1"] = 25

# 4. Salviamo la nuova barca collegata all'utente loggato
nuova_barca = {
    "owner_id": user_id,
    "classe_id": "meteor",
    "nome_barca": "Pequod",
    "numero_velico": "ITA 452",
    "dati_regolazioni": dati_base
}

res_insert = supabase.table("barche").insert(nuova_barca).execute()
print("Barca salvata con successo! ID Barca:", res_insert.data[0]["id"])

# 5. Leggiamo le barche visibili a questo utente
mie_barche = supabase.table("barche").select("nome_barca, numero_velico, dati_regolazioni").execute()
print("Barche nel mio profilo:", mie_barche.data)