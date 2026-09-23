"""
views/feed.py
Vista principal tipo feed: artículos como tarjetas (no un Listbox plano),
con ordenamiento por fecha y filtro por categoría/tag.
"""

import tkinter as tk
from tkinter import ttk

import theme
from db_connection import fetch_options
from utils import safe_get_all, users_lookup
from widgets.cards import ArticleCard
from widgets.scrollframe import ScrollableFrame


class FeedView(tk.Frame):
    def __init__(self, parent, on_open_article):
        super().__init__(parent, bg=theme.CONTENT_BG)
        self.on_open_article = on_open_article
        self._articles = None

        self._build_toolbar()
        self._build_feed_area()
        self.reload()

    # ---------- construcción de UI ----------

    def _build_toolbar(self):
        toolbar = tk.Frame(self, bg=theme.CONTENT_BG)
        toolbar.pack(fill="x", padx=16, pady=(14, 8))

        tk.Label(
            toolbar, text="Feed principal", font=("Segoe UI", 14, "bold"),
            bg=theme.CONTENT_BG, fg="#1a1a1b",
        ).pack(side="left")

        controls = tk.Frame(toolbar, bg=theme.CONTENT_BG)
        controls.pack(side="right")

        tk.Label(controls, text="Ordenar:", bg=theme.CONTENT_BG).pack(side="left", padx=(0, 4))
        self.combo_orden = ttk.Combobox(
            controls, state="readonly", width=18,
            values=["Más reciente primero", "Más antiguo primero"],
        )
        self.combo_orden.current(0)
        self.combo_orden.pack(side="left", padx=(0, 12))
        self.combo_orden.bind("<<ComboboxSelected>>", lambda e: self._render())

        tk.Label(controls, text="Categoría:", bg=theme.CONTENT_BG).pack(side="left", padx=(0, 4))
        self.combo_categoria = ttk.Combobox(controls, state="readonly", width=16)
        self.combo_categoria.pack(side="left", padx=(0, 12))
        self.combo_categoria.bind("<<ComboboxSelected>>", lambda e: self._render())

        tk.Label(controls, text="Tag:", bg=theme.CONTENT_BG).pack(side="left", padx=(0, 4))
        self.combo_tag = ttk.Combobox(controls, state="readonly", width=16)
        self.combo_tag.pack(side="left", padx=(0, 12))
        self.combo_tag.bind("<<ComboboxSelected>>", lambda e: self._render())

        ttk.Button(controls, text="Actualizar", command=self.reload).pack(side="left")

        self._cargar_filtros()

    def _cargar_filtros(self):
        # Los combos de filtro usan fetch_options (helper temporal ya
        # existente) porque solo necesitan poblar opciones, igual que en el
        # formulario de publicar artículo. Nota: el filtrado real solo
        # tendrá efecto cuando get_all_articles también entregue las
        # categorías/tags de cada artículo (ver comentario en reload()).
        try:
            categorias = fetch_options("categories", "id", "name")
        except Exception:
            categorias = []
        try:
            tags = fetch_options("tags", "id", "name")
        except Exception:
            tags = []

        self.combo_categoria["values"] = ["Todas"] + [nombre for _, nombre in categorias]
        self.combo_categoria.current(0)
        self.combo_tag["values"] = ["Todos"] + [nombre for _, nombre in tags]
        self.combo_tag.current(0)

    def _build_feed_area(self):
        self.scroll_area = ScrollableFrame(self, bg=theme.CONTENT_BG)
        self.scroll_area.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self.cards_container = self.scroll_area.inner

    # ---------- datos ----------

    def reload(self):
        author_by_id = users_lookup()
        rows = safe_get_all("pkg_articles.get_all_articles")

        if rows is None:
            self._articles = None  # backend aún no listo
        else:
            # Contrato actual de get_all_articles: (id, title, date, user_id).
            # Todavía no incluye tags/categorías por artículo — eso
            # requeriría extender el procedimiento con un JOIN, algo que no
            # nos toca decidir aquí (firmas congeladas). Se dejan vacíos
            # por ahora; el filtro por categoría/tag simplemente no tendrá
            # candidatos que excluir hasta entonces.
            self._articles = [
                {
                    "id": r[0],
                    "title": r[1],
                    "date": r[2],
                    "author": author_by_id.get(r[3], f"Usuario {r[3]}"),
                    "snippet": "",
                    "tags": [],
                    "categories": [],
                }
                for r in rows
            ]
        self._render()

    # ---------- render ----------

    def _render(self):
        for widget in self.cards_container.winfo_children():
            widget.destroy()

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
            ArticleCard(self.cards_container, articulo, on_click=self.on_open_article).pack(
                fill="x", pady=6
            )

    def _render_placeholder(self, mensaje):
        tk.Label(
            self.cards_container, text=mensaje, font=("Segoe UI", 10, "italic"),
            fg="#8a8a8a", bg=theme.CONTENT_BG, pady=30,
        ).pack(fill="x")
