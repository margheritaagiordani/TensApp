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

        # Campi extra visibili SOLO se l'utente sceglie il modello 'custom'
        classe_custom_field = ft.TextField(label="Nome Classe / Modello (es. J/24, First 31.7) *", width=370)
        lft_field = ft.TextField(label="Lunghezza LFT (m)", width=115, keyboard_type=ft.KeyboardType.NUMBER)
        larghezza_field = ft.TextField(label="Larghezza (m)", width=115, keyboard_type=ft.KeyboardType.NUMBER)
        pescaggio_field = ft.TextField(label="Pescaggio (m)", width=115, keyboard_type=ft.KeyboardType.NUMBER)

        contenitore_custom = ft.Column(
            [
                classe_custom_field,
                ft.Row([lft_field, larghezza_field, pescaggio_field], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ],
            visible=(dropdown_classe.value == "custom"),
        )

        def on_cambia_classe(e):
            is_custom = dropdown_classe.value == "custom"
            contenitore_custom.visible = is_custom
            peso_field.value = "" if is_custom else "770"
            page.update()

        dropdown_classe.on_select = on_cambia_classe

        # Campi specifici dello scafo dell'armatore (comuni a tutte le barche)
        cantiere_field = ft.TextField(label="Cantiere (es. Sipla, Beneteau)", width=370)
        anno_field = ft.TextField(label="Anno costruzione", width=180, keyboard_type=ft.KeyboardType.NUMBER)
        peso_field = ft.TextField(
            label="Peso reale / Dislocamento (kg)",
            value="" if dropdown_classe.value == "custom" else "770",
            width=180,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        correttori_field = ft.TextField(label="Correttori di stazza (es. 6kg prua)", width=370)
        albero_field = ft.TextField(label="Modello / Profilo Albero (es. Sparcraft)", width=370)
        tensiometro_field = ft.TextField(label="Scala Tensiometro", value="Loos PT-1", width=370)

        errore_text = ft.Text("", color=ft.Colors.RED_600, size=13)

        def parse_float(val):
            if not val or not val.strip():
                return None
            try:
                return float(val.strip().replace(",", "."))
            except ValueError:
                return None

        def salva_nuova_barca(e):
            if not nome_field.value or not nome_field.value.strip():
                errore_text.value = "Inserisci il nome della barca."
                page.update()
                return

            if dropdown_classe.value == "custom" and (not classe_custom_field.value or not classe_custom_field.value.strip()):
                errore_text.value = "Inserisci il nome della classe o modello della barca."
                page.update()
                return

            template_scelto = next(t for t in templates if t["id"] == dropdown_classe.value)
            nuova = db.crea_nuova_barca(
                owner_id=stato["user"].id,
                template=template_scelto,
                nome_barca=nome_field.value,
                numero_velico=vela_field.value,
            )

            dati_reg = nuova["dati_regolazioni"]
            if "dati_barca" in dati_reg:
                if dropdown_classe.value == "custom":
                    dati_reg["dati_barca"]["classe_personalizzata"] = classe_custom_field.value.strip()
                    dati_reg["dati_barca"]["lunghezza_ft_m"] = parse_float(lft_field.value)
                    dati_reg["dati_barca"]["larghezza_max_m"] = parse_float(larghezza_field.value)
                    dati_reg["dati_barca"]["pescaggio_m"] = parse_float(pescaggio_field.value)

                dati_reg["dati_barca"]["cantiere"] = cantiere_field.value.strip()
                dati_reg["dati_barca"]["anno_costruzione"] = int(anno_field.value) if anno_field.value.strip().isdigit() else None
                dati_reg["dati_barca"]["peso_reale_kg"] = parse_float(peso_field.value)
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
            contenitore_custom,
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