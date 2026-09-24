"""Utilidades de lectura y normalización para las vistas de la aplicación.

Las vistas consultan primero los procedimientos PL/SQL. Cuando una operación
de lectura no está disponible, se usa una consulta de respaldo explícita para
mantener la interfaz operativa sin ocultar errores de escritura.
"""

from db_connection import call_procedure_with_cursor, fetch_options, get_connection


def safe_get_all(package_procedure, params=None):
    """Obtiene filas mediante PL/SQL y aplica una consulta de respaldo.

    Returns:
        Lista de filas. Si no existe un respaldo o falla la consulta, devuelve
        una lista vacía para que la vista pueda mostrar su estado vacío.
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
    """Devuelve un mapa ``id -> nombre`` para presentar autores en la GUI."""
    try:
        return {uid: nombre for uid, nombre in fetch_options("users", "id", "name")}
    except Exception:
        return {}
