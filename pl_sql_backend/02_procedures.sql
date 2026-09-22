-- =====================================================
-- 02_procedures.sql
-- Administrador de Blog — Bases de Datos Avanzadas
-- Integrante 2 (Samuel): Backend PL/SQL
--
-- ESTE ES UN ESQUELETO. Las firmas (nombres y parámetros) ya
-- siguen el Contrato de Nombres del documento del proyecto —
-- NO cambiarlas, porque Python ya las va a invocar con estos
-- nombres exactos. Rellenar la lógica donde dice TODO.
-- =====================================================


-- ---------- PKG_USERS ----------

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
        -- TODO Samuel: INSERT INTO users(name, email) VALUES (p_name, p_email);
        -- TODO Samuel: capturar DUP_VAL_ON_INDEX (email duplicado, es UNIQUE)
        --              y relanzar con RAISE_APPLICATION_ERROR(-20001, 'Email ya registrado');
        NULL;
    END insert_user;

    PROCEDURE get_all_users(
        p_cursor OUT SYS_REFCURSOR
    ) IS
    BEGIN
        -- TODO Samuel: OPEN p_cursor FOR SELECT id, name, email FROM users ORDER BY id;
        NULL;
    END get_all_users;

END pkg_users;
/


-- ---------- PKG_ARTICLES ----------

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
        -- TODO Samuel: INSERT INTO articles(title, text, user_id)
        --              VALUES (p_title, p_text, p_user_id)
        --              RETURNING id INTO p_article_id;
        -- TODO Samuel: capturar violación de FK (user_id inexistente) con
        --              RAISE_APPLICATION_ERROR
        NULL;
    END create_article;

    PROCEDURE assign_tag(
        p_article_id IN NUMBER,
        p_tag_id     IN NUMBER
    ) IS
    BEGIN
        -- TODO Samuel: INSERT INTO article_tags(article_id, tag_id)
        --              VALUES (p_article_id, p_tag_id);
        NULL;
    END assign_tag;

    PROCEDURE assign_category(
        p_article_id  IN NUMBER,
        p_category_id IN NUMBER
    ) IS
    BEGIN
        -- TODO Samuel: INSERT INTO article_categories(article_id, category_id)
        --              VALUES (p_article_id, p_category_id);
        NULL;
    END assign_category;

    PROCEDURE get_all_articles(
        p_cursor OUT SYS_REFCURSOR
    ) IS
    BEGIN
        -- TODO Samuel: OPEN p_cursor FOR SELECT id, title, date, user_id FROM articles ORDER BY id;
        NULL;
    END get_all_articles;

END pkg_articles;
/


-- ---------- PKG_COMMENTS ----------

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
        -- TODO Samuel: INSERT INTO comments(content, user_id, article_id)
        --              VALUES (p_content, p_user_id, p_article_id);
        NULL;
    END add_comment;

    PROCEDURE get_by_article(
        p_article_id IN  NUMBER,
        p_cursor     OUT SYS_REFCURSOR
    ) IS
    BEGIN
        -- TODO Samuel: OPEN p_cursor FOR
        --   SELECT id, content, creation_date, user_id
        --   FROM comments WHERE article_id = p_article_id ORDER BY creation_date;
        NULL;
    END get_by_article;

END pkg_comments;
/


-- ---------- PKG_CATEGORIES ----------

CREATE OR REPLACE PACKAGE pkg_categories AS
    PROCEDURE insert_category(
        p_name IN VARCHAR2,
        p_url  IN VARCHAR2
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
        -- TODO Samuel: INSERT INTO categories(name, url) VALUES (p_name, p_url);
        NULL;
    END insert_category;

    PROCEDURE get_all(
        p_cursor OUT SYS_REFCURSOR
    ) IS
    BEGIN
        -- TODO Samuel: OPEN p_cursor FOR SELECT id, name, url FROM categories ORDER BY id;
        NULL;
    END get_all;

END pkg_categories;
/


-- ---------- PKG_TAGS ----------

CREATE OR REPLACE PACKAGE pkg_tags AS
    PROCEDURE insert_tag(
        p_name IN VARCHAR2,
        p_url  IN VARCHAR2
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
        -- TODO Samuel: INSERT INTO tags(name, url) VALUES (p_name, p_url);
        NULL;
    END insert_tag;

    PROCEDURE get_all(
        p_cursor OUT SYS_REFCURSOR
    ) IS
    BEGIN
        -- TODO Samuel: OPEN p_cursor FOR SELECT id, name, url FROM tags ORDER BY id;
        NULL;
    END get_all;

END pkg_tags;
/
