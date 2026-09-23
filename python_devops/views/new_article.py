"""
views/new_article.py
Formulario de publicación de artículo (ventana emergente). Mismo
comportamiento que la versión anterior: selección de autor/tags/categorías
siempre por nombre visible (nunca por ID), placeholder hasta que
pkg_articles.create_article tenga lógica real.

Usa la paleta de PANEL_BG/PANEL_FG (la misma de los otros formularios) para
que se vea consistente con el resto de la app en vez de heredar el gris
por defecto de la ventana del sistema.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from db_connection import fetch_options
import theme


def abrir_form_publicar_articulo(parent, on_saved=None):
    ventana = tk.Toplevel(parent, bg=theme.PANEL_BG)
    ventana.title("Publicar Artículo")
    ventana.geometry("420x520")

    def etiqueta(texto):
        tk.Label(ventana, text=texto, bg=theme.PANEL_BG, fg=theme.PANEL_FG).pack(pady=(10, 0))

    etiqueta("Título:")
    entry_titulo = tk.Entry(ventana, width=40, bg=theme.ENTRY_BG, fg=theme.ENTRY_FG, insertbackground=theme.ENTRY_FG)
    entry_titulo.pack()

    etiqueta("Texto:")
    text_cuerpo = tk.Text(ventana, width=40, height=6, bg=theme.ENTRY_BG, fg=theme.ENTRY_FG, insertbackground=theme.ENTRY_FG)
    text_cuerpo.pack()

    etiqueta("Usuario autor:")
    combo_usuario = ttk.Combobox(ventana, width=37, state="readonly")
    combo_usuario.pack()
    usuarios = fetch_options("users", "id", "name")
    combo_usuario["values"] = [nombre for _, nombre in usuarios]
    if usuarios:
        combo_usuario.current(0)

    etiqueta("Etiquetas (Ctrl/Cmd + clic para varias):")
    lista_tags = tk.Listbox(
        ventana, selectmode=tk.MULTIPLE, exportselection=False, height=4,
        bg=theme.ENTRY_BG, fg=theme.ENTRY_FG, selectbackground=theme.SIDEBAR_SELECTED_BG,
    )
    tags_opciones = fetch_options("tags", "id", "name")
    for _id, nombre in tags_opciones:
        lista_tags.insert(tk.END, nombre)
    lista_tags.pack(fill="x", padx=20)

    etiqueta("Categorías (Ctrl/Cmd + clic para varias):")
    lista_categorias = tk.Listbox(
        ventana, selectmode=tk.MULTIPLE, exportselection=False, height=3,
        bg=theme.ENTRY_BG, fg=theme.ENTRY_FG, selectbackground=theme.SIDEBAR_SELECTED_BG,
    )
    categorias_opciones = fetch_options("categories", "id", "name")
    for _id, nombre in categorias_opciones:
        lista_categorias.insert(tk.END, nombre)
    lista_categorias.pack(fill="x", padx=20)

    def guardar():
        titulo = entry_titulo.get().strip()
        texto = text_cuerpo.get("1.0", tk.END).strip()
        usuario_nombre = combo_usuario.get()

        if not titulo or not texto or not usuario_nombre:
            messagebox.showwarning("Falta información", "Título, texto y usuario son obligatorios.")
            return

        # tag_ids / categoria_ids ya quedan resueltos por si se necesitan
        # apenas create_article regrese un p_article_id real:
        # tag_ids = [tags_opciones[i][0] for i in lista_tags.curselection()]
        # categoria_ids = [categorias_opciones[i][0] for i in lista_categorias.curselection()]
        #
        # TODO: cuando pkg_articles.create_article tenga lógica real, descomentar
        # (create_article tiene un parámetro OUT p_article_id — hay que usar
        # cursor.var(...) directo, no call_procedure simple, para capturarlo):
        # user_id = dict((n, i) for i, n in usuarios)[usuario_nombre]
        # article_id = ...  # resultado del OUT de create_article
        # for tag_id in tag_ids:
        #     call_procedure("pkg_articles.assign_tag", [article_id, tag_id])
        # for cat_id in categoria_ids:
        #     call_procedure("pkg_articles.assign_category", [article_id, cat_id])

        messagebox.showinfo("Pendiente", "pkg_articles.create_article aún no está disponible.")
        if on_saved:
            on_saved()
        ventana.destroy()

    ttk.Button(ventana, text="Publicar", command=guardar).pack(pady=15)
