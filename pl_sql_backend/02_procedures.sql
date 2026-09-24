-- =====================================================
-- 02_procedures.sql
-- Propósito: definir la API PL/SQL de la aplicación.
-- Cada paquete encapsula las operaciones de una entidad y confirma o
-- revierte sus propias transacciones de escritura.
-- =====================================================

-- ---------- Usuarios ----------

CREATE OR REPLACE PACKAGE pkg_users AS
    PROCEDURE insert_user(
        p_name  IN VARCHAR2,
        p_email IN VARCHAR2
    );

    PROCEDURE get_all_users(
        p_cursor OUT SYS_REFCURSOR
    );
END pkg_users;
/

CREATE OR REPLACE PACKAGE BODY pkg_users AS

    PROCEDURE insert_user(
        p_name  IN VARCHAR2,
        p_email IN VARCHAR2
    ) IS
    BEGIN
        INSERT INTO users(name, email)
        VALUES (p_name, p_email);
        COMMIT;
    EXCEPTION
        WHEN DUP_VAL_ON_INDEX THEN
            RAISE_APPLICATION_ERROR(-20001, 'Email ya registrado');
        WHEN OTHERS THEN
            ROLLBACK;
            RAISE;
    END insert_user;

    PROCEDURE get_all_users(
        p_cursor OUT SYS_REFCURSOR
    ) IS
    BEGIN
        OPEN p_cursor FOR
            SELECT id, name, email
            FROM users
            ORDER BY id;
    END get_all_users;

END pkg_users;
/


-- ---------- Artículos y asociaciones taxonómicas ----------

CREATE OR REPLACE PACKAGE pkg_articles AS
    PROCEDURE create_article(
        p_title      IN  VARCHAR2,
        p_text       IN  CLOB,
        p_user_id    IN  NUMBER,
        p_article_id OUT NUMBER
    );

    PROCEDURE assign_tag(
        p_article_id IN NUMBER,
        p_tag_id     IN NUMBER
    );

    PROCEDURE assign_category(
        p_article_id  IN NUMBER,
        p_category_id IN NUMBER
    );

    PROCEDURE get_all_articles(
        p_cursor OUT SYS_REFCURSOR
    );
END pkg_articles;
/

CREATE OR REPLACE PACKAGE BODY pkg_articles AS

    PROCEDURE create_article(
        p_title      IN  VARCHAR2,
        p_text       IN  CLOB,
        p_user_id    IN  NUMBER,
        p_article_id OUT NUMBER
    ) IS
    BEGIN
        INSERT INTO articles(title, text, user_id)
        VALUES (p_title, p_text, p_user_id)
        RETURNING id INTO p_article_id;
        COMMIT;
    EXCEPTION
        WHEN OTHERS THEN
            ROLLBACK;
            IF SQLCODE = -2291 THEN
                RAISE_APPLICATION_ERROR(-20002, 'Usuario no existe');
            ELSE
                RAISE;
            END IF;
    END create_article;

    PROCEDURE assign_tag(
        p_article_id IN NUMBER,
        p_tag_id     IN NUMBER
    ) IS
    BEGIN
        INSERT INTO article_tags(article_id, tag_id)
        VALUES (p_article_id, p_tag_id);
        COMMIT;
    EXCEPTION
        WHEN DUP_VAL_ON_INDEX THEN
            RAISE_APPLICATION_ERROR(-20003, 'Tag ya asignado a este artículo');
        WHEN OTHERS THEN
            ROLLBACK;
            IF SQLCODE = -2291 THEN
                RAISE_APPLICATION_ERROR(-20004, 'Artículo o tag no existe');
            ELSE
                RAISE;
            END IF;
    END assign_tag;

    PROCEDURE assign_category(
        p_article_id  IN NUMBER,
        p_category_id IN NUMBER
    ) IS
    BEGIN
        INSERT INTO article_categories(article_id, category_id)
        VALUES (p_article_id, p_category_id);
        COMMIT;
    EXCEPTION
        WHEN DUP_VAL_ON_INDEX THEN
            RAISE_APPLICATION_ERROR(-20005, 'Categoría ya asignada a este artículo');
        WHEN OTHERS THEN
            ROLLBACK;
            IF SQLCODE = -2291 THEN
                RAISE_APPLICATION_ERROR(-20006, 'Artículo o categoría no existe');
            ELSE
                RAISE;
            END IF;
    END assign_category;

    PROCEDURE get_all_articles(
        p_cursor OUT SYS_REFCURSOR
    ) IS
    BEGIN
        OPEN p_cursor FOR
            SELECT id, title, pub_date, user_id
            FROM articles
            ORDER BY id;
    END get_all_articles;

END pkg_articles;
/


-- ---------- Comentarios ----------

CREATE OR REPLACE PACKAGE pkg_comments AS
    PROCEDURE add_comment(
        p_content    IN CLOB,
        p_user_id    IN NUMBER,
        p_article_id IN NUMBER
    );

    PROCEDURE get_by_article(
        p_article_id IN  NUMBER,
        p_cursor     OUT SYS_REFCURSOR
    );
END pkg_comments;
/

CREATE OR REPLACE PACKAGE BODY pkg_comments AS

    PROCEDURE add_comment(
        p_content    IN CLOB,
        p_user_id    IN NUMBER,
        p_article_id IN NUMBER
    ) IS
    BEGIN
        INSERT INTO comments(content, user_id, article_id)
        VALUES (p_content, p_user_id, p_article_id);
        COMMIT;
    EXCEPTION
        WHEN OTHERS THEN
            ROLLBACK;
            IF SQLCODE = -2291 THEN
                RAISE_APPLICATION_ERROR(-20007, 'Usuario o artículo no existe');
            ELSE
                RAISE;
            END IF;
    END add_comment;

    PROCEDURE get_by_article(
        p_article_id IN  NUMBER,
        p_cursor     OUT SYS_REFCURSOR
    ) IS
    BEGIN
        OPEN p_cursor FOR
            SELECT id, content, creation_date, user_id
            FROM comments
            WHERE article_id = p_article_id
            ORDER BY creation_date;
    END get_by_article;

END pkg_comments;
/


-- ---------- Categorías ----------

CREATE OR REPLACE PACKAGE pkg_categories AS
    PROCEDURE insert_category(
        p_name IN VARCHAR2,
        p_url  IN VARCHAR2
    );

    PROCEDURE update_category(
        p_id   IN NUMBER,
        p_name IN VARCHAR2,
        p_url  IN VARCHAR2
    );

    PROCEDURE delete_category(
        p_id IN NUMBER
    );

    PROCEDURE get_all(
        p_cursor OUT SYS_REFCURSOR
    );
END pkg_categories;
/

CREATE OR REPLACE PACKAGE BODY pkg_categories AS

    PROCEDURE insert_category(
        p_name IN VARCHAR2,
        p_url  IN VARCHAR2
    ) IS
    BEGIN
        INSERT INTO categories(name, url)
        VALUES (p_name, p_url);
        COMMIT;
    EXCEPTION
        WHEN OTHERS THEN
            ROLLBACK;
            RAISE;
    END insert_category;

    PROCEDURE update_category(
        p_id   IN NUMBER,
        p_name IN VARCHAR2,
        p_url  IN VARCHAR2
    ) IS
    BEGIN
        UPDATE categories
        SET name = p_name, url = p_url
        WHERE id = p_id;
        IF SQL%ROWCOUNT = 0 THEN
            RAISE_APPLICATION_ERROR(-20008, 'Categoría no existe');
        END IF;
        COMMIT;
    EXCEPTION
        WHEN OTHERS THEN
            ROLLBACK;
            RAISE;
    END update_category;

    PROCEDURE delete_category(
        p_id IN NUMBER
    ) IS
    BEGIN
        DELETE FROM categories WHERE id = p_id;
        IF SQL%ROWCOUNT = 0 THEN
            RAISE_APPLICATION_ERROR(-20009, 'Categoría no existe');
        END IF;
        COMMIT;
    EXCEPTION
        WHEN OTHERS THEN
            ROLLBACK;
            RAISE;
    END delete_category;

    PROCEDURE get_all(
        p_cursor OUT SYS_REFCURSOR
    ) IS
    BEGIN
        OPEN p_cursor FOR
            SELECT id, name, url
            FROM categories
            ORDER BY id;
    END get_all;

END pkg_categories;
/


-- ---------- Etiquetas ----------

CREATE OR REPLACE PACKAGE pkg_tags AS
    PROCEDURE insert_tag(
        p_name IN VARCHAR2,
        p_url  IN VARCHAR2
    );

    PROCEDURE update_tag(
        p_id   IN NUMBER,
        p_name IN VARCHAR2,
        p_url  IN VARCHAR2
    );

    PROCEDURE delete_tag(
        p_id IN NUMBER
    );

    PROCEDURE get_all(
        p_cursor OUT SYS_REFCURSOR
    );
END pkg_tags;
/

CREATE OR REPLACE PACKAGE BODY pkg_tags AS

    PROCEDURE insert_tag(
        p_name IN VARCHAR2,
        p_url  IN VARCHAR2
    ) IS
    BEGIN
        INSERT INTO tags(name, url)
        VALUES (p_name, p_url);
        COMMIT;
    EXCEPTION
        WHEN OTHERS THEN
            ROLLBACK;
            RAISE;
    END insert_tag;

    PROCEDURE update_tag(
        p_id   IN NUMBER,
        p_name IN VARCHAR2,
        p_url  IN VARCHAR2
    ) IS
    BEGIN
        UPDATE tags
        SET name = p_name, url = p_url
        WHERE id = p_id;
        IF SQL%ROWCOUNT = 0 THEN
            RAISE_APPLICATION_ERROR(-20010, 'Etiqueta no existe');
        END IF;
        COMMIT;
    EXCEPTION
        WHEN OTHERS THEN
            ROLLBACK;
            RAISE;
    END update_tag;

    PROCEDURE delete_tag(
        p_id IN NUMBER
    ) IS
    BEGIN
        DELETE FROM tags WHERE id = p_id;
        IF SQL%ROWCOUNT = 0 THEN
            RAISE_APPLICATION_ERROR(-20011, 'Etiqueta no existe');
        END IF;
        COMMIT;
    EXCEPTION
        WHEN OTHERS THEN
            ROLLBACK;
            RAISE;
    END delete_tag;

    PROCEDURE get_all(
        p_cursor OUT SYS_REFCURSOR
    ) IS
    BEGIN
        OPEN p_cursor FOR
            SELECT id, name, url
            FROM tags
            ORDER BY id;
    END get_all;

END pkg_tags;
/
