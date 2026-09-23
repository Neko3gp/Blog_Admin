"""
main_gui.py
Punto de entrada de la GUI del Administrador de Blog.

Rediseño de la ventana de 8 botones apilados hacia una navegación tipo
feed/blog: barra lateral + área de contenido que cambia entre Feed,
Usuarios, Categorías/Etiquetas y el formulario de Publicar Artículo
(ver directivas_rediseño_gui.md).

No cambia el modelo de datos, ni el Contrato de Nombres de PL/SQL, ni el
contrato público de db_connection.py — solo la capa visual.

Nota de plataforma: en macOS, tk.Button ignora bg/fg porque usa el widget
nativo de Aqua. Por eso los botones de navegación del sidebar están hechos
con tk.Label + bindings de clic/hover (_make_nav_button) en vez de
tk.Button — así los colores sí se respetan en Mac, Windows y Linux por
igual.
"""

import tkinter as tk

import theme
from views.feed import FeedView
from views.article_detail import ArticleDetailView
from views.users import UsersView
from views.taxonomy import TaxonomyView
from views.new_article import abrir_form_publicar_articulo

# Los colores viven en theme.py — cámbialos ahí y se reflejan en toda la app.
SIDEBAR_BG = theme.SIDEBAR_BG
SIDEBAR_TEXT = theme.SIDEBAR_TEXT
SIDEBAR_TEXT_ACTIVE = theme.SIDEBAR_TEXT_ACTIVE
SIDEBAR_HOVER_BG = theme.SIDEBAR_HOVER_BG
SIDEBAR_SELECTED_BG = theme.SIDEBAR_SELECTED_BG
SIDEBAR_DIVIDER = theme.SIDEBAR_DIVIDER
SIDEBAR_MUTED = theme.SIDEBAR_MUTED
CONTENT_BG = theme.CONTENT_BG


class BlogAdminApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Administrador de Blog")
        self.geometry("1000x650")
        self.minsize(820, 560)

        self._nav_buttons = {}  # clave de página -> Label, para marcar la activa
        self._active_page = None

        self._build_sidebar()
        self._build_content_area()
        self._show_feed()

    # ---------- estructura general ----------

    def _build_sidebar(self):
        sidebar = tk.Frame(self, bg=SIDEBAR_BG, width=210)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(
            sidebar, text="Admin de Blog", font=("Segoe UI", 13, "bold"),
            bg=SIDEBAR_BG, fg=SIDEBAR_TEXT_ACTIVE, pady=20,
        ).pack(fill="x")

        nav_items = [
            ("feed", "Feed principal", self._show_feed),
            ("users", "Usuarios", self._show_users),
            ("taxonomy", "Categorías / Etiquetas", self._show_taxonomy),
        ]
        for clave, texto, comando in nav_items:
            self._nav_buttons[clave] = self._make_nav_button(sidebar, texto, comando, page_key=clave)

        tk.Frame(sidebar, bg=SIDEBAR_DIVIDER, height=1).pack(fill="x", pady=10)

        tk.Label(
            sidebar, text="ACCIONES", font=("Segoe UI", 8, "bold"),
            bg=SIDEBAR_BG, fg=SIDEBAR_MUTED, anchor="w", padx=20,
        ).pack(fill="x")

        self._make_nav_button(
            sidebar, "+ Publicar artículo",
            lambda: abrir_form_publicar_articulo(self, on_saved=self._show_feed),
        )

    def _make_nav_button(self, parent, texto, comando, page_key=None):
        """
        Crea un renglón de navegación clicable usando tk.Label en vez de
        tk.Button (ver nota de plataforma arriba). Si se pasa page_key,
        el renglón se resalta cuando esa página está activa.
        """
        lbl = tk.Label(
            parent, text=texto, bg=SIDEBAR_BG, fg=SIDEBAR_TEXT,
            anchor="w", padx=20, pady=10, font=("Segoe UI", 10),
            cursor="hand2",
        )
        lbl.pack(fill="x")

        def on_click(_event):
            comando()

        def on_enter(_event):
            if page_key is None or page_key != self._active_page:
                lbl.configure(bg=SIDEBAR_HOVER_BG, fg=SIDEBAR_TEXT_ACTIVE)

        def on_leave(_event):
            if page_key is None or page_key != self._active_page:
                lbl.configure(bg=SIDEBAR_BG, fg=SIDEBAR_TEXT)

        lbl.bind("<Button-1>", on_click)
        lbl.bind("<Enter>", on_enter)
        lbl.bind("<Leave>", on_leave)
        return lbl

    def _set_active_nav(self, page_key):
        self._active_page = page_key
        for clave, lbl in self._nav_buttons.items():
            if clave == page_key:
                lbl.configure(bg=SIDEBAR_SELECTED_BG, fg=SIDEBAR_TEXT_ACTIVE)
            else:
                lbl.configure(bg=SIDEBAR_BG, fg=SIDEBAR_TEXT)

    def _build_content_area(self):
        self.content = tk.Frame(self, bg=CONTENT_BG)
        self.content.pack(side="right", fill="both", expand=True)

    def _clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    # ---------- navegación ----------

    def _show_feed(self):
        self._clear_content()
        self._set_active_nav("feed")
        FeedView(self.content, on_open_article=self._show_article_detail).pack(fill="both", expand=True)

    def _show_users(self):
        self._clear_content()
        self._set_active_nav("users")
        UsersView(self.content).pack(fill="both", expand=True)

    def _show_taxonomy(self):
        self._clear_content()
        self._set_active_nav("taxonomy")
        TaxonomyView(self.content).pack(fill="both", expand=True)

    def _show_article_detail(self, article):
        self._clear_content()
        self._set_active_nav(None)
        ArticleDetailView(self.content, article, on_back=self._show_feed).pack(fill="both", expand=True)


def main():
    app = BlogAdminApp()
    app.mainloop()


if __name__ == "__main__":
    main()
