"""
views/new_article.py
Formulario de publicación de artículo. 
Actualizado con CustomTkinter: se reemplazan los Listbox antiguos por 
paneles con Checkboxes modernos y scroll automático.
"""

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

from db_connection import fetch_options
import theme

def abrir_form_publicar_articulo(parent, on_saved=None):
    ventana = ctk.CTkToplevel(parent, fg_color=theme.PANEL_BG)
    ventana.title("Publicar Artículo")
    ventana.geometry("500x550")
    ventana.attributes("-topmost", True)
    ventana.grab_set()

    def etiqueta(texto):
        ctk.CTkLabel(
            ventana, text=texto, text_color=theme.PANEL_FG,
            font=ctk.CTkFont(family="Helvetica", size=13, weight="bold")
        ).pack(pady=(15, 5), padx=25, anchor="w")

    etiqueta("Título:")
    entry_titulo = ctk.CTkEntry(
        ventana, fg_color=theme.ENTRY_BG, 
        border_color=theme.ENTRY_BORDER, text_color=theme.ENTRY_FG
    )
    entry_titulo.pack(padx=25, fill="x")

    etiqueta("Texto:")
    text_cuerpo = ctk.CTkTextbox(
        ventana, height=100, fg_color=theme.ENTRY_BG, 
        border_color=theme.ENTRY_BORDER, border_width=1, text_color=theme.ENTRY_FG
    )
    text_cuerpo.pack(padx=25, fill="x")

    etiqueta("Usuario autor:")
    combo_usuario = ctk.CTkComboBox(
        ventana, state="readonly",
        fg_color=theme.ENTRY_BG, border_color=theme.ENTRY_BORDER,
        text_color=theme.ENTRY_FG, dropdown_fg_color=theme.DROPDOWN_BG,
        dropdown_text_color=theme.DROPDOWN_TEXT,
        button_color=theme.ENTRY_BORDER, button_hover_color=theme.BTN_SECONDARY_HOVER
    )
    combo_usuario.pack(padx=25, fill="x")
    
    usuarios = fetch_options("users", "id", "name")
    if usuarios:
        combo_usuario.configure(values=[nombre for _, nombre in usuarios])
        combo_usuario.set(usuarios[0][1])

    etiqueta("Etiquetas:")
    combo_etiquetas = ctk.CTkComboBox(
        ventana, state="readonly",
        fg_color=theme.ENTRY_BG, border_color=theme.ENTRY_BORDER,
        text_color=theme.ENTRY_FG, dropdown_fg_color=theme.DROPDOWN_BG,
        dropdown_text_color=theme.DROPDOWN_TEXT,
        button_color=theme.ENTRY_BORDER, button_hover_color=theme.BTN_SECONDARY_HOVER
    )
    combo_etiquetas.pack(padx=25, fill="x")
    
    tags_opciones = fetch_options("tags", "id", "name")
    if tags_opciones:
        combo_etiquetas.configure(values=[nombre for _, nombre in tags_opciones])
        combo_etiquetas.set(tags_opciones[0][1])
    else:
        combo_etiquetas.set("Sin etiquetas")

    etiqueta("Categorías:")
    combo_categorias = ctk.CTkComboBox(
        ventana, state="readonly",
        fg_color=theme.ENTRY_BG, border_color=theme.ENTRY_BORDER,
        text_color=theme.ENTRY_FG, dropdown_fg_color=theme.DROPDOWN_BG,
        dropdown_text_color=theme.DROPDOWN_TEXT,
        button_color=theme.ENTRY_BORDER, button_hover_color=theme.BTN_SECONDARY_HOVER
    )
    combo_categorias.pack(padx=25, fill="x")
    
    categorias_opciones = fetch_options("categories", "id", "name")
    if categorias_opciones:
        combo_categorias.configure(values=[nombre for _, nombre in categorias_opciones])
        combo_categorias.set(categorias_opciones[0][1])
    else:
        combo_categorias.set("Sin categorías")

    def guardar():
        titulo = entry_titulo.get().strip()
        texto = text_cuerpo.get("1.0", tk.END).strip()
        usuario_nombre = combo_usuario.get()

        if not titulo or not texto or not usuario_nombre:
            messagebox.showwarning("Falta información", "Título, texto y usuario son obligatorios.")
            return

        messagebox.showinfo("Pendiente", "pkg_articles.create_article aún no está disponible.")
        if on_saved:
            on_saved()
        ventana.destroy()

    ctk.CTkButton(
        ventana, text="Publicar", command=guardar,
        fg_color=theme.SIDEBAR_SELECTED_TEXT, text_color="#131314",
        hover_color="#8AB4F8", font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
        corner_radius=8
    ).pack(pady=30)