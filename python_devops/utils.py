"""
utils.py
Helpers de la capa visual para llamar procedimientos PL/SQL de lectura
(get_all_*, get_by_*) que todavía pueden no tener lógica real (cuerpo NULL),
sin romper la GUI y sin fingir que el backend respondió cuando no lo hizo.
"""

from db_connection import call_procedure_with_cursor, fetch_options

def safe_get_all(package_procedure, params=None):
    """
    Intenta traer filas de un procedimiento get_all_*/get_by_*.
    Devuelve lista vacía en vez de None para evitar mensajes feos en la interfaz.
    """
    try:
        rows = call_procedure_with_cursor(package_procedure, params)
        return rows if rows is not None else []
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