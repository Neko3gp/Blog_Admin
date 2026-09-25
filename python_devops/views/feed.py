"""Feed — lectura: pkg_articles.get_all_articles (+ taxonomía vía article_tags/categories).
Create: botón en main_gui → new_article.py. Update/Delete: article_detail.py."""

import customtkinter as ctk

import theme
from db_connection import fetch_options, fetch_article_taxonomy
from utils import safe_get_all, users_lookup
from widgets.cards import ArticleCard

class FeedView(ctk.CTkFrame):
    def __init__(self, parent, on_open_article):
        super().__init__(parent, fg_color=theme.CONTENT_BG)
        self.on_open_article = on_open_article
        self._articles = None

        self._build_toolbar()
        self._build_feed_area()
        self.reload()

    def _build_toolbar(self):
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=16, pady=(14, 8))

        controls = ctk.CTkFrame(toolbar, fg_color="transparent")
        controls.pack(side="right")

        ctk.CTkLabel(controls, text="Ordenar:", text_color=theme.CONTENT_FG).pack(side="left", padx=(0, 4))
        self.combo_orden = ctk.CTkComboBox(
            controls, state="readonly", width=180,
            values=["Más reciente primero", "Más antiguo primero"],
            fg_color=theme.ENTRY_BG, border_color=theme.ENTRY_BORDER,
            text_color=theme.ENTRY_FG, dropdown_fg_color=theme.DROPDOWN_BG,
            dropdown_text_color=theme.DROPDOWN_TEXT,
            button_color=theme.ENTRY_BORDER, button_hover_color=theme.BTN_SECONDARY_HOVER,
            command=self._on_filter_change
        )
        self.combo_orden.set("Más reciente primero")
        self.combo_orden.pack(side="left", padx=(0, 12))

        ctk.CTkLabel(controls, text="Categoría:", text_color=theme.CONTENT_FG).pack(side="left", padx=(0, 4))
        self.combo_categoria = ctk.CTkComboBox(
            controls, state="readonly", width=140,
            fg_color=theme.ENTRY_BG, border_color=theme.ENTRY_BORDER,
            text_color=theme.ENTRY_FG, dropdown_fg_color=theme.DROPDOWN_BG,
            dropdown_text_color=theme.DROPDOWN_TEXT,
            button_color=theme.ENTRY_BORDER, button_hover_color=theme.BTN_SECONDARY_HOVER,
            command=self._on_filter_change
        )
        self.combo_categoria.pack(side="left", padx=(0, 12))

        ctk.CTkLabel(controls, text="Tag:", text_color=theme.CONTENT_FG).pack(side="left", padx=(0, 4))
        self.combo_tag = ctk.CTkComboBox(
            controls, state="readonly", width=140,
            fg_color=theme.ENTRY_BG, border_color=theme.ENTRY_BORDER,
            text_color=theme.ENTRY_FG, dropdown_fg_color=theme.DROPDOWN_BG,
            dropdown_text_color=theme.DROPDOWN_TEXT,
            button_color=theme.ENTRY_BORDER, button_hover_color=theme.BTN_SECONDARY_HOVER,
            command=self._on_filter_change
        )
        self.combo_tag.pack(side="left", padx=(0, 12))

        

        self._cargar_filtros()

    def _on_filter_change(self, value):
        self._render()

    def _cargar_filtros(self):
        try:
            categorias = fetch_options("categories", "id", "name")
        except Exception:
            categorias = []
        try:
            tags = fetch_options("tags", "id", "name")
        except Exception:
            tags = []

        self.combo_categoria.configure(values=["Todas"] + [nombre for _, nombre in categorias])
        self.combo_categoria.set("Todas")
        self.combo_tag.configure(values=["Todos"] + [nombre for _, nombre in tags])
        self.combo_tag.set("Todos")

    def _build_feed_area(self):
        self.scroll_area = ctk.CTkScrollableFrame(
            self, fg_color="transparent", 
            scrollbar_button_color=theme.SCROLLBAR_FG,
            scrollbar_button_hover_color=theme.SCROLLBAR_HOVER
        )
        self.scroll_area.pack(fill="both", expand=True, padx=16, pady=(0, 16))

    def reload(self):
        author_by_id = users_lookup()
        rows = safe_get_all("pkg_articles.get_all_articles")
        if rows is None:
            self._articles = None
        else:
            self._articles = []
            for row in rows:
                article_id = row[0]
                tags, categories = fetch_article_taxonomy(article_id)
                self._articles.append(
                    {
                        "id": article_id, "title": row[1], "date": row[2],
                        "author": author_by_id.get(row[3], f"Usuario {row[3]}"),
                        "snippet": "", "tags": tags, "categories": categories,
                    }
                )
        self._render()

    def _render(self):
        for widget in self.scroll_area.winfo_children():
            widget.destroy()

        self.update_idletasks()

        if self._articles is None:
            self._render_placeholder("pendiente de conectar con pkg_articles.get_all_articles")
            return

        articulos = list(self._articles)

        if self.combo_categoria.get() not in ("", "Todas"):
            cat = self.combo_categoria.get()
            articulos = [a for a in articulos if cat in a.get("categories", [])]
        if self.combo_tag.get() not in ("", "Todos"):
            tag = self.combo_tag.get()
            articulos = [a for a in articulos if tag in a.get("tags", [])]

        reverse = self.combo_orden.get() != "Más antiguo primero"
        articulos.sort(key=lambda a: a.get("date") or "", reverse=reverse)

        if not articulos:
            self._render_placeholder("No hay artículos que mostrar todavía.")
            return

        for articulo in articulos:
            ArticleCard(self.scroll_area, articulo, on_click=self.on_open_article).pack(
                fill="x", pady=6
            )

    def _render_placeholder(self, mensaje):
        ctk.CTkLabel(
            self.scroll_area, text=mensaje, 
            font=ctk.CTkFont(family="Segoe UI", size=13, slant="italic"),
            text_color=theme.TEXT_MUTED, pady=40
        ).pack(fill="x")