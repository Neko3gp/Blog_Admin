"""
views/taxonomy.py
Vista combinada de Categorías y Etiquetas, migrada a CustomTkinter 
para usar campos sin bordes blancos, barras de scroll dinámicas 
y botones modernos.
"""

"""
Utiliza CTkSegmentedButton para evitar errores de renderizado de pestañas
e incluye estados vacíos explícitos cuando la base de datos no tiene registros.
"""

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

from utils import safe_get_all
import theme

class _TaxonomyPanel(ctk.CTkFrame):
    def __init__(self, parent, titulo, proc_get_all, proc_insert):
        super().__init__(parent, fg_color="transparent")
        self.proc_get_all = proc_get_all
        self.proc_insert = proc_insert
        self.titulo = titulo

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, pady=10)

        # Columna izquierda: Lista de elementos
        list_col = ctk.CTkFrame(body, fg_color="transparent")
        list_col.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        self.scroll = ctk.CTkScrollableFrame(
            list_col, fg_color="transparent",
            scrollbar_button_color=theme.SCROLLBAR_FG,
            scrollbar_button_hover_color=theme.SCROLLBAR_HOVER
        )
        self.scroll.pack(fill="both", expand=True)

        # Columna derecha: Formulario de creación (name, url)
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
        if not nombre:
            messagebox.showwarning("Falta información", "El nombre es obligatorio.")
            return
        
        messagebox.showinfo("Pendiente", f"{self.proc_insert} aún no está disponible en BD.")
        self.entry_nombre.delete(0, tk.END)
        self.entry_url.delete(0, tk.END)

    def reload(self):
        for widget in self.scroll.winfo_children():
            widget.destroy()

        rows = safe_get_all(self.proc_get_all)

        # Renderizado de la leyenda cuando no hay registros en la BD
        if not rows:
            placeholder_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
            placeholder_frame.pack(fill="both", expand=True, pady=60)
            
            # Si rows es [] significa que conectó pero está vacío. Si es None, falló la conexión.
            mensaje = f"No hay {self.titulo.lower()}s registradas en la base de datos." if rows == [] else f"Esperando conexión con {self.proc_get_all}..."
            
            ctk.CTkLabel(
                placeholder_frame, text=mensaje,
                font=ctk.CTkFont(family="Segoe UI", size=14, slant="italic"), 
                text_color=theme.TEXT_PLACEHOLDER
            ).pack()
            return

        # Renderizado de los registros si existen
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


class TaxonomyView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=theme.PAGE_BG)

        # Encabezado con título y menú de selección
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            header, text="Categorías y Etiquetas", 
            font=ctk.CTkFont(family="Helvetica", size=22, weight="bold"),
            text_color=theme.PAGE_FG
        ).pack(side="left")

        self.current_view = ctk.StringVar(value="Categorías")
        self.seg_button = ctk.CTkSegmentedButton(
            header, values=["Categorías", "Etiquetas"],
            variable=self.current_view,
            command=self.switch_tab,
            fg_color=theme.ENTRY_BG,
            selected_color=theme.SIDEBAR_SELECTED_BG,
            selected_hover_color=theme.SIDEBAR_HOVER_BG,
            unselected_color=theme.ENTRY_BG,
            unselected_hover_color=theme.BTN_SECONDARY_HOVER,
            text_color=theme.PAGE_FG
        )
        self.seg_button.pack(side="right")

        # Contenedor principal que alternará los paneles
        self.panel_container = ctk.CTkFrame(self, fg_color="transparent")
        self.panel_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Instanciar ambos paneles cumpliendo el contrato de la BD
        self.panel_categorias = _TaxonomyPanel(self.panel_container, "Categoría", "pkg_categories.get_all", "pkg_categories.insert_category")
        self.panel_etiquetas = _TaxonomyPanel(self.panel_container, "Etiqueta", "pkg_tags.get_all", "pkg_tags.insert_tag")
        
        # Mostrar panel por defecto
        self.panel_categorias.pack(fill="both", expand=True)

    def switch_tab(self, value):
        self.panel_categorias.pack_forget()
        self.panel_etiquetas.pack_forget()
        
        if value == "Categorías":
            self.panel_categorias.pack(fill="both", expand=True)
        else:
            self.panel_etiquetas.pack(fill="both", expand=True)