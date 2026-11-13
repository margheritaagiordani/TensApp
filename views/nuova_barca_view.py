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
        nome_field = ft.TextField(label="Nome Barca (es. Albatros) *", width=370)
        vela_field = ft.TextField(label="Numero Velico (es. ITA 510)", width=370)

        # Campi specifici dello scafo dell'armatore
        cantiere_field = ft.TextField(label="Cantiere (es. Sipla, Nautica Lario)", width=370)
        anno_field = ft.TextField(label="Anno costruzione", width=180, keyboard_type=ft.KeyboardType.NUMBER)
        peso_field = ft.TextField(label="Peso reale (kg)", value="770", width=180, keyboard_type=ft.KeyboardType.NUMBER)
        correttori_field = ft.TextField(label="Correttori di stazza (es. 6kg prua)", width=370)
        albero_field = ft.TextField(label="Modello / Profilo Albero (es. Sparcraft)", width=370)
        tensiometro_field = ft.TextField(label="Scala Tensiometro", value="Loos PT-1", width=370)

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

            # Aggiorniamo subito i dati_barca personalizzati se il template li prevede
            dati_reg = nuova["dati_regolazioni"]
            if "dati_barca" in dati_reg:
                dati_reg["dati_barca"]["cantiere"] = cantiere_field.value.strip()
                dati_reg["dati_barca"]["anno_costruzione"] = int(anno_field.value) if anno_field.value.strip().isdigit() else None
                try:
                    dati_reg["dati_barca"]["peso_reale_kg"] = float(peso_field.value.replace(",", ".")) if peso_field.value else 770
                except ValueError:
                    dati_reg["dati_barca"]["peso_reale_kg"] = 770
                dati_reg["dati_barca"]["correttori_kg"] = correttori_field.value.strip()
                dati_reg["dati_barca"]["modello_albero"] = albero_field.value.strip()
                dati_reg["dati_barca"]["scala_tensiometro"] = tensiometro_field.value.strip() or "Loos PT-1"
                db.aggiorna_regolazioni(nuova["id"], dati_reg)

            stato["barca_selezionata_id"] = nuova["id"]
            on_back()

        page.add(
            header,
            ft.Divider(),
            ft.Text("Dati Identificativi & Classe", weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
            dropdown_classe,
            nome_field,
            vela_field,
            ft.Divider(height=15),
            ft.Text("Specifiche Scafo & Attrezzatura", weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
            cantiere_field,
            ft.Row([anno_field, peso_field], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            correttori_field,
            albero_field,
            tensiometro_field,
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