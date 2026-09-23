"""
views/users.py
Vista de usuarios: lista + formulario de creación, reemplazando las
ventanas emergentes sueltas por un panel embebido en la navegación
principal.

Nota: todas las Label de aquí llevan fg explícito. Sin eso, tkinter le
pone a la letra el color por defecto del sistema (que en modo oscuro de
macOS es blanco), y sobre un fondo claro el texto queda invisible.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from utils import safe_get_all
from widgets.scrollframe import ScrollableFrame
import theme


class UsersView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=theme.PAGE_BG)

        tk.Label(
            self, text="Usuarios", font=("Segoe UI", 14, "bold"),
            bg=theme.PAGE_BG, fg=theme.PAGE_FG,
        ).pack(anchor="w", padx=20, pady=(16, 8))

        body = tk.Frame(self, bg=theme.PAGE_BG)
        body.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        list_col = tk.Frame(body, bg=theme.PAGE_BG)
        list_col.pack(side="left", fill="both", expand=True)
        self.scroll = ScrollableFrame(list_col, bg=theme.PAGE_BG)
        self.scroll.pack(fill="both", expand=True)
        self.list_container = self.scroll.inner

        # form_col usa PANEL_BG/PANEL_FG a propósito: es un color fijo, no
        # ligado a PAGE_BG, para que el panel siempre se note como una
        # tarjeta aparte, sin importar qué tan oscuro sea el fondo de página.
        form_col = tk.Frame(body, bg=theme.PANEL_BG, highlightbackground=theme.PANEL_BORDER, highlightthickness=1, padx=16, pady=16)
        form_col.pack(side="right", fill="y", padx=(16, 0))
        self._build_form(form_col)

        self.reload()

    def _build_form(self, parent):
        tk.Label(
            parent, text="Nuevo usuario", font=("Segoe UI", 11, "bold"),
            bg=theme.PANEL_BG, fg=theme.PANEL_FG,
        ).pack(anchor="w")

        tk.Label(parent, text="Nombre:", bg=theme.PANEL_BG, fg=theme.PANEL_FG).pack(anchor="w", pady=(10, 0))
        entry_nombre = tk.Entry(parent, width=28, bg=theme.ENTRY_BG, fg=theme.ENTRY_FG, insertbackground=theme.ENTRY_FG)
        entry_nombre.pack()

        tk.Label(parent, text="Email:", bg=theme.PANEL_BG, fg=theme.PANEL_FG).pack(anchor="w", pady=(10, 0))
        entry_email = tk.Entry(parent, width=28, bg=theme.ENTRY_BG, fg=theme.ENTRY_FG, insertbackground=theme.ENTRY_FG)
        entry_email.pack()

        def guardar():
            nombre = entry_nombre.get().strip()
            email = entry_email.get().strip()
            if not nombre or not email:
                messagebox.showwarning("Falta información", "Nombre y email son obligatorios.")
                return
            # TODO: cuando pkg_users.insert_user tenga lógica real, descomentar:
            # call_procedure("pkg_users.insert_user", [nombre, email])
            # self.reload()
            messagebox.showinfo("Pendiente", "pkg_users.insert_user aún no está disponible.")
            entry_nombre.delete(0, tk.END)
            entry_email.delete(0, tk.END)

        ttk.Button(parent, text="Guardar", command=guardar).pack(pady=15)

    def reload(self):
        for widget in self.list_container.winfo_children():
            widget.destroy()

        rows = safe_get_all("pkg_users.get_all_users")

        if rows is None:
            tk.Label(
                self.list_container, text="pendiente de conectar con pkg_users.get_all_users",
                font=("Segoe UI", 9, "italic"), fg=theme.TEXT_PLACEHOLDER, bg=theme.PAGE_BG,
            ).pack(anchor="w", pady=10)
            return

        if not rows:
            tk.Label(
                self.list_container, text="Todavía no hay usuarios.",
                font=("Segoe UI", 9, "italic"), fg=theme.TEXT_PLACEHOLDER, bg=theme.PAGE_BG,
            ).pack(anchor="w", pady=10)
            return

        for row in rows:
            _id, nombre, email = row[0], row[1], row[2]
            item = tk.Frame(self.list_container, bg=theme.PANEL_BG)
            item.pack(fill="x", pady=3)
            tk.Label(
                item, text=nombre, font=("Segoe UI", 10, "bold"),
                bg=theme.PANEL_BG, fg=theme.PANEL_FG, anchor="w",
            ).pack(fill="x", padx=10, pady=(6, 0))
            tk.Label(
                item, text=email, font=("Segoe UI", 9),
                fg=theme.TEXT_MUTED, bg=theme.PANEL_BG, anchor="w",
            ).pack(fill="x", padx=10, pady=(0, 6))
