-- 02_procedures.sql — API PL/SQL (cada paquete hace COMMIT/ROLLBACK propio).
-- CRUD / contrato usado por la GUI (python_devops):
--   pkg_users      → insert_user, get_all_users
--                    Vista: views/users.py
--   pkg_articles   → create/update/delete_article, get_all_articles,
--                    assign_tag/category, clear_tags/categories
--                    Vista: views/feed.py + new_article.py + article_detail.py
--   pkg_comments   → add/update/delete_comment, get_by_article
--                    Vista: views/article_detail.py
--   pkg_categories → insert/update/delete_category, get_all
--                    Vista: views/taxonomy.py (CategoriesView)
--   pkg_tags       → insert/update/delete_tag, get_all
--                    Vista: views/taxonomy.py (TagsView)

-- ---------- Usuarios (C: insert | R: get_all) ----------

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


-- ---------- Artículos (CRUD + N:N tags/categories) ----------

CREATE OR REPLACE PACKAGE pkg_articles AS
    PROCEDURE create_article(
        p_title      IN  VARCHAR2,
        p_text       IN  CLOB,
        p_user_id    IN  NUMBER,
        p_article_id OUT NUMBER
    );

    PROCEDURE update_article(
        p_id      IN NUMBER,
        p_title   IN VARCHAR2,
        p_text    IN CLOB,
        p_user_id IN NUMBER
    );

    PROCEDURE delete_article(
        p_id IN NUMBER
    );

    PROCEDURE assign_tag(
        p_article_id IN NUMBER,
        p_tag_id     IN NUMBER
    );

    PROCEDURE assign_category(
        p_article_id  IN NUMBER,
        p_category_id IN NUMBER
    );

    PROCEDURE clear_tags(
        p_article_id IN NUMBER
    );

    PROCEDURE clear_categories(
        p_article_id IN NUMBER
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

    PROCEDURE update_article(
        p_id      IN NUMBER,
        p_title   IN VARCHAR2,
        p_text    IN CLOB,
        p_user_id IN NUMBER
    ) IS
    BEGIN
        UPDATE articles
        SET title = p_title,
            text = p_text,
            user_id = p_user_id
        WHERE id = p_id;
        IF SQL%ROWCOUNT = 0 THEN
            RAISE_APPLICATION_ERROR(-20012, 'Artículo no existe');
        END IF;
        COMMIT;
    EXCEPTION
        WHEN OTHERS THEN
            ROLLBACK;
            IF SQLCODE = -2291 THEN
                RAISE_APPLICATION_ERROR(-20002, 'Usuario no existe');
            ELSE
                RAISE;
            END IF;
    END update_article;

    PROCEDURE delete_article(
        p_id IN NUMBER
    ) IS
    BEGIN
        DELETE FROM articles WHERE id = p_id;
        IF SQL%ROWCOUNT = 0 THEN
            RAISE_APPLICATION_ERROR(-20013, 'Artículo no existe');
        END IF;
        COMMIT;
    EXCEPTION
        WHEN OTHERS THEN
            ROLLBACK;
            RAISE;
    END delete_article;

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

    PROCEDURE clear_tags(
        p_article_id IN NUMBER
    ) IS
    BEGIN
        DELETE FROM article_tags WHERE article_id = p_article_id;
        COMMIT;
    EXCEPTION
        WHEN OTHERS THEN
            ROLLBACK;
            RAISE;
    END clear_tags;

    PROCEDURE clear_categories(
        p_article_id IN NUMBER
    ) IS
    BEGIN
        DELETE FROM article_categories WHERE article_id = p_article_id;
        COMMIT;
    EXCEPTION
        WHEN OTHERS THEN
            ROLLBACK;
            RAISE;
    END clear_categories;

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


-- ---------- Comentarios (CRUD por artículo) ----------

CREATE OR REPLACE PACKAGE pkg_comments AS
    PROCEDURE add_comment(
        p_content    IN CLOB,
        p_user_id    IN NUMBER,
        p_article_id IN NUMBER
    );

    PROCEDURE update_comment(
        p_id      IN NUMBER,
        p_content IN CLOB
    );

    PROCEDURE delete_comment(
        p_id IN NUMBER
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

    PROCEDURE update_comment(
        p_id      IN NUMBER,
        p_content IN CLOB
    ) IS
    BEGIN
        UPDATE comments
        SET content = p_content
        WHERE id = p_id;
        IF SQL%ROWCOUNT = 0 THEN
            RAISE_APPLICATION_ERROR(-20014, 'Comentario no existe');
        END IF;
        COMMIT;
    EXCEPTION
        WHEN OTHERS THEN
            ROLLBACK;
            RAISE;
    END update_comment;

    PROCEDURE delete_comment(
        p_id IN NUMBER
    ) IS
    BEGIN
        DELETE FROM comments WHERE id = p_id;
        IF SQL%ROWCOUNT = 0 THEN
            RAISE_APPLICATION_ERROR(-20015, 'Comentario no existe');
        END IF;
        COMMIT;
    EXCEPTION
        WHEN OTHERS THEN
            ROLLBACK;
            RAISE;
    END delete_comment;

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


-- ---------- Categorías (CRUD) ----------

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


-- ---------- Etiquetas (CRUD) ----------

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
