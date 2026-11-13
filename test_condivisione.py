from supabase import create_client

URL = "https://hzfqsliadkzekdpxtvnd.supabase.co"
KEY = "sb_publishable_sn6GdpLbig5pNpf-YqwPfg_9T2ATotO"
supabase = create_client(URL, KEY)

email_armatore = "armatore.meteor@esempio.it"
pass_armatore = "PasswordSicura123!"

email_prodiere = "prodiere@esempio.it"
pass_prodiere = "PasswordProdiere123!"

# --- 1. CREIAMO / ACCEDIAMO COME PRODIERE (per assicurarci che esista in 'profili') ---
try:
    res_prod = supabase.auth.sign_up({"email": email_prodiere, "password": pass_prodiere})
    if res_prod.user and res_prod.session:
        print("1. Nuovo account Prodiere registrato!")
    else:
        res_prod = supabase.auth.sign_in_with_password({"email": email_prodiere, "password": pass_prodiere})
        print("1. Prodiere già esistente, login effettuato.")
except Exception:
    res_prod = supabase.auth.sign_in_with_password({"email": email_prodiere, "password": pass_prodiere})
    print("1. Prodiere già esistente, login effettuato.")

# --- 2. L'ARMATORE FA LOGIN E CONDIVIDE LA BARCA ---
supabase.auth.sign_in_with_password({"email": email_armatore, "password": pass_armatore})
print("\n2. Armatore loggato.")

# Recuperiamo l'ID della barca 'Pequod' dell'armatore
barche_armatore = supabase.table("barche").select("id, nome_barca").execute()
pequod = barche_armatore.data[0]
print(f"   Trovata barca da condividere: {pequod['nome_barca']} (ID: {pequod['id']})")

# Cerchiamo l'UUID del prodiere partendo dalla sua email (come farà l'app!)
profilo_prodiere = supabase.table("profili").select("id").eq("email", email_prodiere).single().execute()
id_prodiere = profilo_prodiere.data["id"]
print(f"   Trovato ID del prodiere: {id_prodiere}")

# Inseriamo la condivisione (upsert evita errori se rilanci lo script due volte)
condivisione = {
    "barca_id": pequod["id"],
    "utente_id": id_prodiere,
    "permesso": "read"  # Prova anche 'write' in seguito!
}
supabase.table("condivisioni").upsert(condivisione, on_conflict="barca_id,utente_id").execute()
print("   -> Condivisione attivata con successo!")

# --- 3. IL PRODIERE FA LOGIN E CONTROLLA LE SUE BARCHE ---
supabase.auth.sign_out()
supabase.auth.sign_in_with_password({"email": email_prodiere, "password": pass_prodiere})
print("\n3. Prodiere loggato. Controllo quali barche può vedere...")

barche_visibili_prodiere = supabase.table("barche").select("nome_barca, numero_velico, owner_id").execute()
print("   Barche visibili al prodiere:", barche_visibili_prodiere.data)

# --- 4. TEST DI SICUREZZA: IL PRODIERE PROVA A MODIFICARE IN SOLA LETTURA ---
print("\n4. Test sicurezza: il prodiere prova a rinominare la barca avendo solo permesso 'read'...")
tentativo_modifica = supabase.table("barche").update({"nome_barca": "Barca Rubata"}).eq("id", pequod["id"]).execute()

if len(tentativo_modifica.data) == 0:
    print("   ✓ BLOCCATO! Il database ha impedito la modifica perché il permesso è solo 'read'.")
else:
    print("   Attenzione: modifica riuscita.")