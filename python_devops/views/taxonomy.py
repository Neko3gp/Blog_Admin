"""
views/taxonomy.py
Vistas separadas de Categorías y Etiquetas.
"""

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

from utils import safe_get_all
from db_connection import call_procedure
import oracledb
import theme


class _TaxonomyPanel(ctk.CTkFrame):
    def __init__(self, parent, titulo, proc_get_all, proc_insert):
        super().__init__(parent, fg_color="transparent")
        self.proc_get_all = proc_get_all
        self.proc_insert = proc_insert
        self.titulo = titulo

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, pady=10)

        list_col = ctk.CTkFrame(body, fg_color="transparent")
        list_col.pack(side="left", fill="both", expand=True, padx=(0, 15))

        self.scroll = ctk.CTkScrollableFrame(
            list_col, fg_color="transparent",
            scrollbar_button_color=theme.SCROLLBAR_FG,
            scrollbar_button_hover_color=theme.SCROLLBAR_HOVER
        )
        self.scroll.pack(fill="both", expand=True)

        form_col = ctk.CTkFrame(
            body, fg_color=theme.PANEL_BG, border_color=theme.PANEL_BORDER,
            border_width=1, corner_radius=10, width=320
        )
        form_col.pack_propagate(False)
        form_col.pack(side="right", fill="y", ipadx=10, ipady=10)

        ctk.CTkLabel(
            form_col, text=f"Nueva {self.titulo.lower()}",
            font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"),
            text_color=theme.PANEL_FG
        ).pack(anchor="w", padx=16, pady=(16, 10))

        ctk.CTkLabel(
            form_col, text="Nombre:", text_color=theme.PANEL_FG,
            font=ctk.CTkFont(family="Helvetica", size=13)
        ).pack(anchor="w", padx=16, pady=(10, 0))

        self.entry_nombre = ctk.CTkEntry(
            form_col, fg_color=theme.ENTRY_BG,
            border_color=theme.ENTRY_BORDER, text_color=theme.ENTRY_FG
        )
        self.entry_nombre.pack(fill="x", padx=16, pady=(0, 10))

        ctk.CTkLabel(
            form_col, text="URL:", text_color=theme.PANEL_FG,
            font=ctk.CTkFont(family="Helvetica", size=13)
        ).pack(anchor="w", padx=16, pady=(10, 0))

        self.entry_url = ctk.CTkEntry(
            form_col, fg_color=theme.ENTRY_BG,
            border_color=theme.ENTRY_BORDER, text_color=theme.ENTRY_FG
        )
        self.entry_url.pack(fill="x", padx=16, pady=(0, 10))

        ctk.CTkButton(
            form_col, text="Guardar", command=self.guardar,
            fg_color=theme.BTN_SECONDARY_BG, hover_color=theme.BTN_SECONDARY_HOVER,
            text_color=theme.BTN_SECONDARY_FG, border_width=1,
            border_color=theme.BTN_SECONDARY_BORDER, corner_radius=6
        ).pack(pady=25, padx=16, fill="x")

        self.reload()

    def guardar(self):
        nombre = self.entry_nombre.get().strip()
        url = self.entry_url.get().strip()
        if not nombre:
            messagebox.showwarning("Falta información", "El nombre es obligatorio.")
            return
        try:
            call_procedure(self.proc_insert, [nombre, url or None])
        except oracledb.Error as e:
            messagebox.showerror("Error", str(e).split("\n")[0])
            return
        self.entry_nombre.delete(0, tk.END)
        self.entry_url.delete(0, tk.END)
        self.reload()
        messagebox.showinfo("Listo", f"{self.titulo} creada.")

    def reload(self):
        for widget in self.scroll.winfo_children():
            widget.destroy()

        rows = safe_get_all(self.proc_get_all)

        if not rows:
            placeholder_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
            placeholder_frame.pack(fill="both", expand=True, pady=60)

            mensaje = (
                f"No hay {self.titulo.lower()}s registradas en la base de datos."
                if rows == []
                else f"Esperando conexión con {self.proc_get_all}..."
            )

            ctk.CTkLabel(
                placeholder_frame, text=mensaje,
                font=ctk.CTkFont(family="Segoe UI", size=14, slant="italic"),
                text_color=theme.TEXT_PLACEHOLDER
            ).pack()
            return

        for row in rows:
            _id, nombre, url = row[0], row[1], row[2]
            item = ctk.CTkFrame(self.scroll, fg_color=theme.ENTRY_BG, corner_radius=6)
            item.pack(fill="x", pady=4, padx=2)

            ctk.CTkLabel(
                item, text=nombre, font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                text_color=theme.PANEL_FG
            ).pack(fill="x", padx=15, pady=(10, 0), anchor="w")

            if url:
                ctk.CTkLabel(
                    item, text=url, font=ctk.CTkFont(family="Segoe UI", size=12),
                    text_color=theme.TEXT_MUTED
                ).pack(fill="x", padx=15, pady=(0, 10), anchor="w")
            else:
                ctk.CTkFrame(item, fg_color="transparent", height=10).pack()


class CategoriesView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=theme.PAGE_BG)

        ctk.CTkLabel(
            self, text="Categorías",
            font=ctk.CTkFont(family="Helvetica", size=22, weight="bold"),
            text_color=theme.PAGE_FG
        ).pack(anchor="w", padx=20, pady=(20, 10))

        panel = _TaxonomyPanel(
            self, "Categoría",
            "pkg_categories.get_all",
            "pkg_categories.insert_category",
        )
        panel.pack(fill="both", expand=True, padx=20, pady=(0, 20))


class TagsView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=theme.PAGE_BG)

        ctk.CTkLabel(
            self, text="Etiquetas",
            font=ctk.CTkFont(family="Helvetica", size=22, weight="bold"),
            text_color=theme.PAGE_FG
        ).pack(anchor="w", padx=20, pady=(20, 10))

        panel = _TaxonomyPanel(
            self, "Etiqueta",
            "pkg_tags.get_all",
            "pkg_tags.insert_tag",
        )
        panel.pack(fill="both", expand=True, padx=20, pady=(0, 20))
