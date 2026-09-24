"""Vistas de administración de categorías y etiquetas.

Ambos tipos de taxonomía comparten el mismo panel visual. El nombre se
convierte en un slug URL y las operaciones de alta, edición y eliminación se
delegan a los procedimientos definidos para cada entidad.
"""

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import re
import unicodedata

from utils import safe_get_all
from db_connection import call_procedure
import oracledb
import theme


def generar_slug(texto):
    """Convierte un nombre en un slug URL estable y sin acentos."""
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    texto = texto.lower().strip()
    return re.sub(r'[-\s]+', '-', re.sub(r'[^a-z0-9\s-]', '', texto))

class _TaxonomyPanel(ctk.CTkFrame):
    """Panel reutilizable para listar y administrar una taxonomía."""

    def __init__(self, parent, titulo, proc_get_all, proc_insert, proc_update, proc_delete):
        super().__init__(parent, fg_color="transparent")
        self.proc_get_all = proc_get_all
        self.proc_insert = proc_insert
        self.proc_update = proc_update
        self.proc_delete = proc_delete
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

        ctk.CTkButton(
            form_col, text="Guardar", command=self.guardar,
            fg_color=theme.BTN_SECONDARY_BG, hover_color=theme.BTN_SECONDARY_HOVER,
            text_color=theme.BTN_SECONDARY_FG, border_width=1,
            border_color=theme.BTN_SECONDARY_BORDER, corner_radius=6
        ).pack(pady=25, padx=16, fill="x")

        self.reload()

    def guardar(self):
        """Valida el nombre, genera el slug y crea el registro."""
        nombre = self.entry_nombre.get().strip()
        if not nombre:
            messagebox.showwarning("Falta información", "El nombre es obligatorio.")
            return
            
        url = generar_slug(nombre)
        
        try:
            call_procedure(self.proc_insert, [nombre, url])
        except oracledb.Error as e:
            messagebox.showerror("Error", str(e).split("\n")[0])
            return
            
        self.entry_nombre.delete(0, tk.END)
        self.reload()
        messagebox.showinfo("Listo", f"{self.titulo} creada exitosamente.")

    def reload(self):
        """Actualiza la lista y conserva un estado vacío comprensible."""
        for widget in self.scroll.winfo_children():
            widget.destroy()
            
        self.update_idletasks()

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

            info_frame = ctk.CTkFrame(item, fg_color="transparent")
            info_frame.pack(side="left", fill="both", expand=True)

            ctk.CTkLabel(
                info_frame, text=nombre, font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                text_color=theme.PANEL_FG
            ).pack(fill="x", padx=15, pady=(10, 0), anchor="w")

            if url:
                ctk.CTkLabel(
                    info_frame, text=url, font=ctk.CTkFont(family="Segoe UI", size=12),
                    text_color=theme.TEXT_MUTED
                ).pack(fill="x", padx=15, pady=(0, 10), anchor="w")
            else:
                ctk.CTkFrame(info_frame, fg_color="transparent", height=10).pack()

            ctk.CTkButton(
                item, text="✖", width=30, fg_color="#dc3545", hover_color="#c82333",
                command=lambda id=_id, n=nombre: self.eliminar(id, n)
            ).pack(side="right", padx=(2, 15))
            
            ctk.CTkButton(
                item, text="✎", width=30, fg_color="#ffc107", hover_color="#e0a800", text_color="black",
                command=lambda id=_id, n=nombre: self.editar(id, n)
            ).pack(side="right", padx=2)

    def editar(self, item_id, current_name):
        """Solicita un nuevo nombre y actualiza el registro seleccionado."""
        dialog = ctk.CTkInputDialog(text=f"Nuevo nombre para '{current_name}':", title="Editar")
        nuevo_nombre = dialog.get_input()
        
        if nuevo_nombre and nuevo_nombre.strip() != current_name:
            nuevo_slug = generar_slug(nuevo_nombre)
            try:
                call_procedure(self.proc_update, [item_id, nuevo_nombre.strip(), nuevo_slug])
                self.reload()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo actualizar: {e}")

    def eliminar(self, item_id, item_name):
        """Confirma y elimina el registro seleccionado."""
        confirm = messagebox.askyesno("Confirmar", f"¿Seguro que deseas eliminar '{item_name}'?")
        if confirm:
            try:
                call_procedure(self.proc_delete, [item_id])
                self.reload()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar. Probablemente esté en uso.\nDetalles: {e}")

class CategoriesView(ctk.CTkFrame):
    """Vista de administración de categorías."""
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
            "pkg_categories.update_category",
            "pkg_categories.delete_category"
        )
        panel.pack(fill="both", expand=True, padx=20, pady=(0, 20))


class TagsView(ctk.CTkFrame):
    """Vista de administración de etiquetas."""
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
            "pkg_tags.update_tag",
            "pkg_tags.delete_tag"
        )
        panel.pack(fill="both", expand=True, padx=20, pady=(0, 20))