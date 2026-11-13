import flet as ft
import db


def build_login_view(page: ft.Page, stato: dict, on_login_success):
    page.clean()
    email_field = ft.TextField(label="Email", value="armatore.meteor@esempio.it", width=350)
    pass_field = ft.TextField(
        label="Password (min. 6 caratteri)",
        value="PasswordSicura123!",
        password=True,
        can_reveal_password=True,
        width=350,
    )
    messaggio_text = ft.Text("", color=ft.Colors.RED_600, size=13)

    def compila_armatore(e):
        email_field.value = "armatore.meteor@esempio.it"
        pass_field.value = "PasswordSicura123!"
        messaggio_text.value = ""
        page.update()

    def compila_prodiere(e):
        email_field.value = "prodiere@esempio.it"
        pass_field.value = "PasswordProdiere123!"
        messaggio_text.value = ""
        page.update()

    def compila_tattico(e):
        email_field.value = "tattico@esempio.it"
        pass_field.value = "Tattico123!"
        messaggio_text.value = ""
        page.update()

    def esegui_login(e):
        if not email_field.value or not pass_field.value:
            messaggio_text.value = "Inserisci email e password."
            messaggio_text.color = ft.Colors.RED_600
            page.update()
            return
        try:
            user = db.login_utente(email_field.value, pass_field.value)
            stato["user"] = user
            stato["barca_selezionata_id"] = None
            on_login_success()
        except Exception as ex:
            messaggio_text.value = f"Errore di accesso: {ex}"
            messaggio_text.color = ft.Colors.RED_600
            page.update()

    def esegui_registrazione(e):
        if not email_field.value or not pass_field.value:
            messaggio_text.value = "Inserisci email e password per registrarti."
            messaggio_text.color = ft.Colors.RED_600
            page.update()
            return
        if len(pass_field.value) < 6:
            messaggio_text.value = "La password deve contenere almeno 6 caratteri."
            messaggio_text.color = ft.Colors.RED_600
            page.update()
            return
        try:
            user = db.registra_utente(email_field.value, pass_field.value)
            stato["user"] = user
            stato["barca_selezionata_id"] = None
            on_login_success()
        except Exception as ex:
            messaggio_text.value = f"Errore registrazione: {ex}"
            messaggio_text.color = ft.Colors.RED_600
            page.update()

    page.add(
        ft.Container(height=25),
        ft.Icon(ft.Icons.SAILING, size=64, color=ft.Colors.BLUE_700),
        ft.Text("TensApp", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
        ft.Text("Le regolazioni della tua barca, sempre a bordo.", color=ft.Colors.GREY_600),
        ft.Container(height=15),
        email_field,
        pass_field,
        messaggio_text,
        ft.Button(
            "Accedi",
            width=350,
            height=45,
            bgcolor=ft.Colors.BLUE_700,
            color=ft.Colors.WHITE,
            on_click=esegui_login,
        ),
        ft.OutlinedButton(
            "Crea nuovo account",
            icon=ft.Icons.PERSON_ADD,
            width=350,
            height=45,
            on_click=esegui_registrazione,
        ),
        ft.Divider(height=25),
        ft.Text("Account rapidi di test:", size=12, color=ft.Colors.GREY_600),
        ft.Row(
            [
                ft.OutlinedButton("Armatore", on_click=compila_armatore),
                ft.OutlinedButton("Prodiere", on_click=compila_prodiere),
                ft.OutlinedButton("Tattico", on_click=compila_tattico),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
    )
    page.update()