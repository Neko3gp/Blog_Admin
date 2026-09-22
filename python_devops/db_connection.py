"""
db_connection.py
Módulo centralizado de conexión a Oracle para el proyecto Administrador de Blog.

Uso:
    from db_connection import get_connection

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM DUAL")
            print(cursor.fetchone())
"""

import oracledb

# Credenciales estándar del equipo (ver README / docker-compose.yml)
DB_USER = "blog_admin"
DB_PASSWORD = "admin123"
DB_DSN = "localhost:1521/FREEPDB2"


def _clob_output_type_handler(cursor, metadata):
    """
    Convierte automáticamente las columnas CLOB a string al leerlas,
    para no tener que llamar .read() manualmente en cada SELECT.
    Sin esto, imprimir un CLOB muestra <oracledb.LOB object at 0x...>
    en vez del texto real.
    """
    if metadata.type_code is oracledb.DB_TYPE_CLOB:
        return cursor.var(oracledb.DB_TYPE_LONG, arraysize=cursor.arraysize)


def get_connection():
    """
    Abre y regresa una conexión a Oracle, con el output_type_handler
    ya configurado para manejar CLOB automáticamente.

    Se recomienda usar con 'with' para que se cierre sola:
        with get_connection() as connection:
            ...
    """
    connection = oracledb.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        dsn=DB_DSN,
    )
    connection.outputtypehandler = _clob_output_type_handler
    return connection


def call_procedure(package_procedure, params=None):
    """
    Helper genérico para invocar un procedimiento almacenado (sin cursor de salida).

    Ejemplo:
        call_procedure("pkg_users.insert_user", ["Ana", "ana@correo.com"])
    """
    params = params or []
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.callproc(package_procedure, params)


def call_procedure_with_cursor(package_procedure, params=None):
    """
    Helper genérico para invocar un procedimiento que regresa un SYS_REFCURSOR
    como parámetro de salida, y regresa la lista de filas ya resuelta.

    Ejemplo:
        rows = call_procedure_with_cursor("pkg_users.get_all_users")
        for row in rows:
            print(row)
    """
    params = params or []
    with get_connection() as connection:
        with connection.cursor() as cursor:
            out_cursor = cursor.var(oracledb.DB_TYPE_CURSOR)
            cursor.callproc(package_procedure, params + [out_cursor])
            result_cursor = out_cursor.getvalue()
            return result_cursor.fetchall()


if __name__ == "__main__":
    # Prueba rápida manual: python db_connection.py
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM DUAL")
            print("Conexión OK:", cursor.fetchone())
