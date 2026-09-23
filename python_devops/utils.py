"""
utils.py
Helpers de la capa visual para llamar procedimientos PL/SQL de lectura
(get_all_*, get_by_*) que todavía pueden no tener lógica real (cuerpo NULL),
sin romper la GUI y sin fingir que el backend respondió cuando no lo hizo.

No modifica ni reemplaza nada de db_connection.py — solo envuelve sus
funciones para distinguir 'no hay datos todavía' de 'el backend no está
listo'.
"""

from db_connection import call_procedure_with_cursor, fetch_options


def safe_get_all(package_procedure, params=None):
    """
    Intenta traer filas de un procedimiento get_all_*/get_by_*.

    Regresa:
        - list[...]  si el procedimiento ya funciona (puede ser vacía si aún
                      no hay datos en la tabla)
        - None       si el procedimiento todavía no tiene lógica real
                      (la llamada falla porque el cursor nunca se abrió)

    Así cada vista puede mostrar el mensaje correcto: "pendiente de
    conectar con X" vs. "todavía no hay datos".
    """
    try:
        rows = call_procedure_with_cursor(package_procedure, params)
        return rows if rows is not None else []
    except Exception:
        return None


def users_lookup():
    """
    Mapa id -> nombre de usuario, usando el helper temporal fetch_options
    (ver su docstring en db_connection.py). Se usa solo para mostrar el
    nombre del autor en tarjetas/comentarios, no para lógica de negocio.
    """
    try:
        return {uid: nombre for uid, nombre in fetch_options("users", "id", "name")}
    except Exception:
        return {}
