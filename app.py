import flet as ft
from views.login_view import build_login_view
from views.dashboard_view import build_dashboard_view
from views.nuova_barca_view import build_nuova_barca_view
from views.condividi_view import build_condividi_view


def main(page: ft.Page):
    page.title = "TensApp - Boat Specs"
    page.window.width = 410
    page.window.height = 800
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    stato = {
        "user": None,
        "barche": [],
        "permessi_condivisi": {},
        "barca_selezionata_id": None,
    }

    def vai_a_login():
        build_login_view(page, stato, on_login_success=vai_a_dashboard)

    def vai_a_dashboard():
        build_dashboard_view(
            page,
            stato,
            on_logout=vai_a_login,
            on_open_nuova_barca=vai_a_nuova_barca,
            on_open_condividi=vai_a_condividi,
        )

    def vai_a_nuova_barca():
        build_nuova_barca_view(page, stato, on_back=vai_a_dashboard)

    def vai_a_condividi(barca: dict):
        build_condividi_view(page, barca, on_back=vai_a_dashboard)

    # Avvio dall'accesso
    vai_a_login()


ft.run(main, view=ft.AppView.WEB_BROWSER, port=8550)