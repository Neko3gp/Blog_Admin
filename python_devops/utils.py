"""Helpers de lectura para las vistas (PL/SQL con fallback SQL)."""

from db_connection import call_procedure_with_cursor, fetch_options, get_connection


def safe_get_all(package_procedure, params=None):
    try:
        rows = call_procedure_with_cursor(package_procedure, params)
        if rows:
            return rows
    except Exception:
        pass

    # Fallback si el procedimiento get_* no responde (misma proyección que el paquete).
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
    """id → name (autores en feed / comentarios)."""
    try:
        return {uid: nombre for uid, nombre in fetch_options("users", "id", "name")}
    except Exception:
        return {}
