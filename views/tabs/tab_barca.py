import flet as ft
import db


def build_tab_barca(page: ft.Page, barca: dict, puo_modificare: bool):
    is_custom = barca["classe_id"] == "custom"
    dati = barca["dati_regolazioni"]
    specs = dati.get("specifiche_fisse", {})
    dati_barca = dati.get("dati_barca", {})
    assetto = dati.get("assetto_banchina", dati.get("assetto_base_banchina", {}))

    msg_barca = ft.Text("", color=ft.Colors.GREEN_700, weight=ft.FontWeight.BOLD)

    if is_custom:
        # ==================================================================
        # CASO 1: BARCA DI DEFAULT / PERSONALIZZATA ('custom') - NESSUN DATO FISSO
        # ==================================================================
        f_modello = ft.TextField(label="Modello Barca", value=str(dati_barca.get("modello_barca", "")), width=370, dense=True, read_only=not puo_modificare)
        f_cantiere = ft.TextField(label="Cantiere", value=str(dati_barca.get("cantiere", "")), width=220, dense=True, read_only=not puo_modificare)
        f_anno = ft.TextField(label="Anno", value=str(dati_barca.get("anno_costruzione") or ""), width=140, dense=True, keyboard_type=ft.KeyboardType.NUMBER, read_only=not puo_modificare)
        f_peso = ft.TextField(label="Peso (kg)", value=str(dati_barca.get("peso_kg") or ""), width=180, dense=True, keyboard_type=ft.KeyboardType.NUMBER, read_only=not puo_modificare)
        f_peso_chiglia = ft.TextField(label="Peso in chiglia (kg)", value=str(dati_barca.get("peso_chiglia_kg") or ""), width=180, dense=True, keyboard_type=ft.KeyboardType.NUMBER, read_only=not puo_modificare)
        f_lft = ft.TextField(label="Lunghezza LFT (mm)", value=str(dati_barca.get("lunghezza_lft_mm") or ""), width=180, dense=True, keyboard_type=ft.KeyboardType.NUMBER, read_only=not puo_modificare)
        f_beam = ft.TextField(label="Larghezza Beam (mm)", value=str(dati_barca.get("larghezza_beam_mm") or ""), width=180, dense=True, keyboard_type=ft.KeyboardType.NUMBER, read_only=not puo_modificare)
        f_pescaggio = ft.TextField(label="Pescaggio (mm)", value=str(dati_barca.get("pescaggio_mm") or ""), width=180, dense=True, keyboard_type=ft.KeyboardType.NUMBER, read_only=not puo_modificare)
        f_max_p = ft.TextField(label="Max P (mm)", value=str(dati_barca.get("max_p_mm") or ""), width=180, dense=True, keyboard_type=ft.KeyboardType.NUMBER, read_only=not puo_modificare)
        f_correttori = ft.TextField(label="Correttori di stazza", value=str(dati_barca.get("correttori_stazza", "")), width=370, dense=True, read_only=not puo_modificare)

        def salva_custom(e):
            dati["dati_barca"] = {
                "modello_barca": f_modello.value.strip(),
                "cantiere": f_cantiere.value.strip(),
                "anno_costruzione": int(f_anno.value) if f_anno.value.strip().isdigit() else None,
                "peso_kg": float(f_peso.value.replace(",", ".")) if f_peso.value.strip() else None,
                "peso_chiglia_kg": float(f_peso_chiglia.value.replace(",", ".")) if f_peso_chiglia.value.strip() else None,
                "lunghezza_lft_mm": int(float(f_lft.value.replace(",", "."))) if f_lft.value.strip() else None,
                "larghezza_beam_mm": int(float(f_beam.value.replace(",", "."))) if f_beam.value.strip() else None,
                "pescaggio_mm": int(float(f_pescaggio.value.replace(",", "."))) if f_pescaggio.value.strip() else None,
                "max_p_mm": int(float(f_max_p.value.replace(",", "."))) if f_max_p.value.strip() else None,
                "correttori_stazza": f_correttori.value.strip(),
            }
            db.aggiorna_regolazioni(barca["id"], dati)
            msg_barca.value = "✓ Dati barca salvati!"
            page.update()

        page.add(
            ft.Text("Dati & Dimensioni Barca (mm)", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
            f_modello,
            ft.Row([f_cantiere, f_anno], spacing=10),
            ft.Row([f_peso, f_peso_chiglia], spacing=10),
            ft.Row([f_lft, f_beam], spacing=10),
            ft.Row([f_pescaggio, f_max_p], spacing=10),
            f_correttori,
        )
        if puo_modificare:
            page.add(
                ft.Button("Salva Dati Barca", icon=ft.Icons.SAVE, bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE, width=370, on_click=salva_custom),
                msg_barca,
            )

    else:
        # ==================================================================
        # CASO 2: CLASSE MONOTIPO CON TEMPLATE (es. METEOR)
        # ==================================================================
        peso_min = specs.get("dislocamento_minimo_kg", specs.get("dislocamento_kg", 770))
        page.add(
            ft.Text("Specifiche Fisse di Classe", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            f"LFT: {specs.get('lunghezza_ft_m', '-')}m  •  Larghezza: {specs.get('larghezza_max_m', '-')}m  •  Pescaggio: {specs.get('pescaggio_m', '-')}m",
                            size=12,
                        ),
                        ft.Text(
                            f"Peso min: {peso_min}kg  •  Randa: {specs.get('superficie_randa_mq', '-')}mq  •  Genoa: {specs.get('superficie_genoa_mq', '-')}mq  •  Fiocco: {specs.get('superficie_fiocco_mq', '-')}mq  •  Spi: {specs.get('superficie_spi_mq', '-')}mq",
                            size=12,
                        ),
                    ],
                    spacing=4,
                ),
                padding=10,
                bgcolor=ft.Colors.GREY_100,
                border_radius=8,
            ),
            ft.Text("Dati Specifici Scafo (Modificabili)", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
        )

        f_cantiere = ft.TextField(label="Cantiere", value=str(dati_barca.get("cantiere", "")), width=180, dense=True, read_only=not puo_modificare)
        f_anno = ft.TextField(label="Anno", value=str(dati_barca.get("anno_costruzione") or ""), width=180, dense=True, keyboard_type=ft.KeyboardType.NUMBER, read_only=not puo_modificare)
        f_peso = ft.TextField(label="Peso reale (kg)", value=str(dati_barca.get("peso_reale_kg", peso_min)), width=180, dense=True, keyboard_type=ft.KeyboardType.NUMBER, read_only=not puo_modificare)
        f_correttori = ft.TextField(label="Correttori (kg)", value=str(dati_barca.get("correttori_kg", "")), width=180, dense=True, read_only=not puo_modificare)
        f_albero = ft.TextField(label="Modello Albero", value=str(dati_barca.get("modello_albero", "")), width=180, dense=True, read_only=not puo_modificare)
        f_tensiometro = ft.TextField(label="Scala Tensiometro", value=str(dati_barca.get("scala_tensiometro", "Loos PT-1")), width=180, dense=True, read_only=not puo_modificare)

        f_strallo = ft.TextField(label="Lunghezza Strallo (mm)", value=str(assetto.get("lunghezza_strallo_mm", "")), width=118, dense=True, keyboard_type=ft.KeyboardType.NUMBER, read_only=not puo_modificare)
        f_rake = ft.TextField(label="Rake (mm)", value=str(assetto.get("rake_testa_albero_mm", "")), width=118, dense=True, keyboard_type=ft.KeyboardType.NUMBER, read_only=not puo_modificare)
        f_prebend = ft.TextField(label="Pre-bend (mm)", value=str(assetto.get("pre_bend_mm", "")), width=118, dense=True, keyboard_type=ft.KeyboardType.NUMBER, read_only=not puo_modificare)

        def salva_monotipo(e):
            dati["dati_barca"] = {
                "cantiere": f_cantiere.value.strip(),
                "anno_costruzione": int(f_anno.value) if f_anno.value.strip().isdigit() else None,
                "peso_reale_kg": float(f_peso.value.replace(",", ".")) if f_peso.value else peso_min,
                "correttori_kg": f_correttori.value.strip(),
                "modello_albero": f_albero.value.strip(),
                "scala_tensiometro": f_tensiometro.value.strip(),
            }
            dati["assetto_banchina"] = {
                "lunghezza_strallo_mm": int(f_strallo.value) if f_strallo.value.strip().isdigit() else None,
                "rake_testa_albero_mm": int(f_rake.value) if f_rake.value.strip().isdigit() else None,
                "pre_bend_mm": int(f_prebend.value) if f_prebend.value.strip().isdigit() else None,
            }
            db.aggiorna_regolazioni(barca["id"], dati)
            msg_barca.value = "✓ Dati barca salvati!"
            page.update()

        page.add(
            ft.Row([f_cantiere, f_anno], spacing=12, alignment=ft.MainAxisAlignment.START),
            ft.Row([f_peso, f_correttori], spacing=12, alignment=ft.MainAxisAlignment.START),
            ft.Row([f_albero, f_tensiometro], spacing=12, alignment=ft.MainAxisAlignment.START),
            ft.Text("Assetto Base Banchina", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
            ft.Row([f_strallo, f_rake, f_prebend], spacing=12, alignment=ft.MainAxisAlignment.START),
        )
        if puo_modificare:
            page.add(
                ft.Button("Salva Dati Barca", icon=ft.Icons.SAVE, bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE, width=370, on_click=salva_monotipo),
                msg_barca,
            )