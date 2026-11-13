import flet as ft
import db


def build_nuova_barca_view(page: ft.Page, stato: dict, on_back):
    page.clean()
    try:
        templates = db.get_templates()

        header = ft.Row(
            [
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    tooltip="Torna indietro",
                    on_click=lambda _: on_back(),
                ),
                ft.Text("Nuova Barca", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                ft.Container(width=40),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        if not templates:
            page.add(header, ft.Text("Nessun template di classe disponibile sul database."))
            page.update()
            return

        opzioni_classi = [ft.dropdown.Option(key=t["id"], text=t["nome_classe"]) for t in templates]

        dropdown_classe = ft.Dropdown(
            label="Classe Velica (Template)",
            value=templates[0]["id"],
            options=opzioni_classi,
            width=370,
        )
        nome_field = ft.TextField(label="Nome Barca (es. Albatros)", width=370)
        vela_field = ft.TextField(label="Numero Velico (es. ITA 510)", width=370)
        errore_text = ft.Text("", color=ft.Colors.RED_600, size=13)

        def salva_nuova_barca(e):
            if not nome_field.value or not nome_field.value.strip():
                errore_text.value = "Inserisci il nome della barca."
                page.update()
                return

            template_scelto = next(t for t in templates if t["id"] == dropdown_classe.value)
            nuova = db.crea_nuova_barca(
                owner_id=stato["user"].id,
                template=template_scelto,
                nome_barca=nome_field.value,
                numero_velico=vela_field.value,
            )
            stato["barca_selezionata_id"] = nuova["id"]
            on_back()

        page.add(
            header,
            ft.Divider(),
            ft.Text(
                "Scegli una classe per precompilare automaticamente misure e tensioni base:",
                size=13,
                color=ft.Colors.GREY_700,
            ),
            ft.Container(height=10),
            dropdown_classe,
            nome_field,
            vela_field,
            errore_text,
            ft.Container(height=10),
            ft.Button(
                "Crea Scheda Barca",
                icon=ft.Icons.ADD,
                bgcolor=ft.Colors.BLUE_700,
                color=ft.Colors.WHITE,
                width=370,
                height=45,
                on_click=salva_nuova_barca,
            ),
        )
    except Exception as err:
        page.add(ft.Text(f"Errore: {err}", color=ft.Colors.RED_600))

    page.update()