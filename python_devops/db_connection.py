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
# IMPORTANTE: este valor debe coincidir exactamente con docker-compose.yml y el README.
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


def fetch_options(table, id_column, label_column, order_by=None):
    """
    Helper TEMPORAL para poblar dropdowns (ttk.Combobox) con pares (id, etiqueta),
    ej. fetch_options("users", "id", "name") -> [(1, "Ana Torres"), (2, "Luis Fernández"), ...]

    Usa un SELECT directo en vez de pasar por los paquetes de PL/SQL, porque los
    procedimientos get_all_* de Samuel todavía no abren su cursor (ver TODOs en
    02_procedures.sql). En cuanto esos procedimientos ya funcionen, hay que
    reemplazar las llamadas a esta función por call_procedure_with_cursor(...)
    y borrar este helper — es un puente, no la versión definitiva.
    """
    order_clause = f" ORDER BY {order_by}" if order_by else f" ORDER BY {id_column}"
    query = f"SELECT {id_column}, {label_column} FROM {table}{order_clause}"
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()


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


def call_procedure_returning_id(package_procedure, params, out_index=-1):
    """Invoca un procedimiento con parámetro OUT NUMBER y regresa el ID."""
    params = list(params)
    with get_connection() as connection:
        with connection.cursor() as cursor:
            out_id = cursor.var(oracledb.DB_TYPE_NUMBER)
            if out_index < 0:
                out_index = len(params)
            call_args = params[:out_index] + [out_id] + params[out_index:]
            cursor.callproc(package_procedure, call_args)
            value = out_id.getvalue()
            return int(value) if value is not None else None


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


def fetch_article_text(article_id):
    """Lee el texto (CLOB) de un artículo por id."""
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT text FROM articles WHERE id = :id", {"id": article_id})
            row = cursor.fetchone()
            return row[0] if row else None


def fetch_article_taxonomy(article_id):
    """Regresa (tags, categories) como listas de nombres."""
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT t.name FROM tags t
                JOIN article_tags at ON at.tag_id = t.id
                WHERE at.article_id = :id ORDER BY t.name
                """,
                {"id": article_id},
            )
            tags = [r[0] for r in cursor.fetchall()]
            cursor.execute(
                """
                SELECT c.name FROM categories c
                JOIN article_categories ac ON ac.category_id = c.id
                WHERE ac.article_id = :id ORDER BY c.name
                """,
                {"id": article_id},
            )
            categories = [r[0] for r in cursor.fetchall()]
            return tags, categories


if __name__ == "__main__":
    # Prueba rápida manual: python db_connection.py
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM DUAL")
            print("Conexión OK:", cursor.fetchone())