import flet as ft
import db
from views.tabs.tab_barca import build_tab_barca
from views.tabs.tab_baseline import build_tab_baseline
from views.tabs.tab_vele import build_tab_vele
from views.tabs.tab_log import build_tab_log


def build_dashboard_view(page: ft.Page, stato: dict, on_logout, on_open_nuova_barca, on_open_condividi):
    page.clean()
    try:
        user_id = stato["user"].id

        barche, permessi = db.get_barche_e_permessi(user_id)
        stato["barche"] = barche
        stato["permessi_condivisi"] = permessi

        if "tab_attiva" not in stato:
            stato["tab_attiva"] = "barca"

        def ricarica():
            build_dashboard_view(page, stato, on_logout, on_open_nuova_barca, on_open_condividi)

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
            ricarica()

        dropdown_barche = ft.Dropdown(
            label="Seleziona Barca",
            value=stato["barca_selezionata_id"],
            options=opzioni_dropdown,
            width=370,
            on_select=cambia_barca,
        )
        page.add(dropdown_barche)

        # Dati barca attiva e permessi
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

        dati_barca = barca["dati_regolazioni"].get("dati_barca", {})
        is_custom = not bool(barca.get("dati_regolazioni", {}).get("specifiche_fisse"))
        nome_classe_mostrato = (
            dati_barca.get("modello_barca") #or "Barca Personalizzata"
            if is_custom
            else barca["classe_id"].upper()
        )

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
                                        f"{nome_classe_mostrato} | {barca.get('numero_velico', '')}",
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

        def seleziona_tab(nome_tab: str):
            stato["tab_attiva"] = nome_tab
            ricarica()

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

        # Delega del disegno alle singole tab modulari
        if stato["tab_attiva"] == "barca":
            build_tab_barca(page, barca, puo_modificare, on_refresh=ricarica)
        elif stato["tab_attiva"] == "baseline":
            build_tab_baseline(page, barca, puo_modificare, on_refresh=ricarica)
        elif stato["tab_attiva"] == "vele":
            build_tab_vele(page, barca, puo_modificare, on_refresh=ricarica)
        elif stato["tab_attiva"] == "log":
            build_tab_log(page, barca, puo_modificare, on_refresh=ricarica)

    except Exception as err:
        page.add(ft.Text(f"Errore nel caricamento: {err}", color=ft.Colors.RED_600))

    page.update()