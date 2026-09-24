"""Punto de entrada y navegación principal de la aplicación de escritorio.

La ventana coordina la barra lateral, el área de contenido y las vistas de
feed, detalle, usuarios, categorías y etiquetas. La navegación solo cambia
la capa visual; el modelo de datos y los contratos PL/SQL permanecen en sus
módulos especializados.
"""

import customtkinter as ctk

import theme
from views.feed import FeedView
from views.article_detail import ArticleDetailView
from views.users import UsersView
from views.taxonomy import CategoriesView, TagsView
from views.new_article import abrir_form_publicar_articulo

ctk.set_appearance_mode("dark")

class BlogAdminApp(ctk.CTk):
    """Ventana raíz que coordina la navegación del administrador."""

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

        # Grid permite ocultar la barra lateral sin afectar el área principal.
        self.main_container = ctk.CTkFrame(self, fg_color=theme.CONTENT_BG)
        self.main_container.pack(fill="both", expand=True)
        self.main_container.grid_columnconfigure(1, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)

        self._build_sidebar(self.main_container)
        self._build_content_area(self.main_container)
        self.after(100, self._show_feed)

    def _build_top_bar(self):
        """Construye la barra superior y el control de menú."""
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
        """Construye la navegación y la acción de publicación."""
        self.sidebar = ctk.CTkFrame(parent, fg_color=theme.SIDEBAR_BG, width=240, corner_radius=0)
        self.sidebar.grid_propagate(False)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        ctk.CTkFrame(self.sidebar, fg_color="transparent", height=20).pack(fill="x")

        nav_items = [
            ("feed", "Inicio", self._show_feed),
            ("users", "Usuarios", self._show_users),
            ("categories", "Categorías", self._show_categories),
            ("tags", "Etiquetas", self._show_tags),
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
        """Alterna la visibilidad de la barra lateral."""
        if self._sidebar_visible:
            self.sidebar.grid_remove()
            self._sidebar_visible = False
        else:
            self.sidebar.grid(row=0, column=0, sticky="nsew")
            self._sidebar_visible = True

    def _make_nav_button(self, parent, texto, comando, page_key=None):
        """Crea un botón de navegación asociado a una vista."""
        btn = ctk.CTkButton(
            parent, text=texto, anchor="w", fg_color="transparent",
            text_color=theme.SIDEBAR_TEXT, hover_color=theme.SIDEBAR_HOVER_BG,            font=ctk.CTkFont(family="Helvetica", size=14), command=comando, corner_radius=8
        )
        btn.pack(fill="x", padx=10, pady=2)
        return btn

    def _set_active_nav(self, page_key):
        """Actualiza el estilo de la opción de navegación activa."""
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
        """Crea el contenedor donde se monta la vista seleccionada."""
        self.content = ctk.CTkFrame(parent, fg_color=theme.CONTENT_BG, corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")

    def _clear_content(self):
        """Destruye la vista actualmente montada."""
        for widget in self.content.winfo_children():
            widget.destroy()

    def _show_feed(self):
        """Muestra el feed de artículos."""
        self._clear_content()
        self._set_active_nav("feed")
        FeedView(self.content, on_open_article=self._show_article_detail).pack(fill="both", expand=True)

    def _show_users(self):
        """Muestra la administración de usuarios."""
        self._clear_content()
        self._set_active_nav("users")
        UsersView(self.content).pack(fill="both", expand=True)

    def _show_categories(self):
        """Muestra la administración de categorías."""
        self._clear_content()
        self._set_active_nav("categories")
        CategoriesView(self.content).pack(fill="both", expand=True)

    def _show_tags(self):
        """Muestra la administración de etiquetas."""
        self._clear_content()
        self._set_active_nav("tags")
        TagsView(self.content).pack(fill="both", expand=True)

    def _show_article_detail(self, article):
        """Muestra el detalle del artículo seleccionado."""
        self._clear_content()
        self._set_active_nav(None)
        ArticleDetailView(self.content, article, on_back=self._show_feed).pack(fill="both", expand=True)

def main():
    """Crea la ventana raíz e inicia el bucle de eventos de Tkinter."""
    app = BlogAdminApp()
    app.after(50, app.lift)
    app.after(50, app.focus_force)
    app.mainloop()

if __name__ == "__main__":
    main()