"""
test_integration.py
Prueba de integración de todo el circuito: Docker -> Oracle -> Python.

Valida:
1. Conexión y CLOB (vía db_connection.get_connection()).
2. Datos semilla del schema (users, tags, categories, articles).
3. Que los 5 paquetes PL/SQL existan y sean invocables con la firma
   correcta (aunque su lógica interna todavía sea NULL; solo confirma
   que Python y PL/SQL están bien conectados, no que el CRUD funcione).

Uso: python test_integration.py
"""

import oracledb
from db_connection import get_connection, call_procedure, call_procedure_with_cursor

resultados = []


def check(nombre, condicion, detalle=""):
    estado = "✅" if condicion else "❌"
    resultados.append(condicion)
    print(f"{estado} {nombre}{(' — ' + detalle) if detalle else ''}")


def check_cursor_procedure(nombre, funcion):
    """
    Para procedimientos que regresan SYS_REFCURSOR: si el cuerpo real
    todavía es NULL;, oracledb lanza DPY-4025 (cursor nunca abierto).
    Eso NO es un error de conexión ni de firma — es la señal correcta
    de que el procedimiento existe y fue invocado bien, solo falta que
    Samuel implemente el OPEN p_cursor FOR ... adentro.
    """
    try:
        funcion()
        check(nombre, True)
    except oracledb.Error as e:
        if "DPY-4025" in str(e):
            print(f"⚠️  {nombre} — firma OK, pendiente de lógica en PL/SQL (cursor sin abrir)")
            resultados.append(True)
        else:
            check(nombre, False, str(e))


def probar_conexion_y_datos_semilla():
    print("\n--- 1. Conexión y datos semilla ---")
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM users")
            check("Conexión abierta y query simple", True)

            cur.execute("SELECT COUNT(*) FROM users")
            n = cur.fetchone()[0]
            check("Seed: 3 usuarios", n == 3, f"encontrados: {n}")

            cur.execute("SELECT COUNT(*) FROM tags")
            n = cur.fetchone()[0]
            check("Seed: 5 etiquetas", n == 5, f"encontrados: {n}")

            cur.execute("SELECT COUNT(*) FROM categories")
            n = cur.fetchone()[0]
            check("Seed: 3 categorías", n == 3, f"encontrados: {n}")

            cur.execute("SELECT COUNT(*) FROM articles")
            n = cur.fetchone()[0]
            check("Seed: 2 artículos", n == 2, f"encontrados: {n}")

            # Verifica que el CLOB de 'text' se lea como string normal
            cur.execute("SELECT title, text FROM articles WHERE id = 1")
            title, text = cur.fetchone()
            check(
                "CLOB de 'text' se lee como string (outputtypehandler OK)",
                isinstance(text, str) and len(text) > 0,
                f"tipo recibido: {type(text).__name__}",
            )


def probar_firmas_procedimientos():
    print("\n--- 2. Firmas de los 5 paquetes PL/SQL ---")

    # pkg_users
    try:
        call_procedure("pkg_users.insert_user", ["Prueba Integración", "prueba@correo.com"])
        check("pkg_users.insert_user es invocable", True)
    except oracledb.Error as e:
        check("pkg_users.insert_user es invocable", False, str(e))

    check_cursor_procedure(
        "pkg_users.get_all_users es invocable",
        lambda: call_procedure_with_cursor("pkg_users.get_all_users"),
    )

    # pkg_articles — create_article tiene parámetro OUT NUMBER, se prueba aparte
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                out_id = cur.var(oracledb.DB_TYPE_NUMBER)
                cur.callproc("pkg_articles.create_article", ["Título de prueba", "Texto de prueba", 1, out_id])
        check("pkg_articles.create_article (con OUT) es invocable", True)
    except oracledb.Error as e:
        check("pkg_articles.create_article (con OUT) es invocable", False, str(e))

    try:
        call_procedure("pkg_articles.assign_tag", [1, 1])
        check("pkg_articles.assign_tag es invocable", True)
    except oracledb.Error as e:
        check("pkg_articles.assign_tag es invocable", False, str(e))

    try:
        call_procedure("pkg_articles.assign_category", [1, 1])
        check("pkg_articles.assign_category es invocable", True)
    except oracledb.Error as e:
        check("pkg_articles.assign_category es invocable", False, str(e))

    check_cursor_procedure(
        "pkg_articles.get_all_articles es invocable",
        lambda: call_procedure_with_cursor("pkg_articles.get_all_articles"),
    )

    # pkg_comments
    try:
        call_procedure("pkg_comments.add_comment", ["Comentario de prueba", 1, 1])
        check("pkg_comments.add_comment es invocable", True)
    except oracledb.Error as e:
        check("pkg_comments.add_comment es invocable", False, str(e))

    check_cursor_procedure(
        "pkg_comments.get_by_article es invocable",
        lambda: call_procedure_with_cursor("pkg_comments.get_by_article", [1]),
    )

    # pkg_categories
    try:
        call_procedure("pkg_categories.insert_category", ["Categoría de prueba", "/prueba"])
        check("pkg_categories.insert_category es invocable", True)
    except oracledb.Error as e:
        check("pkg_categories.insert_category es invocable", False, str(e))

    check_cursor_procedure(
        "pkg_categories.get_all es invocable",
        lambda: call_procedure_with_cursor("pkg_categories.get_all"),
    )

    # pkg_tags
    try:
        call_procedure("pkg_tags.insert_tag", ["Tag de prueba", "/prueba"])
        check("pkg_tags.insert_tag es invocable", True)
    except oracledb.Error as e:
        check("pkg_tags.insert_tag es invocable", False, str(e))

    check_cursor_procedure(
        "pkg_tags.get_all es invocable",
        lambda: call_procedure_with_cursor("pkg_tags.get_all"),
    )


def main():
    probar_conexion_y_datos_semilla()
    probar_firmas_procedimientos()

    print("\n--- Resumen ---")
    total = len(resultados)
    exitosos = sum(resultados)
    print(f"{exitosos}/{total} checks pasaron.")
    if exitosos == total:
        print("✅ Circuito completo (Docker + Oracle + PL/SQL + Python) funcionando de punta a punta.")
        print("   Los ⚠️  son procedimientos con firma correcta, pendientes de que Samuel abra el cursor.")
    else:
        print("❌ Hay al menos un problema de conexión o de firma — revisa el detalle arriba.")


if __name__ == "__main__":
    main()