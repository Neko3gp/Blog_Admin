"""
main.py
Interfaz de escritorio (tkinter) del Administrador de Blog.

Reemplaza al menú de consola: la lógica de conexión no cambió,
sigue viviendo en db_connection.py. Aquí solo cambia la capa visual.

Cada función de acción está marcada como PENDIENTE hasta que
Samuel suba los procedimientos PL/SQL reales — en ese momento,
se descomenta la llamada a call_procedure / call_procedure_with_cursor.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from db_connection import call_procedure, call_procedure_with_cursor


# ---------- VENTANAS DE FORMULARIO ----------

def abrir_form_crear_usuario():
    ventana = tk.Toplevel()
    ventana.title("Crear Usuario")
    ventana.geometry("300x150")

    tk.Label(ventana, text="Nombre:").pack(pady=(10, 0))
    entry_nombre = tk.Entry(ventana, width=30)
    entry_nombre.pack()

    tk.Label(ventana, text="Email:").pack(pady=(10, 0))
    entry_email = tk.Entry(ventana, width=30)
    entry_email.pack()

    def guardar():
        nombre = entry_nombre.get().strip()
        email = entry_email.get().strip()
        if not nombre or not email:
            messagebox.showwarning("Falta información", "Nombre y email son obligatorios.")
            return
        # TODO: cuando pkg_users.insert_user exista, descomentar:
        # call_procedure("pkg_users.insert_user", [nombre, email])
        messagebox.showinfo("Pendiente", "pkg_users.insert_user aún no está disponible.")
        ventana.destroy()

    tk.Button(ventana, text="Guardar", command=guardar).pack(pady=15)


def abrir_ver_usuarios():
    ventana = tk.Toplevel()
    ventana.title("Usuarios")
    ventana.geometry("400x250")

    lista = tk.Listbox(ventana, width=50)
    lista.pack(padx=10, pady=10, fill="both", expand=True)

    # TODO: cuando pkg_users.get_all_users exista, descomentar:
    # rows = call_procedure_with_cursor("pkg_users.get_all_users")
    # for row in rows:
    #     lista.insert(tk.END, f"{row[0]} — {row[1]} ({row[2]})")

    lista.insert(tk.END, "pkg_users.get_all_users aún no está disponible.")


def abrir_form_publicar_articulo():
    ventana = tk.Toplevel()
    ventana.title("Publicar Artículo")
    ventana.geometry("400x400")

    tk.Label(ventana, text="Título:").pack(pady=(10, 0))
    entry_titulo = tk.Entry(ventana, width=40)
    entry_titulo.pack()

    tk.Label(ventana, text="Texto:").pack(pady=(10, 0))
    text_cuerpo = tk.Text(ventana, width=40, height=6)
    text_cuerpo.pack()

    tk.Label(ventana, text="ID de usuario autor:").pack(pady=(10, 0))
    entry_user_id = tk.Entry(ventana, width=10)
    entry_user_id.pack()

    tk.Label(ventana, text="IDs de etiquetas (separados por coma):").pack(pady=(10, 0))
    entry_tags = tk.Entry(ventana, width=40)
    entry_tags.pack()

    tk.Label(ventana, text="IDs de categorías (separados por coma):").pack(pady=(10, 0))
    entry_categorias = tk.Entry(ventana, width=40)
    entry_categorias.pack()

    def guardar():
        titulo = entry_titulo.get().strip()
        texto = text_cuerpo.get("1.0", tk.END).strip()
        user_id = entry_user_id.get().strip()

        if not titulo or not texto or not user_id:
            messagebox.showwarning("Falta información", "Título, texto y usuario son obligatorios.")
            return

        # TODO: cuando pkg_articles.create_article exista, descomentar y capturar
        # el ID de retorno (parámetro OUT) para después llamar assign_tag / assign_category:
        #
        # article_id = ...  # resultado del OUT de create_article
        # for tag_id in entry_tags.get().split(","):
        #     tag_id = tag_id.strip()
        #     if tag_id:
        #         call_procedure("pkg_articles.assign_tag", [article_id, tag_id])
        # for cat_id in entry_categorias.get().split(","):
        #     cat_id = cat_id.strip()
        #     if cat_id:
        #         call_procedure("pkg_articles.assign_category", [article_id, cat_id])

        messagebox.showinfo("Pendiente", "pkg_articles.create_article aún no está disponible.")
        ventana.destroy()

    tk.Button(ventana, text="Publicar", command=guardar).pack(pady=15)


def abrir_ver_articulos():
    ventana = tk.Toplevel()
    ventana.title("Artículos")
    ventana.geometry("400x250")

    lista = tk.Listbox(ventana, width=50)
    lista.pack(padx=10, pady=10, fill="both", expand=True)

    # TODO: cuando pkg_articles.get_all_articles exista, descomentar:
    # rows = call_procedure_with_cursor("pkg_articles.get_all_articles")
    # for row in rows:
    #     lista.insert(tk.END, f"{row[0]} — {row[1]}")

    lista.insert(tk.END, "pkg_articles.get_all_articles aún no está disponible.")


def abrir_form_comentario():
    ventana = tk.Toplevel()
    ventana.title("Agregar Comentario")
    ventana.geometry("350x300")

    tk.Label(ventana, text="ID de artículo:").pack(pady=(10, 0))
    entry_article_id = tk.Entry(ventana, width=10)
    entry_article_id.pack()

    tk.Label(ventana, text="ID de usuario:").pack(pady=(10, 0))
    entry_user_id = tk.Entry(ventana, width=10)
    entry_user_id.pack()

    tk.Label(ventana, text="Comentario:").pack(pady=(10, 0))
    text_contenido = tk.Text(ventana, width=35, height=6)
    text_contenido.pack()

    def guardar():
        # TODO: cuando pkg_comments.add_comment exista, descomentar:
        # call_procedure("pkg_comments.add_comment", [
        #     text_contenido.get("1.0", tk.END).strip(),
        #     entry_user_id.get().strip(),
        #     entry_article_id.get().strip(),
        # ])
        messagebox.showinfo("Pendiente", "pkg_comments.add_comment aún no está disponible.")
        ventana.destroy()

    tk.Button(ventana, text="Comentar", command=guardar).pack(pady=15)


def abrir_ver_comentarios():
    ventana = tk.Toplevel()
    ventana.title("Comentarios de un Artículo")
    ventana.geometry("400x300")

    tk.Label(ventana, text="ID de artículo:").pack(pady=(10, 0))
    entry_article_id = tk.Entry(ventana, width=10)
    entry_article_id.pack()

    lista = tk.Listbox(ventana, width=50)
    lista.pack(padx=10, pady=10, fill="both", expand=True)

    def buscar():
        lista.delete(0, tk.END)
        # TODO: cuando pkg_comments.get_by_article exista, descomentar:
        # rows = call_procedure_with_cursor("pkg_comments.get_by_article", [entry_article_id.get().strip()])
        # for row in rows:
        #     lista.insert(tk.END, f"{row[2]} — {row[1]}")
        lista.insert(tk.END, "pkg_comments.get_by_article aún no está disponible.")

    tk.Button(ventana, text="Buscar", command=buscar).pack(pady=5)


def abrir_form_categoria():
    _abrir_form_generico("Crear Categoría", "pkg_categories.insert_category")


def abrir_form_etiqueta():
    _abrir_form_generico("Crear Etiqueta", "pkg_tags.insert_tag")


def _abrir_form_generico(titulo_ventana, nombre_procedimiento):
    ventana = tk.Toplevel()
    ventana.title(titulo_ventana)
    ventana.geometry("300x150")

    tk.Label(ventana, text="Nombre:").pack(pady=(10, 0))
    entry_nombre = tk.Entry(ventana, width=30)
    entry_nombre.pack()

    tk.Label(ventana, text="URL:").pack(pady=(10, 0))
    entry_url = tk.Entry(ventana, width=30)
    entry_url.pack()

    def guardar():
        # TODO: cuando el procedimiento exista, descomentar:
        # call_procedure(nombre_procedimiento, [entry_nombre.get().strip(), entry_url.get().strip()])
        messagebox.showinfo("Pendiente", f"{nombre_procedimiento} aún no está disponible.")
        ventana.destroy()

    tk.Button(ventana, text="Guardar", command=guardar).pack(pady=15)


# ---------- VENTANA PRINCIPAL ----------

def main():
    root = tk.Tk()
    root.title("Administrador de Blog")
    root.geometry("300x400")

    ttk.Label(root, text="Administrador de Blog", font=("Arial", 14, "bold")).pack(pady=15)

    botones = [
        ("Crear Usuario", abrir_form_crear_usuario),
        ("Ver Usuarios", abrir_ver_usuarios),
        ("Publicar Artículo", abrir_form_publicar_articulo),
        ("Ver Artículos", abrir_ver_articulos),
        ("Agregar Comentario", abrir_form_comentario),
        ("Ver Comentarios de un Artículo", abrir_ver_comentarios),
        ("Crear Categoría", abrir_form_categoria),
        ("Crear Etiqueta", abrir_form_etiqueta),
    ]

    for texto, funcion in botones:
        ttk.Button(root, text=texto, command=funcion, width=30).pack(pady=4)

    root.mainloop()


if __name__ == "__main__":
    main()