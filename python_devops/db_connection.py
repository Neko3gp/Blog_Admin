"""Conexión a Oracle y wrappers de procedimientos PL/SQL."""

import oracledb

# Credenciales = docker-compose.yml (APP_USER / ORACLE_DATABASE)
DB_USER = "blog_admin"
DB_PASSWORD = "admin123"
DB_DSN = "localhost:1521/FREEPDB2"


def _clob_output_type_handler(cursor, metadata):
    # Sin esto oracledb devuelve LOB; con esto articles.text / comments.content llegan como str.
    if metadata.type_code is oracledb.DB_TYPE_CLOB:
        return cursor.var(oracledb.DB_TYPE_LONG, arraysize=cursor.arraysize)


def get_connection():
    connection = oracledb.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        dsn=DB_DSN,
    )
    connection.outputtypehandler = _clob_output_type_handler
    return connection


def fetch_options(table, id_column, label_column, order_by=None):
    """SELECT id,label para combos (users / tags / categories)."""
    order_clause = f" ORDER BY {order_by}" if order_by else f" ORDER BY {id_column}"
    query = f"SELECT {id_column}, {label_column} FROM {table}{order_clause}"
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()


def call_procedure(package_procedure, params=None):
    """callproc sin OUT (insert/update/delete/assign/clear)."""
    params = params or []
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.callproc(package_procedure, params)


def call_procedure_returning_id(package_procedure, params, out_index=-1):
    """callproc con OUT NUMBER (pkg_articles.create_article)."""
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
    """callproc con SYS_REFCURSOR OUT → lista de filas (get_all / get_by_article)."""
    params = params or []
    with get_connection() as connection:
        with connection.cursor() as cursor:
            out_cursor = cursor.var(oracledb.DB_TYPE_CURSOR)
            cursor.callproc(package_procedure, params + [out_cursor])
            result_cursor = out_cursor.getvalue()
            return result_cursor.fetchall()


def fetch_article_text(article_id):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT text FROM articles WHERE id = :id", {"id": article_id})
            row = cursor.fetchone()
            return row[0] if row else None


def fetch_article_taxonomy(article_id):
    """Nombres de tags/categories vía article_tags / article_categories."""
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


def fetch_article_taxonomy_ids(article_id):
    """IDs para premarcar checkboxes al editar un artículo."""
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT tag_id FROM article_tags WHERE article_id = :id ORDER BY tag_id",
                {"id": article_id},
            )
            tag_ids = [r[0] for r in cursor.fetchall()]
            cursor.execute(
                "SELECT category_id FROM article_categories WHERE article_id = :id ORDER BY category_id",
                {"id": article_id},
            )
            category_ids = [r[0] for r in cursor.fetchall()]
            return tag_ids, category_ids


def fetch_article_user_id(article_id):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT user_id FROM articles WHERE id = :id", {"id": article_id})
            row = cursor.fetchone()
            return row[0] if row else None


if __name__ == "__main__":
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM DUAL")
            print("Conexión OK:", cursor.fetchone())
