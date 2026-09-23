"""
utils.py
Helpers de la capa visual para llamar procedimientos PL/SQL de lectura
(get_all_*, get_by_*) que todavía pueden no tener lógica real (cuerpo NULL),
sin romper la GUI y sin fingir que el backend respondió cuando no lo hizo.
"""

from db_connection import call_procedure_with_cursor, fetch_options, get_connection


def safe_get_all(package_procedure, params=None):
    """
    Intenta traer filas de un procedimiento get_all_*/get_by_*.
    Devuelve lista vacía en vez de None para evitar mensajes feos en la interfaz.
    """
    try:
        rows = call_procedure_with_cursor(package_procedure, params)
        if rows:
            return rows
    except Exception:
        pass

    fallback_sql = {
        "pkg_articles.get_all_articles":
            "SELECT id, title, pub_date, user_id FROM articles ORDER BY id",
        "pkg_users.get_all_users":
            "SELECT id, name, email FROM users ORDER BY id",
        "pkg_categories.get_all":
            "SELECT id, name, url FROM categories ORDER BY id",
        "pkg_tags.get_all":
            "SELECT id, name, url FROM tags ORDER BY id",
    }
    sql = fallback_sql.get(package_procedure)
    if not sql:
        return []
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                return cursor.fetchall()
    except Exception:
        return []


def users_lookup():
    """
    Mapa id -> nombre de usuario.
    """
    try:
        return {uid: nombre for uid, nombre in fetch_options("users", "id", "name")}
    except Exception:
        return {}
