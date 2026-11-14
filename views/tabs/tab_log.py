from datetime import date
import flet as ft
import db


def build_tab_log(page: ft.Page, barca: dict, puo_modificare: bool, on_refresh):
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
            on_refresh()

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
            on_refresh()

        vele_usate = []
        if lg.get("randa"):
            vele_usate.append(f"Mainsail: {lg['randa']['nome_vela']}")
        if lg.get("fiocco_genoa"):
            vele_usate.append(f"Headsail: {lg['fiocco_genoa']['nome_vela']}")
        if lg.get("vela_prua"):
            vele_usate.append(f"Kite: {lg['vela_prua']['nome_vela']}")

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