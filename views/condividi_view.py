import flet as ft
import db


def build_condividi_view(page: ft.Page, barca: dict, on_back):
    page.clean()

    header = ft.Row(
        [
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                tooltip="Torna alla barca",
                on_click=lambda _: on_back(),
            ),
            ft.Text("Condividi Barca", size=21, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
            ft.Container(width=40),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    email_field = ft.TextField(label="Email utente da invitare", width=370)
    permesso_dropdown = ft.Dropdown(
        label="Livello di accesso",
        value="read",
        options=[
            ft.dropdown.Option(key="read", text="Sola lettura (Equipaggio)"),
            ft.dropdown.Option(key="write", text="Modifica (Rigger / Tattico)"),
        ],
        width=370,
    )
    feedback_text = ft.Text("", size=13)
    lista_condivisioni_col = ft.Column(spacing=8)

    def aggiorna_lista():
        lista_condivisioni_col.controls.clear()
        condivisioni = db.get_condivisioni_barca(barca["id"])
        if not condivisioni:
            lista_condivisioni_col.controls.append(
                ft.Text("Nessuna condivisione attiva per questa barca.", italic=True, color=ft.Colors.GREY_600, size=13)
            )
        else:
            for c in condivisioni:
                ruolo_label = "Modifica" if c["permesso"] == "write" else "Sola lettura"
                riga = ft.Container(
                    content=ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text(c["email"], weight=ft.FontWeight.BOLD, size=13),
                                    ft.Text(f"Permesso: {ruolo_label}", size=12, color=ft.Colors.GREY_700),
                                ],
                                spacing=2,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                icon_color=ft.Colors.RED_600,
                                tooltip="Revoca accesso",
                                on_click=lambda e, cid=c["id"]: revoca(cid),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=10,
                    border=ft.Border.all(1, ft.Colors.GREY_300),
                    border_radius=8,
                )
                lista_condivisioni_col.controls.append(riga)
        page.update()

    def invia_invito(e):
        if not email_field.value or not email_field.value.strip():
            feedback_text.value = "Inserisci un'email valida."
            feedback_text.color = ft.Colors.RED_600
            page.update()
            return
        try:
            db.condividi_barca_con_email(barca["id"], email_field.value, permesso_dropdown.value)
            feedback_text.value = f"✓ Accesso aggiornato per {email_field.value.strip()}!"
            feedback_text.color = ft.Colors.GREEN_700
            email_field.value = ""
            aggiorna_lista()
        except Exception as err:
            feedback_text.value = str(err)
            feedback_text.color = ft.Colors.RED_600
            page.update()

    def revoca(condivisione_id: str):
        db.rimuovi_condivisione(condivisione_id)
        feedback_text.value = "Accesso revocato."
        feedback_text.color = ft.Colors.GREY_700
        aggiorna_lista()

    page.add(
        header,
        ft.Divider(),
        ft.Text(f"Barca: {barca['nome_barca']} ({barca['numero_velico']})", weight=ft.FontWeight.W_600, size=15),
        ft.Container(height=5),
        email_field,
        permesso_dropdown,
        ft.Button(
            "Concedi / Aggiorna Accesso",
            icon=ft.Icons.PERSON_ADD,
            bgcolor=ft.Colors.BLUE_700,
            color=ft.Colors.WHITE,
            width=370,
            height=45,
            on_click=invia_invito,
        ),
        feedback_text,
        ft.Divider(height=25),
        ft.Text("Utenti con accesso:", weight=ft.FontWeight.BOLD, size=16),
        lista_condivisioni_col,
    )
    aggiorna_lista()