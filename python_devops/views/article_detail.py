"""
views/article_detail.py
Vista de detalle de un artículo: texto completo + hilo de comentarios
(autor + fecha + contenido, estilo hilo de Reddit), con formulario para
agregar uno nuevo al final.

Nota: todas las Label de aquí llevan fg explícito. Sin eso, tkinter le
pone a la letra el color por defecto del sistema (que en modo oscuro de
macOS es blanco), y sobre un fondo claro el texto queda invisible. Los
comentarios usan PANEL_BG/PANEL_FG (fijos) para verse como burbujas aparte
del fondo de página, sin importar qué tan oscuro sea PAGE_BG.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import oracledb

from db_connection import fetch_options, call_procedure, fetch_article_text
from utils import safe_get_all, users_lookup
from widgets.scrollframe import ScrollableFrame
import theme


class ArticleDetailView(tk.Frame):
    def __init__(self, parent, article, on_back):
        """
        article: dict con al menos {id, title, author, date}.
        """
        super().__init__(parent, bg=theme.PAGE_BG)
        self.article = dict(article)
        self.on_back = on_back

        if not self.article.get("text") and self.article.get("id") is not None:
            try:
                self.article["text"] = fetch_article_text(self.article["id"])
            except oracledb.Error:
                self.article["text"] = None

        self._build_header()
        self._build_body_and_comments()

    def _build_header(self):
        header = tk.Frame(self, bg=theme.PAGE_BG)
        header.pack(fill="x", padx=20, pady=(16, 4))

        ttk.Button(header, text="← Volver al feed", command=self.on_back).pack(anchor="w")

        tk.Label(
            header, text=self.article.get("title", ""), font=("Segoe UI", 16, "bold"),
            bg=theme.PAGE_BG, fg=theme.PAGE_FG, anchor="w", wraplength=640, justify="left",
        ).pack(fill="x", pady=(10, 0))

        meta = f"{self.article.get('author', '')} · {self.article.get('date', '')}"
        tk.Label(header, text=meta, font=("Segoe UI", 9), fg=theme.TEXT_MUTED, bg=theme.PAGE_BG, anchor="w").pack(fill="x")

    def _build_body_and_comments(self):
        scroll = ScrollableFrame(self, bg=theme.PAGE_BG)
        scroll.pack(fill="both", expand=True, padx=20, pady=10)
        content = scroll.inner

        texto = self.article.get("text")
        tk.Label(
            content,
            text=texto or "(sin texto)",
            font=("Segoe UI", 10),
            fg=theme.PAGE_FG if texto else theme.TEXT_PLACEHOLDER,
            bg=theme.PAGE_BG, anchor="w", justify="left", wraplength=600,
        ).pack(fill="x", pady=(0, 16))

        tk.Frame(content, bg=theme.CARD_BORDER, height=1).pack(fill="x", pady=(0, 12))

        tk.Label(
            content, text="Comentarios", font=("Segoe UI", 12, "bold"),
            bg=theme.PAGE_BG, fg=theme.PAGE_FG, anchor="w",
        ).pack(fill="x", pady=(0, 8))

        self.comments_container = tk.Frame(content, bg=theme.PAGE_BG)
        self.comments_container.pack(fill="x")
        self._render_comments()

        tk.Frame(content, bg=theme.CARD_BORDER, height=1).pack(fill="x", pady=16)
        self._build_comment_form(content)

    def _render_comments(self):
        for widget in self.comments_container.winfo_children():
            widget.destroy()

        rows = safe_get_all("pkg_comments.get_by_article", [self.article.get("id")])

        if rows is None:
            tk.Label(
                self.comments_container,
                text="pendiente de conectar con pkg_comments.get_by_article",
                font=("Segoe UI", 9, "italic"), fg=theme.TEXT_PLACEHOLDER, bg=theme.PAGE_BG,
            ).pack(anchor="w", pady=10)
            return

        if not rows:
            tk.Label(
                self.comments_container, text="Todavía no hay comentarios.",
                font=("Segoe UI", 9, "italic"), fg=theme.TEXT_PLACEHOLDER, bg=theme.PAGE_BG,
            ).pack(anchor="w", pady=10)
            return

        author_by_id = users_lookup()
        # Contrato de get_by_article: id, content, creation_date, user_id
        for row in rows:
            _id, contenido, fecha, user_id = row[0], row[1], row[2], row[3]
            item = tk.Frame(self.comments_container, bg=theme.PANEL_BG)
            item.pack(fill="x", pady=4)
            meta = f"{author_by_id.get(user_id, f'Usuario {user_id}')} · {fecha}"
            tk.Label(
                item, text=meta, font=("Segoe UI", 8, "bold"), fg=theme.TEXT_MUTED,
                bg=theme.PANEL_BG, anchor="w",
            ).pack(fill="x", padx=10, pady=(6, 0))
            tk.Label(
                item, text=contenido, font=("Segoe UI", 9), fg=theme.PANEL_FG,
                bg=theme.PANEL_BG, anchor="w", justify="left", wraplength=560,
            ).pack(fill="x", padx=10, pady=(0, 6))

    def _build_comment_form(self, parent):
        tk.Label(
            parent, text="Agregar comentario", font=("Segoe UI", 10, "bold"),
            bg=theme.PAGE_BG, fg=theme.PAGE_FG, anchor="w",
        ).pack(fill="x")

        tk.Label(parent, text="Usuario:", bg=theme.PAGE_BG, fg=theme.PAGE_FG, anchor="w").pack(fill="x", pady=(6, 0))
        combo_usuario = ttk.Combobox(parent, state="readonly", width=30)
        opciones_usuario = fetch_options("users", "id", "name")
        usuarios_by_name = {nombre: uid for uid, nombre in opciones_usuario}
        combo_usuario["values"] = [nombre for _, nombre in opciones_usuario]
        if opciones_usuario:
            combo_usuario.current(0)
        combo_usuario.pack(fill="x")

        texto_comentario = tk.Text(
            parent, height=3, width=40, bg=theme.ENTRY_BG, fg=theme.ENTRY_FG,
            insertbackground=theme.ENTRY_FG,
        )
        texto_comentario.pack(fill="x", pady=(8, 8))

        def enviar():
            contenido = texto_comentario.get("1.0", tk.END).strip()
            if not contenido or not combo_usuario.get():
                messagebox.showwarning("Falta información", "Usuario y comentario son obligatorios.")
                return
            user_id = usuarios_by_name.get(combo_usuario.get())
            if user_id is None:
                messagebox.showerror("Error", "Usuario no válido.")
                return
            try:
                call_procedure(
                    "pkg_comments.add_comment",
                    [contenido, user_id, self.article.get("id")],
                )
            except oracledb.Error as e:
                messagebox.showerror("Error", str(e).split("\n")[0])
                return
            texto_comentario.delete("1.0", tk.END)
            self._render_comments()

        ttk.Button(parent, text="Comentar", command=enviar).pack(anchor="e")
