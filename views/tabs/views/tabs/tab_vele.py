import flet as ft
import db


def build_tab_vele(page: ft.Page, barca: dict, puo_modificare: bool, on_refresh):
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
                on_refresh()

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
            on_refresh()

        page.add(
            v_cat,
            v_nome,
            ft.Row([v_velaio, v_anno], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            v_note,
            v_err,
            ft.Button("Aggiungi Vela", icon=ft.Icons.ADD, bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE, width=370, on_click=salva_nuova_vela),
        )
        