"""
widgets/cards.py
Tarjeta de artículo para el feed, estilo Reddit/blog: título, autor,
fecha, fragmento del texto y chips de tags/categorías.
"""

import tkinter as tk

from widgets.chips import make_chip
import theme


class ArticleCard(tk.Frame):
    def __init__(self, parent, article, on_click=None, **kwargs):
        """
        article: dict con llaves esperadas:
            id, title, author, date, snippet, tags (list[str]), categories (list[str])
        Las llaves tags/categories/snippet son opcionales: si el backend
        todavía no las provee, simplemente no se dibuja nada extra.
        on_click recibe el dict completo del artículo (no solo el id), para
        que la vista de detalle tenga lo que ya se cargó sin volver a pedirlo.
        """
        super().__init__(
            parent, bg=theme.PAGE_BG, highlightbackground=theme.CARD_BORDER,
            highlightthickness=1, bd=0, **kwargs
        )
        self.article = article
        self.on_click = on_click

        title_lbl = tk.Label(
            self, text=article.get("title", "(sin título)"),
            font=("Segoe UI", 12, "bold"), fg=theme.PAGE_FG, bg=theme.PAGE_BG,
            anchor="w", justify="left", wraplength=520,
        )
        title_lbl.pack(fill="x", padx=14, pady=(10, 2))

        meta = f"{article.get('author', 'Autor desconocido')} · {article.get('date', '')}"
        meta_lbl = tk.Label(
            self, text=meta, font=("Segoe UI", 9), fg=theme.TEXT_MUTED, bg=theme.PAGE_BG, anchor="w",
        )
        meta_lbl.pack(fill="x", padx=14)

        clickable = [self, title_lbl, meta_lbl]

        if article.get("snippet"):
            snippet_lbl = tk.Label(
                self, text=article["snippet"], font=("Segoe UI", 10), fg=theme.PAGE_FG,
                bg=theme.PAGE_BG, anchor="w", justify="left", wraplength=520,
            )
            snippet_lbl.pack(fill="x", padx=14, pady=(6, 6))
            clickable.append(snippet_lbl)

        chips_row = tk.Frame(self, bg=theme.PAGE_BG)
        chips_row.pack(fill="x", padx=14, pady=(0, 10))
        for cat in article.get("categories", []):
            make_chip(chips_row, cat, kind="category").pack(side="left", padx=(0, 4))
        for tag in article.get("tags", []):
            make_chip(chips_row, tag, kind="tag").pack(side="left", padx=(0, 4))

        for widget in clickable:
            widget.bind("<Button-1>", self._handle_click)
            widget.configure(cursor="hand2")

    def _handle_click(self, _event):
        if self.on_click:
            self.on_click(self.article)
