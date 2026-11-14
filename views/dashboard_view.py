from datetime import date
import flet as ft
import db


def build_dashboard_view(page: ft.Page, stato: dict, on_logout, on_open_nuova_barca, on_open_condividi):
    page.clean()
    try:
        user_id = stato["user"].id

        # 1. Scarichiamo barche e permessi
        barche, permessi = db.get_barche_e_permessi(user_id)
        stato["barche"] = barche
        stato["permessi_condivisi"] = permessi

        # Tab attiva di default
        if "tab_attiva" not in stato:
            stato["tab_attiva"] = "barca"

        header = ft.Row(
            [
                ft.Text("Flotta & Regolazioni", size=21, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                ft.Row(
                    [
                        ft.IconButton(
                            icon=ft.Icons.ADD_CIRCLE,
                            icon_color=ft.Colors.BLUE_700,
                            tooltip="Aggiungi nuova barca",
                            on_click=lambda _: on_open_nuova_barca(),
                        ),
                        ft.IconButton(
                            icon=ft.Icons.LOGOUT,
                            tooltip="Esci",
                            on_click=lambda _: on_logout(),
                        ),
                    ],
                    spacing=0,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        page.add(header)

        if not stato["barche"]:
            page.add(
                ft.Container(height=20),
                ft.Text("Nessuna barca trovata nel tuo profilo."),
                ft.Button(
                    "Aggiungi la tua prima barca",
                    icon=ft.Icons.ADD,
                    on_click=lambda _: on_open_nuova_barca(),
                ),
            )
            page.update()
            return

        ids_disponibili = [b["id"] for b in stato["barche"]]
        if stato["barca_selezionata_id"] not in ids_disponibili:
            stato["barca_selezionata_id"] = ids_disponibili[0]

        opzioni_dropdown = []
        for b in stato["barche"]:
            is_owner = b["owner_id"] == user_id
            etichetta_ruolo = "Mia" if is_owner else "Condivisa"
            num_velico = f" ({b['numero_velico']})" if b.get("numero_velico") else ""
            opzioni_dropdown.append(
                ft.dropdown.Option(
                    key=b["id"],
                    text=f"{b['nome_barca']}{num_velico} • {etichetta_ruolo}",
                )
            )

        def cambia_barca(e):
            stato["barca_selezionata_id"] = dropdown_barche.value
            build_dashboard_view(page, stato, on_logout, on_open_nuova_barca, on_open_condividi)

        dropdown_barche = ft.Dropdown(
            label="Seleziona Barca",
            value=stato["barca_selezionata_id"],
            options=opzioni_dropdown,
            width=370,
            on_select=cambia_barca,
        )
        page.add(dropdown_barche)

        # Recuperiamo la barca attiva e i permessi
        barca = next(b for b in stato["barche"] if b["id"] == stato["barca_selezionata_id"])
        is_owner = barca["owner_id"] == user_id
        permesso = "owner" if is_owner else stato["permessi_condivisi"].get(barca["id"], "read")
        puo_modificare = permesso in ("owner", "write")

        if permesso == "owner":
            badge_testo, badge_colore = "Proprietario", ft.Colors.BLUE_700
        elif permesso == "write":
            badge_testo, badge_colore = "Condivisa (Modifica)", ft.Colors.ORANGE_700
        else:
            badge_testo, badge_colore = "Condivisa (Sola lettura)", ft.Colors.GREY_700

        dati = barca["dati_regolazioni"]
        specs = dati.get("specifiche_fisse", {})
        dati_barca = dati.get("dati_barca", {})
        assetto = dati.get("assetto_banchina", dati.get("assetto_base_banchina", {}))

        # Intestazione Barca + Pulsante Condividi (solo per owner)
        azioni_barca = [
            ft.Container(
                content=ft.Text(badge_testo, size=10, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                bgcolor=badge_colore,
                padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                border_radius=8,
            )
        ]
        if is_owner:
            azioni_barca.append(
                ft.IconButton(
                    icon=ft.Icons.SHARE,
                    icon_color=ft.Colors.BLUE_800,
                    tooltip="Condividi barca",
                    on_click=lambda _: on_open_condividi(barca),
                )
            )

        card_info = ft.Container(
            content=ft.Row(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.SAILING, color=ft.Colors.BLUE_700, size=28),
                            ft.Column(
                                [
                                    ft.Text(barca["nome_barca"], size=18, weight=ft.FontWeight.BOLD),
                                    ft.Text(
                                        f"{barca['classe_id'].upper()} | {barca.get('numero_velico', '')}",
                                        size=12,
                                        color=ft.Colors.GREY_700,
                                    ),
                                ],
                                spacing=1,
                            ),
                        ]
                    ),
                    ft.Row(azioni_barca, spacing=2),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=12,
            bgcolor=ft.Colors.BLUE_50,
            border_radius=12,
        )
        page.add(card_info)

        # Barra di navigazione tra le 4 sezioni
        def seleziona_tab(nome_tab: str):
            stato["tab_attiva"] = nome_tab
            build_dashboard_view(page, stato, on_logout, on_open_nuova_barca, on_open_condividi)

        def crea_bottone_tab(id_tab: str, etichetta: str):
            attivo = stato["tab_attiva"] == id_tab
            return ft.Container(
                content=ft.Text(
                    etichetta,
                    size=12,
                    weight=ft.FontWeight.BOLD if attivo else ft.FontWeight.NORMAL,
                    color=ft.Colors.WHITE if attivo else ft.Colors.BLUE_900,
                ),
                bgcolor=ft.Colors.BLUE_700 if attivo else ft.Colors.BLUE_50,
                padding=ft.Padding.symmetric(horizontal=10, vertical=8),
                border_radius=8,
                on_click=lambda _: seleziona_tab(id_tab),
            )

        barra_tab = ft.Row(
            [
                crea_bottone_tab("barca", "Barca"),
                crea_bottone_tab("baseline", "Baseline"),
                crea_bottone_tab("vele", "Vele"),
                crea_bottone_tab("log", "Diario Uscite"),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        page.add(barra_tab, ft.Divider(height=10))

        # ======================================================================
        # TAB 1: DATI BARCA, SPECIFICHE CLASSE E ASSETTO BANCHINA
        # ======================================================================
        if stato["tab_attiva"] == "barca":
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

            msg_barca = ft.Text("", color=ft.Colors.GREEN_700, weight=ft.FontWeight.BOLD) #quando salvi barca ti viene fuori "barca salvata"

            def salva_dati_scafo(e):
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
                msg_barca.value = "✓ Dati scafo e banchina salvati!"
                page.update()

            page.add(
                ft.Row([f_cantiere, f_anno], spacing=12, alignment=ft.MainAxisAlignment.START),
                ft.Row([f_peso, f_correttori], spacing=12, alignment=ft.MainAxisAlignment.START),
                ft.Row([f_albero, f_tensiometro], spacing=12, alignment=ft.MainAxisAlignment.START),
                ft.Text("Assetto Base Banchina", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
                ft.Row([f_strallo, f_rake, f_prebend], spacing=12, alignment=ft.MainAxisAlignment.START)
            )
            if puo_modificare:
                page.add(
                    ft.Button("Salva Dati Barca", icon=ft.Icons.SAVE, bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE, width=370, on_click=salva_dati_scafo),
                    msg_barca,
                )

        # ======================================================================
        # TAB 2: TENSIONI BASELINE (MULTIPLI ASSETTI DI RIFERIMENTO)
        # ======================================================================
        elif stato["tab_attiva"] == "baseline":
            baselines = db.get_baseline_barca(barca["id"])
            scala = dati_barca.get("scala_tensiometro", "Loos PT-1")
            page.add(ft.Text(f"Baseline di Riferimento ({scala})", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800))

            if not baselines:
                page.add(ft.Text("Nessuna baseline registrata per questa barca.", size=12, italic=True, color=ft.Colors.GREY_600))

            for bl in baselines:
                def rimuovi_bl(e, bl_id=bl["id"]):
                    db.elimina_baseline(bl_id)
                    build_dashboard_view(page, stato, on_logout, on_open_nuova_barca, on_open_condividi)

                riga_top = [
                    ft.Column(
                        [
                            ft.Text(bl["nome_baseline"], weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.BLUE_900),
                            ft.Text(
                                f"Vento: {bl['condizioni_vento']}  •  Equipaggio: {bl.get('peso_equipaggio') or '-'}",
                                size=12,
                                color=ft.Colors.GREY_800,
                            ),
                        ],
                        spacing=2,
                    )
                ]
                if puo_modificare:
                    riga_top.append(ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color=ft.Colors.RED_600, icon_size=20, on_click=rimuovi_bl))

                dettagli_bl = [
                    ft.Row(riga_top, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Text(f"Alte (V1): {bl.get('tensione_alte') if bl.get('tensione_alte') is not None else '-'}", weight=ft.FontWeight.BOLD, size=12),
                                ft.Text(f"Basse (D1): {bl.get('tensione_basse') if bl.get('tensione_basse') is not None else '-'}", weight=ft.FontWeight.BOLD, size=12),
                                ft.Text(f"Strallo: {bl.get('tensione_strallo') if bl.get('tensione_strallo') is not None else '-'}", weight=ft.FontWeight.BOLD, size=12),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        bgcolor=ft.Colors.BLUE_50,
                        padding=8,
                        border_radius=6,
                    ),
                ]
                if bl.get("primo_utilizzo"):
                    dettagli_bl.append(ft.Text(f"Primo utilizzo: {bl['primo_utilizzo']}", size=11, color=ft.Colors.GREY_600))
                if bl.get("commenti"):
                    dettagli_bl.append(ft.Text(f"Note: {bl['commenti']}", size=12, italic=True))

                page.add(
                    ft.Container(
                        content=ft.Column(dettagli_bl, spacing=6),
                        padding=10,
                        border=ft.Border.all(1, ft.Colors.GREY_300),
                        border_radius=10,
                    )
                )

            if puo_modificare:
                page.add(ft.Divider(height=15), ft.Text("+ Aggiungi Nuova Baseline", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800))
                b_nome = ft.TextField(label="Nome Baseline (es. Lago Vento Medio) *", width=370, dense=True)
                b_vento = ft.TextField(label="Condizioni Vento (es. 8-12 kn) *", width=180, dense=True)
                b_eq = ft.Dropdown(
                    label="Peso Equipaggio",
                    value="Medio",
                    options=[
                        ft.dropdown.Option(key="Leggero", text="Leggero"),
                        ft.dropdown.Option(key="Medio", text="Medio"),
                        ft.dropdown.Option(key="Pesante", text="Pesante"),
                    ],
                    width=180,
                )
                b_alte = ft.TextField(label="Alte (V1)", width=118, dense=True, keyboard_type=ft.KeyboardType.NUMBER)
                b_basse = ft.TextField(label="Basse (D1)", width=118, dense=True, keyboard_type=ft.KeyboardType.NUMBER)
                b_strallo = ft.TextField(label="Strallo", width=118, dense=True, keyboard_type=ft.KeyboardType.NUMBER)
                b_primo_uso = ft.TextField(label="Primo utilizzo (AAAA-MM-GG)", value=str(date.today()), width=370, dense=True)
                b_commenti = ft.TextField(label="Commenti", width=370, dense=True, multiline=True)
                b_err = ft.Text("", color=ft.Colors.RED_600, size=12)

                def parse_num(val):
                    try:
                        return float(val.replace(",", ".")) if val and val.strip() else None
                    except ValueError:
                        return None

                def salva_nuova_bl(e):
                    if not b_nome.value.strip() or not b_vento.value.strip():
                        b_err.value = "Nome baseline e condizioni vento sono obbligatori."
                        page.update()
                        return
                    db.aggiungi_baseline(
                        barca["id"],
                        {
                            "nome_baseline": b_nome.value.strip(),
                            "condizioni_vento": b_vento.value.strip(),
                            "peso_equipaggio": b_eq.value,
                            "tensione_alte": parse_num(b_alte.value),
                            "tensione_basse": parse_num(b_basse.value),
                            "tensione_strallo": parse_num(b_strallo.value),
                            "primo_utilizzo": b_primo_uso.value.strip() or None,
                            "commenti": b_commenti.value.strip() or None,
                        },
                    )
                    build_dashboard_view(page, stato, on_logout, on_open_nuova_barca, on_open_condividi)

                page.add(
                    b_nome,
                    ft.Row([b_vento, b_eq], spacing=12, alignment=ft.MainAxisAlignment.START),
                    ft.Row([b_alte, b_basse, b_strallo], spacing=12, alignment=ft.MainAxisAlignment.START),
                    b_primo_uso,
                    b_commenti,
                    b_err,
                    ft.Button("Salva Baseline", icon=ft.Icons.ADD, bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE, width=370, on_click=salva_nuova_bl),
                )

        # ======================================================================
        # TAB 3: INVENTARIO VELE (RANDE, FIOCCO/GENOA, PRUA)
        # ======================================================================
        elif stato["tab_attiva"] == "vele":
            vele = db.get_inventario_vele(barca["id"])
            categorie = [
                ("randa", "Rande"),
                ("fiocco_genoa", "Fiocco / Genoa"),
                ("prua", "Vele di Prua (Spi / Gennaker)"),
            ]

            for cat_key, cat_titolo in categorie:
                page.add(ft.Text(cat_titolo, size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800))
                vele_cat = [v for v in vele if v["categoria"] == cat_key]
                if not vele_cat:
                    page.add(ft.Text("Nessuna vela inserita.", size=12, italic=True, color=ft.Colors.GREY_600))
                for v in vele_cat:
                    def cancella_vela(e, v_id=v["id"]):
                        db.elimina_vela(v_id)
                        build_dashboard_view(page, stato, on_logout, on_open_nuova_barca, on_open_condividi)

                    info_extra = " • ".join(filter(None, [v.get("velaio"), str(v["anno"]) if v.get("anno") else None, v.get("note")]))
                    row_v = [
                        ft.Column(
                            [
                                ft.Text(v["nome_vela"], weight=ft.FontWeight.BOLD, size=13),
                                ft.Text(info_extra or "Nessun dettaglio", size=11, color=ft.Colors.GREY_700),
                            ],
                            spacing=1,
                        )
                    ]
                    if puo_modificare:
                        row_v.append(ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color=ft.Colors.RED_600, icon_size=18, on_click=cancella_vela))

                    page.add(
                        ft.Container(
                            content=ft.Row(row_v, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            padding=8,
                            border=ft.Border.all(1, ft.Colors.GREY_300),
                            border_radius=8,
                        )
                    )

            if puo_modificare:
                page.add(ft.Divider(height=15), ft.Text("+ Aggiungi Vela all'Inventario", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800))
                v_cat = ft.Dropdown(
                    label="Categoria *",
                    value="fiocco_genoa",
                    options=[
                        ft.dropdown.Option(key="randa", text="Mainsail"),
                        ft.dropdown.Option(key="fiocco_genoa", text="Headsail"),
                        ft.dropdown.Option(key="prua", text="Kite"),
                    ],
                    width=370,
                )
                v_nome = ft.TextField(label="Nome Vela (es. fiocco 1 Eurosail) *", width=370, dense=True)
                v_velaio = ft.TextField(label="Velaio", width=230, dense=True)
                v_anno = ft.TextField(label="Anno", width=130, dense=True, keyboard_type=ft.KeyboardType.NUMBER)
                v_note = ft.TextField(label="Note (es. vento leggero, regata)", width=370, dense=True)
                v_err = ft.Text("", color=ft.Colors.RED_600, size=12)

                def salva_nuova_vela(e):
                    if not v_nome.value.strip():
                        v_err.value = "Inserisci il nome della vela."
                        page.update()
                        return
                    db.aggiungi_vela(
                        barca["id"],
                        {
                            "categoria": v_cat.value,
                            "nome_vela": v_nome.value.strip(),
                            "velaio": v_velaio.value.strip() or None,
                            "anno": int(v_anno.value) if v_anno.value.strip().isdigit() else None,
                            "note": v_note.value.strip() or None,
                        },
                    )
                    build_dashboard_view(page, stato, on_logout, on_open_nuova_barca, on_open_condividi)

                page.add(
                    v_cat,
                    v_nome,
                    ft.Row([v_velaio, v_anno], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    v_note,
                    v_err,
                    ft.Button("Aggiungi Vela", icon=ft.Icons.ADD, bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE, width=370, on_click=salva_nuova_vela),
                )

        # ======================================================================
        # TAB 4: DIARIO USCITE (LOG_TENSIONI + VELE USATE)
        # ======================================================================
        elif stato["tab_attiva"] == "log":
            vele = db.get_inventario_vele(barca["id"])
            logs = db.get_log_tensioni(barca["id"])

            if puo_modificare:
                page.add(ft.Text("+ Registra Nuova Uscita / Allenamento", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800))
                l_data = ft.TextField(label="Data (AAAA-MM-GG)", value=str(date.today()), width=180, dense=True)
                l_vento = ft.TextField(label="Vento (es. 10-12 kn)", width=180, dense=True)
                l_onda = ft.TextField(label="Condizioni Onda (es. Piatta / Formata)", width=370, dense=True)

                l_alte = ft.TextField(label="Alte (V1)", width=118, dense=True, keyboard_type=ft.KeyboardType.NUMBER)
                l_basse = ft.TextField(label="Basse (D1)", width=118, dense=True, keyboard_type=ft.KeyboardType.NUMBER)
                l_strallo = ft.TextField(label="Strallo", width=118, dense=True, keyboard_type=ft.KeyboardType.NUMBER)

                # Menu a tendina popolati dall'inventario vele della barca
                opt_rande = [ft.dropdown.Option(key="", text="Nessuna")] + [
                    ft.dropdown.Option(key=v["id"], text=v["nome_vela"]) for v in vele if v["categoria"] == "randa"
                ]
                opt_fiocchi = [ft.dropdown.Option(key="", text="Nessuna")] + [
                    ft.dropdown.Option(key=v["id"], text=v["nome_vela"]) for v in vele if v["categoria"] == "fiocco_genoa"
                ]
                opt_prua = [ft.dropdown.Option(key="", text="Nessuna")] + [
                    ft.dropdown.Option(key=v["id"], text=v["nome_vela"]) for v in vele if v["categoria"] == "prua"
                ]

                l_randa = ft.Dropdown(label="Randa usata", value="", options=opt_rande, width=370)
                l_fiocco = ft.Dropdown(label="Fiocco / Genoa usato", value="", options=opt_fiocchi, width=370)
                l_prua = ft.Dropdown(label="Vela di prua usata", value="", options=opt_prua, width=370)
                l_commento = ft.TextField(label="Commento Armatore", width=370, dense=True, multiline=True)

                def parse_num_log(val):
                    try:
                        return float(val.replace(",", ".")) if val and val.strip() else None
                    except ValueError:
                        return None

                def salva_uscita(e):
                    db.aggiungi_log_tensione(
                        barca["id"],
                        {
                            "data": l_data.value.strip() or str(date.today()),
                            "condizioni_vento": l_vento.value.strip() or None,
                            "condizioni_onda": l_onda.value.strip() or None,
                            "tensione_alte": parse_num_log(l_alte.value),
                            "tensione_basse": parse_num_log(l_basse.value),
                            "tensione_strallo": parse_num_log(l_strallo.value),
                            "randa_id": l_randa.value if l_randa.value else None,
                            "fiocco_genoa_id": l_fiocco.value if l_fiocco.value else None,
                            "vela_prua_id": l_prua.value if l_prua.value else None,
                            "commento_armatore": l_commento.value.strip() or None,
                        },
                    )
                    build_dashboard_view(page, stato, on_logout, on_open_nuova_barca, on_open_condividi)

                page.add(
                    ft.Row([l_data, l_vento], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    l_onda,
                    ft.Row([l_alte, l_basse, l_strallo], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    l_randa,
                    l_fiocco,
                    l_prua,
                    l_commento,
                    ft.Button("Registra Uscita", icon=ft.Icons.SAVE, bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE, width=370, on_click=salva_uscita),
                    ft.Divider(height=15),
                )

            page.add(ft.Text("Storico Uscite & Tensioni", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800))
            if not logs:
                page.add(ft.Text("Nessuna uscita registrata nel diario.", size=12, italic=True, color=ft.Colors.GREY_600))

            for lg in logs:
                def rimuovi_lg(e, lg_id=lg["id"]):
                    db.elimina_log_tensione(lg_id)
                    build_dashboard_view(page, stato, on_logout, on_open_nuova_barca, on_open_condividi)

                vele_usate = []
                if lg.get("randa"):
                    vele_usate.append(f"Randa: {lg['randa']['nome_vela']}")
                if lg.get("fiocco_genoa"):
                    vele_usate.append(f"Prua/Genoa: {lg['fiocco_genoa']['nome_vela']}")
                if lg.get("vela_prua"):
                    vele_usate.append(f"Spi: {lg['vela_prua']['nome_vela']}")

                top_lg = [
                    ft.Column(
                        [
                            ft.Text(f"📅 {lg['data']}  •  Vento: {lg.get('condizioni_vento') or '-'}", weight=ft.FontWeight.BOLD, size=13, color=ft.Colors.BLUE_900),
                            ft.Text(f"Onda: {lg.get('condizioni_onda') or '-'}", size=12, color=ft.Colors.GREY_700),
                        ],
                        spacing=1,
                    )
                ]
                if puo_modificare:
                    top_lg.append(ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color=ft.Colors.RED_600, icon_size=18, on_click=rimuovi_lg))

                corpo_lg = [
                    ft.Row(top_lg, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Text(f"Alte: {lg.get('tensione_alte') if lg.get('tensione_alte') is not None else '-'}", weight=ft.FontWeight.BOLD, size=12),
                                ft.Text(f"Basse: {lg.get('tensione_basse') if lg.get('tensione_basse') is not None else '-'}", weight=ft.FontWeight.BOLD, size=12),
                                ft.Text(f"Strallo: {lg.get('tensione_strallo') if lg.get('tensione_strallo') is not None else '-'}", weight=ft.FontWeight.BOLD, size=12),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        bgcolor=ft.Colors.GREY_100,
                        padding=8,
                        border_radius=6,
                    ),
                ]
                if vele_usate:
                    corpo_lg.append(ft.Text("⛵ " + " | ".join(vele_usate), size=11, color=ft.Colors.BLUE_800))
                if lg.get("commento_armatore"):
                    corpo_lg.append(ft.Text(f"\"{lg['commento_armatore']}\"", size=12, italic=True))

                page.add(
                    ft.Container(
                        content=ft.Column(corpo_lg, spacing=6),
                        padding=10,
                        border=ft.Border.all(1, ft.Colors.GREY_300),
                        border_radius=10,
                    )
                )

    except Exception as err:
        page.add(ft.Text(f"Errore nel caricamento: {err}", color=ft.Colors.RED_600))

    page.update()