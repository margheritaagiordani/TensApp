from datetime import date
import flet as ft
import db


def build_tab_baseline(page: ft.Page, barca: dict, puo_modificare: bool, on_refresh):
    baselines = db.get_baseline_barca(barca["id"])
    dati_barca = barca["dati_regolazioni"].get("dati_barca", {})
    scala = dati_barca.get("scala_tensiometro", "Loos PT-1")
    page.add(ft.Text(f"Baseline di Riferimento ({scala})", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800))

    if not baselines:
        page.add(ft.Text("Nessuna baseline registrata per questa barca.", size=12, italic=True, color=ft.Colors.GREY_600))

    for bl in baselines:
        def rimuovi_bl(e, bl_id=bl["id"]):
            db.elimina_baseline(bl_id)
            on_refresh()

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
            on_refresh()

        page.add(
            b_nome,
            ft.Row([b_vento, b_eq], spacing=12, alignment=ft.MainAxisAlignment.START),
            ft.Row([b_alte, b_basse, b_strallo], spacing=12, alignment=ft.MainAxisAlignment.START),
            b_primo_uso,
            b_commenti,
            b_err,
            ft.Button("Salva Baseline", icon=ft.Icons.ADD, bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE, width=370, on_click=salva_nuova_bl),
        )
        