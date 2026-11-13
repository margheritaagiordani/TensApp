import flet as ft
import db


def build_dashboard_view(page: ft.Page, stato: dict, on_logout, on_open_nuova_barca, on_open_condividi):
    page.clean()
    try:
        user_id = stato["user"].id
        barche, permessi_condivisi = db.get_barche_e_permessi(user_id)
        stato["barche"] = barche
        stato["permessi_condivisi"] = permessi_condivisi

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

        if not barche:
            page.add(
                ft.Container(height=20),
                ft.Text("Nessuna barca trovata nel tuo profilo."),
                ft.Button("Aggiungi la tua prima barca", icon=ft.Icons.ADD, on_click=lambda _: on_open_nuova_barca()),
            )
            page.update()
            return

        ids_disponibili = [b["id"] for b in barche]
        if stato["barca_selezionata_id"] not in ids_disponibili:
            stato["barca_selezionata_id"] = ids_disponibili[0]

        opzioni_dropdown = []
        for b in barche:
            is_owner = b["owner_id"] == user_id
            etichetta_ruolo = "Mia" if is_owner else "Condivisa"
            num_velico = f" ({b['numero_velico']})" if b.get("numero_velico") else ""
            opzioni_dropdown.append(
                ft.dropdown.Option(key=b["id"], text=f"{b['nome_barca']}{num_velico} • {etichetta_ruolo}")
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
        page.add(dropdown_barche, ft.Divider(height=15))

        barca = next(b for b in barche if b["id"] == stato["barca_selezionata_id"])
        is_owner = barca["owner_id"] == user_id
        permesso = "owner" if is_owner else permessi_condivisi.get(barca["id"], "read")
        puo_modificare = permesso in ("owner", "write")

        if permesso == "owner":
            badge_testo, badge_colore = "Proprietario", ft.Colors.BLUE_700
        elif permesso == "write":
            badge_testo, badge_colore = "Condivisa (Modifica)", ft.Colors.ORANGE_700
        else:
            badge_testo, badge_colore = "Condivisa (Sola lettura)", ft.Colors.GREY_700

        dati = barca["dati_regolazioni"]
        specs = dati["specifiche_fisse"]

        # Pulsante Condividi visibile solo al proprietario
        azioni_card = [
            ft.Container(
                content=ft.Text(badge_testo, size=11, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                bgcolor=badge_colore,
                padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                border_radius=8,
            )
        ]
        if is_owner:
            azioni_card.append(
                ft.IconButton(
                    icon=ft.Icons.SHARE,
                    icon_color=ft.Colors.BLUE_700,
                    tooltip="Condividi barca",
                    on_click=lambda _: on_open_condividi(barca),
                )
            )

        card_info = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Row(
                                [
                                    ft.Icon(ft.Icons.SAILING, color=ft.Colors.BLUE_700, size=28),
                                    ft.Column(
                                        [
                                            ft.Text(barca["nome_barca"], size=19, weight=ft.FontWeight.BOLD),
                                            ft.Text(
                                                f"Classe: {barca['classe_id'].upper()} | {barca['numero_velico']}",
                                                size=12,
                                                color=ft.Colors.GREY_700,
                                            ),
                                        ],
                                        spacing=1,
                                    ),
                                ]
                            ),
                            ft.Row(azioni_card, spacing=2),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Divider(height=10),
                    ft.Text(
                        f"LFT: {specs['lunghezza_ft_m']}m  •  Larghezza: {specs['larghezza_max_m']}m  •  Peso: {specs['dislocamento_kg']}kg",
                        size=12,
                    ),
                ]
            ),
            padding=15,
            bgcolor=ft.Colors.BLUE_50,
            border_radius=12,
        )
        page.add(card_info, ft.Text("Matrice Tensioni Sartie", size=17, weight=ft.FontWeight.W_600))

        campi_input = []
        for idx, riga in enumerate(dati["matrice_vento"]):
            campo_v1 = ft.TextField(
                label="V1 (Alte)",
                value=str(riga["sartie_alte_v1"]),
                width=95,
                keyboard_type=ft.KeyboardType.NUMBER,
                dense=True,
                read_only=not puo_modificare,
            )
            campo_d1 = ft.TextField(
                label="D1 (Basse)",
                value=str(riga["sartie_basse_d1"]),
                width=95,
                keyboard_type=ft.KeyboardType.NUMBER,
                dense=True,
                read_only=not puo_modificare,
            )
            campi_input.append((idx, campo_v1, campo_d1))

            card_vento = ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text(riga["fascia_vento_kn"], weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
                                ft.Text(riga["vela"], size=12, italic=True),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Row(
                            [
                                campo_v1,
                                campo_d1,
                                ft.Text(f"Pat: {riga['paterazzo']}", size=12),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                    ],
                    spacing=8,
                ),
                padding=12,
                border=ft.Border.all(1, ft.Colors.GREY_300),
                border_radius=10,
            )
            page.add(card_vento)

        if puo_modificare:
            messaggio_salvataggio = ft.Text("", color=ft.Colors.GREEN_700, weight=ft.FontWeight.BOLD)

            def salva_modifiche(e):
                for idx, c_v1, c_d1 in campi_input:
                    dati["matrice_vento"][idx]["sartie_alte_v1"] = int(c_v1.value)
                    dati["matrice_vento"][idx]["sartie_basse_d1"] = int(c_d1.value)

                db.aggiorna_regolazioni(barca["id"], dati)
                messaggio_salvataggio.value = "✓ Regolazioni salvate su Supabase!"
                page.update()

            page.add(
                ft.Container(height=10),
                ft.Button(
                    "Salva Modifiche",
                    icon=ft.Icons.SAVE,
                    bgcolor=ft.Colors.BLUE_700,
                    color=ft.Colors.WHITE,
                    width=370,
                    height=45,
                    on_click=salva_modifiche,
                ),
                messaggio_salvataggio,
            )
        else:
            page.add(
                ft.Container(
                    content=ft.Text(
                        "Modalità sola lettura: chiedi al proprietario l'accesso in modifica per aggiornare i valori.",
                        size=12,
                        italic=True,
                        color=ft.Colors.GREY_700,
                    ),
                    padding=10,
                )
            )

    except Exception as err:
        page.add(ft.Text(f"Errore nel caricamento: {err}", color=ft.Colors.RED_600))

    page.update()