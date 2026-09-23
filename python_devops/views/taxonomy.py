"""
views/taxonomy.py
Vista combinada de Categorías y Etiquetas (dos pestañas), cada una con
lista + formulario de creación. Antes eran 2 de los 8 botones sueltos.

Nota: todas las Label de aquí llevan fg explícito. Sin eso, tkinter le
pone a la letra el color por defecto del sistema (que en modo oscuro de
macOS es blanco), y sobre un fondo claro el texto queda invisible.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from utils import safe_get_all
from widgets.scrollframe import ScrollableFrame
import theme


class _TaxonomyPanel(tk.Frame):
    """Panel genérico reutilizado para la pestaña de Categorías y la de Etiquetas."""

    def __init__(self, parent, titulo, proc_get_all, proc_insert):
        super().__init__(parent, bg=theme.PAGE_BG)
        self.proc_get_all = proc_get_all
        self.proc_insert = proc_insert

        body = tk.Frame(self, bg=theme.PAGE_BG)
        body.pack(fill="both", expand=True, padx=20, pady=16)

        list_col = tk.Frame(body, bg=theme.PAGE_BG)
        list_col.pack(side="left", fill="both", expand=True)
        self.scroll = ScrollableFrame(list_col, bg=theme.PAGE_BG)
        self.scroll.pack(fill="both", expand=True)
        self.list_container = self.scroll.inner

        # form_col usa PANEL_BG/PANEL_FG a propósito: es un color fijo, no
        # ligado a PAGE_BG, para que el panel siempre se note como una
        # tarjeta aparte, sin importar qué tan oscuro sea el fondo de página.
        form_col = tk.Frame(
            body, bg=theme.PANEL_BG, highlightbackground=theme.PANEL_BORDER,
            highlightthickness=1, padx=16, pady=16,
        )
        form_col.pack(side="right", fill="y", padx=(16, 0))

        tk.Label(
            form_col, text=f"Nueva {titulo.lower()}", font=("Segoe UI", 11, "bold"),
            bg=theme.PANEL_BG, fg=theme.PANEL_FG,
        ).pack(anchor="w")

        tk.Label(form_col, text="Nombre:", bg=theme.PANEL_BG, fg=theme.PANEL_FG).pack(anchor="w", pady=(10, 0))
        entry_nombre = tk.Entry(form_col, width=26, bg=theme.ENTRY_BG, fg=theme.ENTRY_FG, insertbackground=theme.ENTRY_FG)
        entry_nombre.pack()

        tk.Label(form_col, text="URL:", bg=theme.PANEL_BG, fg=theme.PANEL_FG).pack(anchor="w", pady=(10, 0))
        entry_url = tk.Entry(form_col, width=26, bg=theme.ENTRY_BG, fg=theme.ENTRY_FG, insertbackground=theme.ENTRY_FG)
        entry_url.pack()

        def guardar():
            nombre = entry_nombre.get().strip()
            if not nombre:
                messagebox.showwarning("Falta información", "El nombre es obligatorio.")
                return
            # TODO: cuando el procedimiento real exista, descomentar:
            # call_procedure(self.proc_insert, [nombre, entry_url.get().strip()])
            # self.reload()
            messagebox.showinfo("Pendiente", f"{self.proc_insert} aún no está disponible.")
            entry_nombre.delete(0, tk.END)
            entry_url.delete(0, tk.END)

        ttk.Button(form_col, text="Guardar", command=guardar).pack(pady=15)

        self.reload()

    def reload(self):
        for widget in self.list_container.winfo_children():
            widget.destroy()

        rows = safe_get_all(self.proc_get_all)

        if rows is None:
            tk.Label(
                self.list_container, text=f"pendiente de conectar con {self.proc_get_all}",
                font=("Segoe UI", 9, "italic"), fg=theme.TEXT_PLACEHOLDER, bg=theme.PAGE_BG,
            ).pack(anchor="w", pady=10)
            return
        if not rows:
            tk.Label(
                self.list_container, text="Todavía no hay elementos.",
                font=("Segoe UI", 9, "italic"), fg=theme.TEXT_PLACEHOLDER, bg=theme.PAGE_BG,
            ).pack(anchor="w", pady=10)
            return

        for row in rows:
            _id, nombre, url = row[0], row[1], row[2]
            item = tk.Frame(self.list_container, bg=theme.PANEL_BG)
            item.pack(fill="x", pady=3)
            tk.Label(
                item, text=nombre, font=("Segoe UI", 10, "bold"),
                bg=theme.PANEL_BG, fg=theme.PANEL_FG, anchor="w",
            ).pack(fill="x", padx=10, pady=(6, 0))
            if url:
                tk.Label(
                    item, text=url, font=("Segoe UI", 9),
                    fg=theme.TEXT_MUTED, bg=theme.PANEL_BG, anchor="w",
                ).pack(fill="x", padx=10, pady=(0, 6))


class TaxonomyView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=theme.PAGE_BG)

        tk.Label(
            self, text="Categorías / Etiquetas", font=("Segoe UI", 14, "bold"),
            bg=theme.PAGE_BG, fg=theme.PAGE_FG,
        ).pack(anchor="w", padx=20, pady=(16, 8))

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=(0, 16))

        # Firmas exactas del contrato: pkg_categories.get_all / pkg_tags.get_all
        categorias = _TaxonomyPanel(notebook, "Categoría", "pkg_categories.get_all", "pkg_categories.insert_category")
        etiquetas = _TaxonomyPanel(notebook, "Etiqueta", "pkg_tags.get_all", "pkg_tags.insert_tag")

        notebook.add(categorias, text="Categorías")
        notebook.add(etiquetas, text="Etiquetas")
