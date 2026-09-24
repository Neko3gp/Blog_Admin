"""
views/users.py
Vista de usuarios migrada a CustomTkinter. 
Lista interactiva + formulario de creación integrado como panel lateral.
"""

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

from utils import safe_get_all
from db_connection import call_procedure
import oracledb
import theme


class UsersView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=theme.PAGE_BG)

        ctk.CTkLabel(
            self, text="Usuarios", 
            font=ctk.CTkFont(family="Helvetica", size=22, weight="bold"),
            text_color=theme.PAGE_FG
        ).pack(anchor="w", padx=20, pady=(20, 10))

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        list_col = ctk.CTkFrame(body, fg_color="transparent")
        list_col.pack(side="left", fill="both", expand=True)
        
        # ScrollableFrame moderno: oculta la barra automáticamente si no es necesaria
        self.scroll = ctk.CTkScrollableFrame(
            list_col, fg_color="transparent",
            scrollbar_button_color=theme.SCROLLBAR_FG,
            scrollbar_button_hover_color=theme.SCROLLBAR_HOVER
        )
        self.scroll.pack(fill="both", expand=True)

        form_col = ctk.CTkFrame(
            body, fg_color=theme.PANEL_BG, border_color=theme.PANEL_BORDER, 
            border_width=1, corner_radius=10
        )
        form_col.pack(side="right", fill="y", padx=(16, 0), ipadx=16, ipady=16)
        
        self._build_form(form_col)
        self.reload()

    def _build_form(self, parent):
        ctk.CTkLabel(
            parent, text="Nuevo usuario", 
            font=ctk.CTkFont(family="Helvetica", size=15, weight="bold"),
            text_color=theme.PANEL_FG
        ).pack(anchor="w", padx=16, pady=(16, 10))

        ctk.CTkLabel(
            parent, text="Nombre:", text_color=theme.PANEL_FG,
            font=ctk.CTkFont(family="Helvetica", size=13)
        ).pack(anchor="w", padx=16, pady=(10, 0))
        
        entry_nombre = ctk.CTkEntry(
            parent, width=220, fg_color=theme.ENTRY_BG, 
            border_color=theme.ENTRY_BORDER, text_color=theme.ENTRY_FG
        )
        entry_nombre.pack(padx=16, pady=(0, 10))

        ctk.CTkLabel(
            parent, text="Email:", text_color=theme.PANEL_FG,
            font=ctk.CTkFont(family="Helvetica", size=13)
        ).pack(anchor="w", padx=16, pady=(10, 0))
        
        entry_email = ctk.CTkEntry(
            parent, width=220, fg_color=theme.ENTRY_BG, 
            border_color=theme.ENTRY_BORDER, text_color=theme.ENTRY_FG
        )
        entry_email.pack(padx=16, pady=(0, 10))

        def guardar():
            nombre = entry_nombre.get().strip()
            email = entry_email.get().strip()
            if not nombre or not email:
                messagebox.showwarning("Falta información", "Nombre y email son obligatorios.")
                return
            try:
                call_procedure("pkg_users.insert_user", [nombre, email])
            except oracledb.Error as e:
                messagebox.showerror("Error", str(e).split("\n")[0])
                return
            entry_nombre.delete(0, tk.END)
            entry_email.delete(0, tk.END)
            self.reload()
            messagebox.showinfo("Listo", "Usuario creado.")

        ctk.CTkButton(
            parent, text="Guardar", command=guardar,
            fg_color=theme.BTN_SECONDARY_BG, hover_color=theme.BTN_SECONDARY_HOVER,
            text_color=theme.BTN_SECONDARY_FG, border_width=1, 
            border_color=theme.BTN_SECONDARY_BORDER, corner_radius=6
        ).pack(pady=20)

    def reload(self):
        for widget in self.scroll.winfo_children():
            widget.destroy()

        rows = safe_get_all("pkg_users.get_all_users")

        if rows is None:
            ctk.CTkLabel(
                self.scroll, text="pendiente de conectar con pkg_users.get_all_users",
                font=ctk.CTkFont(family="Segoe UI", size=12, slant="italic"), 
                text_color=theme.TEXT_PLACEHOLDER
            ).pack(anchor="w", pady=10)
            return

        if not rows:
            ctk.CTkLabel(
                self.scroll, text="Todavía no hay usuarios.",
                font=ctk.CTkFont(family="Segoe UI", size=12, slant="italic"), 
                text_color=theme.TEXT_PLACEHOLDER
            ).pack(anchor="w", pady=10)
            return

        for row in rows:
            _id, nombre, email = row[0], row[1], row[2]
            
            # Tarjeta de usuario moderna
            item = ctk.CTkFrame(self.scroll, fg_color=theme.ENTRY_BG, corner_radius=6)
            item.pack(fill="x", pady=4)
            
            ctk.CTkLabel(
                item, text=nombre, font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                text_color=theme.PANEL_FG
            ).pack(fill="x", padx=12, pady=(8, 0), anchor="w")
            
            ctk.CTkLabel(
                item, text=email, font=ctk.CTkFont(family="Segoe UI", size=11),
                text_color=theme.TEXT_MUTED
            ).pack(fill="x", padx=12, pady=(0, 8), anchor="w")