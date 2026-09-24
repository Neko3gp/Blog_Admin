"""
views/article_detail.py
Vista de detalle de un artículo: texto completo + hilo de comentarios
(autor + fecha + contenido, estilo hilo de Reddit), con formulario para
agregar uno nuevo al final.

"""

"""
Vista de detalle de un artículo migrada a CustomTkinter.
Incluye hilo de comentarios y formulario con componentes modernos.

Vista de detalle de un artículo con formulario de comentarios ajustado.
"""

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import oracledb

from db_connection import fetch_options, call_procedure, fetch_article_text
from utils import safe_get_all, users_lookup
import theme


class ArticleDetailView(ctk.CTkFrame):
    def __init__(self, parent, article, on_back):
        super().__init__(parent, fg_color=theme.PAGE_BG)
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
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(16, 4))

        ctk.CTkButton(
            header, text="← Volver al feed", command=self.on_back,
            fg_color="transparent", text_color=theme.SIDEBAR_SELECTED_TEXT,
            hover_color=theme.SIDEBAR_HOVER_BG, font=ctk.CTkFont(family="Helvetica", size=13, weight="bold"),
            width=120, anchor="w"
        ).pack(anchor="w", pady=(0, 10))

        ctk.CTkLabel(
            header, text=self.article.get("title", ""), 
            font=ctk.CTkFont(family="Helvetica", size=22, weight="bold"),
            text_color=theme.PAGE_FG, anchor="w", wraplength=640, justify="left"
        ).pack(fill="x")

        meta = f"{self.article.get('author', '')} · {self.article.get('date', '')}"
        ctk.CTkLabel(
            header, text=meta, font=ctk.CTkFont(family="Helvetica", size=12), 
            text_color=theme.TEXT_MUTED, anchor="w"
        ).pack(fill="x", pady=(2, 0))

    def _build_body_and_comments(self):
        self.scroll = ctk.CTkScrollableFrame(
            self, fg_color="transparent",
            scrollbar_button_color=theme.SCROLLBAR_FG,
            scrollbar_button_hover_color=theme.SCROLLBAR_HOVER
        )
        self.scroll.pack(fill="both", expand=True, padx=15, pady=(5, 15))

        texto = self.article.get("text")
        ctk.CTkLabel(
            self.scroll,
            text=texto or "(sin texto)",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=theme.PAGE_FG if texto else theme.TEXT_PLACEHOLDER,
            anchor="w", justify="left", wraplength=700
        ).pack(fill="x", padx=5, pady=(10, 20))

        ctk.CTkFrame(self.scroll, fg_color=theme.CARD_BORDER, height=1).pack(fill="x", padx=5, pady=(0, 20))

        ctk.CTkLabel(
            self.scroll, text="Comentarios", 
            font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"),
            text_color=theme.PAGE_FG, anchor="w"
        ).pack(fill="x", padx=5, pady=(0, 15))

        self.comments_container = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self.comments_container.pack(fill="x", padx=5)
        self._render_comments()

        ctk.CTkFrame(self.scroll, fg_color=theme.CARD_BORDER, height=1).pack(fill="x", padx=5, pady=20)
        self._build_comment_form(self.scroll)

    def _render_comments(self):
        for widget in self.comments_container.winfo_children():
            widget.destroy()

        rows = safe_get_all("pkg_comments.get_by_article", [self.article.get("id")])

        if rows is None:
            ctk.CTkLabel(
                self.comments_container,
                text="Pendiente de conectar con pkg_comments.get_by_article...",
                font=ctk.CTkFont(family="Segoe UI", size=13, slant="italic"), 
                text_color=theme.TEXT_PLACEHOLDER, anchor="w"
            ).pack(fill="x", pady=10)
            return

        if not rows:
            ctk.CTkLabel(
                self.comments_container, text="Todavía no hay comentarios.",
                font=ctk.CTkFont(family="Segoe UI", size=13, slant="italic"), 
                text_color=theme.TEXT_PLACEHOLDER, anchor="w"
            ).pack(fill="x", pady=10)
            return

        author_by_id = users_lookup()
        
        for row in rows:
            _id, contenido, fecha, user_id = row[0], row[1], row[2], row[3]
            item = ctk.CTkFrame(self.comments_container, fg_color=theme.PANEL_BG, corner_radius=10)
            item.pack(fill="x", pady=6)
            
            meta = f"{author_by_id.get(user_id, f'Usuario {user_id}')} · {fecha}"
            ctk.CTkLabel(
                item, text=meta, font=ctk.CTkFont(family="Helvetica", size=11, weight="bold"), 
                text_color=theme.TEXT_MUTED, anchor="w"
            ).pack(fill="x", padx=15, pady=(10, 2))
            
            ctk.CTkLabel(
                item, text=contenido, font=ctk.CTkFont(family="Segoe UI", size=13), 
                text_color=theme.PANEL_FG, anchor="w", justify="left", wraplength=650
            ).pack(fill="x", padx=15, pady=(0, 10))

    def _build_comment_form(self, parent):
        form_container = ctk.CTkFrame(parent, fg_color="transparent")
        form_container.pack(fill="x", padx=5, pady=(0, 20))

        # Fila de selección de usuario
        user_row = ctk.CTkFrame(form_container, fg_color="transparent")
        user_row.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            user_row, text="Usuario:", text_color=theme.PAGE_FG, 
            font=ctk.CTkFont(family="Helvetica", size=13, weight="bold")
        ).pack(side="left", padx=(0, 10))
        
        combo_usuario = ctk.CTkComboBox(
            user_row, state="readonly", width=260,
            fg_color=theme.ENTRY_BG, border_color=theme.ENTRY_BORDER,
            text_color=theme.ENTRY_FG, dropdown_fg_color=theme.DROPDOWN_BG,
            dropdown_text_color=theme.DROPDOWN_TEXT,
            button_color=theme.ENTRY_BORDER, button_hover_color=theme.BTN_SECONDARY_HOVER
        )
        
        opciones_usuario = fetch_options("users", "id", "name")
        usuarios_by_name = {nombre: uid for uid, nombre in opciones_usuario}
        if opciones_usuario:
            combo_usuario.configure(values=[nombre for _, nombre in opciones_usuario])
            combo_usuario.set(opciones_usuario[0][1])
        combo_usuario.pack(side="left")

        # Etiqueta posicionada directamente encima del cuadro de texto
        ctk.CTkLabel(
            form_container, text="Agregar comentario:", 
            font=ctk.CTkFont(family="Helvetica", size=13, weight="bold"),
            text_color=theme.PAGE_FG, anchor="w"
        ).pack(fill="x", pady=(5, 5))

        texto_comentario = ctk.CTkTextbox(
            form_container, height=80, fg_color=theme.ENTRY_BG, 
            border_color=theme.ENTRY_BORDER, border_width=1, text_color=theme.ENTRY_FG
        )
        texto_comentario.pack(fill="x", pady=(0, 12))

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
                messagebox.showerror("Error de Base de Datos", str(e).split("\n")[0])
                return
            except Exception as e:
                messagebox.showerror("Error", str(e))
                return

            texto_comentario.delete("1.0", tk.END)
            self._render_comments()

        ctk.CTkButton(
            form_container, text="Comentar", command=enviar,
            fg_color=theme.SIDEBAR_SELECTED_BG, hover_color=theme.SIDEBAR_HOVER_BG,
            text_color=theme.SIDEBAR_SELECTED_TEXT, font=ctk.CTkFont(family="Helvetica", size=13, weight="bold"),
            corner_radius=6, width=120
        ).pack(anchor="e")