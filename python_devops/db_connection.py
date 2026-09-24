"""Servicios de acceso a Oracle para la aplicación Administrador de Blog.

Este módulo concentra la configuración de conexión, la conversión de valores
CLOB y los adaptadores utilizados por la interfaz para ejecutar procedimientos
PL/SQL y consultas auxiliares. Las funciones que abren conexiones las cierran
mediante gestores de contexto para evitar recursos abiertos.
"""

import oracledb

# Estos valores deben coincidir con docker-compose.yml. Son credenciales de
# desarrollo local y no deben reutilizarse en un entorno de producción.
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
    """Obtiene pares ``(id, etiqueta)`` para controles de selección.

    Args:
        table: Tabla de origen validada por los módulos consumidores.
        id_column: Columna que identifica el registro.
        label_column: Columna visible para el usuario.
        order_by: Columna opcional de ordenación; por defecto se usa el ID.

    Returns:
        Lista de tuplas devuelta por Oracle.
    """
    order_clause = f" ORDER BY {order_by}" if order_by else f" ORDER BY {id_column}"
    query = f"SELECT {id_column}, {label_column} FROM {table}{order_clause}"
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()


def call_procedure(package_procedure, params=None):
    """Ejecuta un procedimiento PL/SQL sin parámetros de salida."""
    params = params or []
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.callproc(package_procedure, params)


def call_procedure_returning_id(package_procedure, params, out_index=-1):
    """Ejecuta un procedimiento con un parámetro ``OUT NUMBER``.

    ``out_index`` permite insertar el parámetro de salida en cualquier
    posición de la firma; por defecto se añade al final.
    """
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
    """Ejecuta un procedimiento que devuelve un ``SYS_REFCURSOR``.

    El cursor de salida se consume dentro de la conexión y se transforma en
    una lista de filas para que la capa visual no dependa de objetos Oracle.
    """
    params = params or []
    with get_connection() as connection:
        with connection.cursor() as cursor:
            out_cursor = cursor.var(oracledb.DB_TYPE_CURSOR)
            cursor.callproc(package_procedure, params + [out_cursor])
            result_cursor = out_cursor.getvalue()
            return result_cursor.fetchall()


def fetch_article_text(article_id):
    """Obtiene el contenido CLOB de un artículo o ``None`` si no existe."""
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT text FROM articles WHERE id = :id", {"id": article_id})
            row = cursor.fetchone()
            return row[0] if row else None


def fetch_article_taxonomy(article_id):
    """Obtiene las etiquetas y categorías asociadas a un artículo.

    Returns:
        Tupla ``(tags, categories)`` con listas de nombres ordenadas.
    """
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
    # Permite verificar el acceso a Oracle sin iniciar la interfaz gráfica.
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM DUAL")
            print("Conexión OK:", cursor.fetchone())