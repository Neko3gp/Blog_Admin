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

"""
Punto de entrada de la GUI del Administrador de Blog.
Rediseño implementando una barra lateral flotante e independiente del área de contenido.
"""

import customtkinter as ctk

import theme
from views.feed import FeedView
from views.article_detail import ArticleDetailView
from views.users import UsersView
from views.taxonomy import TaxonomyView
from views.new_article import abrir_form_publicar_articulo

ctk.set_appearance_mode("dark")

class BlogAdminApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Administrador de Blog")
        self.geometry("1050x680")
        self.minsize(820, 560)
        self.configure(fg_color=theme.CONTENT_BG)

        self._nav_buttons = {}
        self._active_page = None
        self._sidebar_visible = True

        self._build_top_bar()

        # Usar grid en lugar de pack para evitar saltos bruscos en la animación
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)
        self.main_container.grid_columnconfigure(1, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)

        self._build_sidebar(self.main_container)
        self._build_content_area(self.main_container)
        self._show_feed()

    def _build_top_bar(self):
        top_bar = ctk.CTkFrame(self, fg_color=theme.CONTENT_BG, height=50, corner_radius=0)
        top_bar.pack(fill="x")
        
        btn_menu = ctk.CTkButton(
            top_bar, text="☰", width=40, height=40, fg_color="transparent",
            text_color=theme.PAGE_FG, hover_color=theme.SIDEBAR_HOVER_BG,
            font=ctk.CTkFont(size=22), command=self._toggle_sidebar
        )
        btn_menu.pack(side="left", padx=10, pady=5)
        
        ctk.CTkLabel(
            top_bar, text="Administrador", 
            font=ctk.CTkFont(family="Helvetica", size=18, weight="bold"),
            text_color=theme.SIDEBAR_TEXT_ACTIVE
        ).pack(side="left", padx=5)

    def _build_sidebar(self, parent):
        self.sidebar = ctk.CTkFrame(parent, fg_color=theme.SIDEBAR_BG, width=240, corner_radius=0)
        self.sidebar.grid_propagate(False)
        self.sidebar.grid(row=0, column=0, sticky="ns")

        ctk.CTkFrame(self.sidebar, fg_color="transparent", height=20).pack(fill="x")

        nav_items = [
            ("feed", "Inicio", self._show_feed),
            ("users", "Usuarios", self._show_users),
            ("taxonomy", "Categorías / Etiquetas", self._show_taxonomy),
        ]
        
        for clave, texto, comando in nav_items:
            self._nav_buttons[clave] = self._make_nav_button(self.sidebar, texto, comando, page_key=clave)

        ctk.CTkFrame(self.sidebar, fg_color=theme.SIDEBAR_DIVIDER, height=1).pack(fill="x", pady=15, padx=20)

        ctk.CTkLabel(
            self.sidebar, text="ACCIONES", font=ctk.CTkFont(family="Helvetica", size=11, weight="bold"),
            text_color=theme.SIDEBAR_MUTED, anchor="w"
        ).pack(fill="x", padx=20, pady=(0, 10))

        action_btn = ctk.CTkButton(
            self.sidebar, text="+ Publicar artículo", fg_color=theme.SIDEBAR_SELECTED_TEXT,
            text_color="#131314", hover_color="#8AB4F8", corner_radius=8, 
            font=ctk.CTkFont(family="Helvetica", size=13, weight="bold"),
            command=lambda: abrir_form_publicar_articulo(self, on_saved=self._show_feed)
        )
        action_btn.pack(fill="x", padx=15, pady=5)

    def _toggle_sidebar(self):
        if self._sidebar_visible:
            self.sidebar.grid_remove()
            self._sidebar_visible = False
        else:
            self.sidebar.grid(row=0, column=0, sticky="ns")
            self._sidebar_visible = True

    def _make_nav_button(self, parent, texto, comando, page_key=None):
        btn = ctk.CTkButton(
            parent, text=texto, anchor="w", fg_color="transparent",
            text_color=theme.SIDEBAR_TEXT, hover_color=theme.SIDEBAR_HOVER_BG,
            font=ctk.CTkFont(family="Helvetica", size=14), command=comando, corner_radius=8
        )
        btn.pack(fill="x", padx=10, pady=2)
        return btn

    def _set_active_nav(self, page_key):
        self._active_page = page_key
        for clave, btn in self._nav_buttons.items():
            if clave == page_key:
                btn.configure(
                    fg_color=theme.SIDEBAR_SELECTED_BG, hover_color=theme.SIDEBAR_SELECTED_BG,
                    text_color=theme.SIDEBAR_SELECTED_TEXT, font=ctk.CTkFont(family="Helvetica", size=14, weight="bold")
                )
            else:
                btn.configure(
                    fg_color="transparent", hover_color=theme.SIDEBAR_HOVER_BG,
                    text_color=theme.SIDEBAR_TEXT, font=ctk.CTkFont(family="Helvetica", size=14, weight="normal")
                )

    def _build_content_area(self, parent):
        self.content = ctk.CTkFrame(parent, fg_color=theme.CONTENT_BG, corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")

    def _clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

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