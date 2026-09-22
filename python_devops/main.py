"""
main.py
Interfaz de consola del Administrador de Blog.

Este es un ESQUELETO: las funciones de cada opción están vacías (placeholder).
Cuando el Integrante 2 suba los procedimientos PL/SQL definitivos, cada función
se conecta a su procedimiento real usando call_procedure / call_procedure_with_cursor
de db_connection.py, siguiendo el Contrato de Nombres del documento del proyecto.
"""

from db_connection import call_procedure, call_procedure_with_cursor


# ---------- USUARIOS ----------

def crear_usuario():
    print("\n[Crear Usuario] — pendiente de conectar con pkg_users.insert_user")
    # name = input("Nombre: ")
    # email = input("Email: ")
    # call_procedure("pkg_users.insert_user", [name, email])


def ver_usuarios():
    print("\n[Ver Usuarios] — pendiente de conectar con pkg_users.get_all_users")
    # rows = call_procedure_with_cursor("pkg_users.get_all_users")
    # for row in rows:
    #     print(row)


# ---------- ARTÍCULOS ----------

def publicar_articulo():
    print("\n[Publicar Artículo] — pendiente de conectar con pkg_articles.create_article")
    # title = input("Título: ")
    # text = input("Texto: ")
    # user_id = input("ID de usuario autor: ")
    # article_id = ...  # capturar el OUT de create_article
    # tag_ids = input("IDs de etiquetas separados por coma: ").split(",")
    # for tag_id in tag_ids:
    #     call_procedure("pkg_articles.assign_tag", [article_id, tag_id.strip()])
    # category_ids = input("IDs de categorías separados por coma: ").split(",")
    # for category_id in category_ids:
    #     call_procedure("pkg_articles.assign_category", [article_id, category_id.strip()])


def ver_articulos():
    print("\n[Ver Artículos] — pendiente de conectar con el procedimiento correspondiente")


# ---------- COMENTARIOS ----------

def agregar_comentario():
    print("\n[Agregar Comentario] — pendiente de conectar con pkg_comments.add_comment")


def ver_comentarios_de_articulo():
    print("\n[Ver Comentarios] — pendiente de conectar con pkg_comments.get_by_article")


# ---------- CATEGORÍAS Y ETIQUETAS ----------

def crear_categoria():
    print("\n[Crear Categoría] — pendiente de conectar con pkg_categories.insert_category")


def crear_etiqueta():
    print("\n[Crear Etiqueta] — pendiente de conectar con pkg_tags.insert_tag")


# ---------- MENÚ PRINCIPAL ----------

MENU_OPCIONES = {
    "1": ("Crear Usuario", crear_usuario),
    "2": ("Ver Usuarios", ver_usuarios),
    "3": ("Publicar Artículo", publicar_articulo),
    "4": ("Ver Artículos", ver_articulos),
    "5": ("Agregar Comentario", agregar_comentario),
    "6": ("Ver Comentarios de un Artículo", ver_comentarios_de_articulo),
    "7": ("Crear Categoría", crear_categoria),
    "8": ("Crear Etiqueta", crear_etiqueta),
}


def mostrar_menu():
    print("\n===== Administrador de Blog =====")
    for key, (label, _) in MENU_OPCIONES.items():
        print(f"{key}. {label}")
    print("0. Salir")


def main():
    while True:
        mostrar_menu()
        opcion = input("\nSelecciona una opción: ").strip()

        if opcion == "0":
            print("Saliendo...")
            break

        seleccion = MENU_OPCIONES.get(opcion)
        if seleccion:
            _, funcion = seleccion
            funcion()
        else:
            print("Opción no válida.")


if __name__ == "__main__":
    main()
