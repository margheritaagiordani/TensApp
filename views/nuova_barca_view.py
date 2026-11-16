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

        def is_template_default():
            t = next((x for x in templates if x["id"] == dropdown_classe.value), None)
            return not bool(t and t.get("dati_template", {}).get("specifiche_fisse"))

        # Dati identificativi
        nome_field = ft.TextField(label="Nome Barca *", width=370)
        modello_field = ft.TextField(label="Modello Barca (es. J/24, First 31.7) *", width=370)
        vela_field = ft.TextField(label="Numero Velico (es. ITA 510)", width=370)

        # Cantiere, anno e pesi
        cantiere_field = ft.TextField(label="Cantiere", width=220)
        anno_field = ft.TextField(label="Anno costruzione", width=140, keyboard_type=ft.KeyboardType.NUMBER)
        peso_field = ft.TextField(label="Peso (kg)", width=180, keyboard_type=ft.KeyboardType.TEXT)
        peso_chiglia_field = ft.TextField(label="Peso in chiglia (kg)", width=180, keyboard_type=ft.KeyboardType.TEXT)
        correttori_field = ft.TextField(label="Correttori di stazza", width=370)

        # Misure in millimetri (per barca di default)
        lft_field = ft.TextField(label="Lunghezza LFT (mm)", width=180, keyboard_type=ft.KeyboardType.TEXT)
        beam_field = ft.TextField(label="Larghezza Beam (mm)", width=180, keyboard_type=ft.KeyboardType.TEXT)
        pescaggio_field = ft.TextField(label="Pescaggio (mm)", width=180, keyboard_type=ft.KeyboardType.TEXT)
        max_p_field = ft.TextField(label="Max P (mm)", width=180, keyboard_type=ft.KeyboardType.TEXT)

        sezione_misure_mm = ft.Column(
            [
                ft.Row([lft_field, beam_field], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([pescaggio_field, max_p_field], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ],
            visible=is_template_default(),
        )
        modello_field.visible = is_template_default()
        peso_chiglia_field.visible = is_template_default()
        peso_field.value = "" if is_template_default() else "770"

        def on_cambia_classe(e):
            is_custom = is_template_default()
            modello_field.visible = is_custom
            peso_chiglia_field.visible = is_custom
            sezione_misure_mm.visible = is_custom
            peso_field.value = "" if is_custom else "770"
            page.update()

        dropdown_classe.on_select = on_cambia_classe

        errore_text = ft.Text("", color=ft.Colors.RED_600, size=13)

        def parse_float(val):
            if not val or not val.strip():
                return None
            try:
                return float(val.strip().replace(",", "."))
            except ValueError:
                return None

        def parse_int(val):
            if not val or not val.strip():
                return None
            try:
                return int(float(val.strip().replace(",", ".")))
            except ValueError:
                return None

        def salva_nuova_barca(e):
            is_custom = is_template_default()

            if not nome_field.value or not nome_field.value.strip():
                errore_text.value = "Inserisci il nome della barca."
                page.update()
                return

            if is_custom and (not modello_field.value or not modello_field.value.strip()):
                errore_text.value = "Inserisci il modello della barca."
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
                if is_custom:
                    dati_reg["dati_barca"]["modello_barca"] = modello_field.value.strip()
                    dati_reg["dati_barca"]["peso_kg"] = parse_float(peso_field.value)
                    dati_reg["dati_barca"]["peso_chiglia_kg"] = parse_float(peso_chiglia_field.value)
                    dati_reg["dati_barca"]["correttori_stazza"] = correttori_field.value.strip()
                    dati_reg["dati_barca"]["lunghezza_lft_mm"] = parse_int(lft_field.value)
                    dati_reg["dati_barca"]["larghezza_beam_mm"] = parse_int(beam_field.value)
                    dati_reg["dati_barca"]["pescaggio_mm"] = parse_int(pescaggio_field.value)
                    dati_reg["dati_barca"]["max_p_mm"] = parse_int(max_p_field.value)
                else:
                    dati_reg["dati_barca"]["peso_reale_kg"] = parse_float(peso_field.value)
                    dati_reg["dati_barca"]["correttori_kg"] = correttori_field.value.strip()

                dati_reg["dati_barca"]["cantiere"] = cantiere_field.value.strip()
                dati_reg["dati_barca"]["anno_costruzione"] = parse_int(anno_field.value)

                db.aggiorna_regolazioni(nuova["id"], dati_reg)

            stato["barca_selezionata_id"] = nuova["id"]
            on_back()

        page.add(
            header,
            ft.Divider(),
            ft.Text("Dati Identificativi", weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
            dropdown_classe,
            nome_field,
            modello_field,
            vela_field,
            ft.Divider(height=15),
            ft.Text("Scafo, Pesi & Dimensioni (mm)", weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
            ft.Row([cantiere_field, anno_field], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([peso_field, peso_chiglia_field], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            sezione_misure_mm,
            correttori_field,
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