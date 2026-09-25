"""Formulario Create/Update de artículos → pkg_articles.
  C: create_article + assign_tag/assign_category
  U: update_article + clear_tags/clear_categories + reassign
"""

import customtkinter as ctk
from tkinter import messagebox
from db_connection import (
    fetch_options,
    call_procedure_returning_id,
    call_procedure,
    fetch_article_text,
    fetch_article_taxonomy_ids,
    fetch_article_user_id,
)


class NewArticleView(ctk.CTkToplevel):
    def __init__(self, master, go_back_callback=None, article=None, **kwargs):
        super().__init__(master, **kwargs)
        self.go_back_callback = go_back_callback
        self.article = article
        self.editing = article is not None and article.get("id") is not None

        self.title("Editar Artículo" if self.editing else "Publicar Nuevo Artículo")
        self.geometry("550x700")
        self.focus_force()

        self.main_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main_scroll.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(self.main_scroll, text="Título:", font=("Arial", 14, "bold")).pack(anchor="w")
        self.title_entry = ctk.CTkEntry(self.main_scroll, placeholder_text="Escribe el título...")
        self.title_entry.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(self.main_scroll, text="Texto:", font=("Arial", 14, "bold")).pack(anchor="w")
        self.text_entry = ctk.CTkTextbox(self.main_scroll, height=150)
        self.text_entry.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(self.main_scroll, text="Usuario autor:", font=("Arial", 14, "bold")).pack(anchor="w")
        self.users_list = fetch_options("users", "id", "name")
        user_names = [u[1] for u in self.users_list] if self.users_list else []
        self.combo_user = ctk.CTkComboBox(self.main_scroll, values=user_names)
        self.combo_user.pack(fill="x", pady=(0, 15))

        self.tags_visible = False
        self.cats_visible = False

        self.tags_container = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        self.tags_container.pack(fill="x", pady=(10, 5))

        self.btn_toggle_tags = ctk.CTkButton(
            self.tags_container, text="Etiquetas ►", anchor="w",
            fg_color="#333333", hover_color="#444444", text_color="white",
            command=self.toggle_tags
        )
        self.btn_toggle_tags.pack(fill="x")

        self.tags_frame = ctk.CTkScrollableFrame(self.tags_container, height=120)

        self.tag_vars = {}
        self.tags_list = fetch_options("tags", "id", "name")

        if self.tags_list:
            for tag in self.tags_list:
                var = ctk.BooleanVar()
                cb = ctk.CTkCheckBox(self.tags_frame, text=tag[1], variable=var)
                cb.pack(anchor="w", padx=5, pady=2)
                self.tag_vars[tag[0]] = var

        self.cats_container = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        self.cats_container.pack(fill="x", pady=(10, 15))

        self.btn_toggle_cats = ctk.CTkButton(
            self.cats_container, text="Categorías ►", anchor="w",
            fg_color="#333333", hover_color="#444444", text_color="white",
            command=self.toggle_cats
        )
        self.btn_toggle_cats.pack(fill="x")

        self.cats_frame = ctk.CTkScrollableFrame(self.cats_container, height=120)

        self.cat_vars = {}
        self.categories_list = fetch_options("categories", "id", "name")

        if self.categories_list:
            for cat in self.categories_list:
                var = ctk.BooleanVar()
                cb = ctk.CTkCheckBox(self.cats_frame, text=cat[1], variable=var)
                cb.pack(anchor="w", padx=5, pady=2)
                self.cat_vars[cat[0]] = var

        self.btn_guardar = ctk.CTkButton(
            self.main_scroll,
            text="Guardar cambios" if self.editing else "Publicar Artículo",
            font=("Arial", 14, "bold"), fg_color="#28a745", hover_color="#218838",
            command=self.guardar
        )
        self.btn_guardar.pack(pady=20, fill="x")

        if self.editing:
            self._prefiller()

    def _prefiller(self):
        article_id = self.article["id"]
        title = self.article.get("title") or ""
        self.title_entry.insert(0, title)

        text = self.article.get("text")
        if not text:
            try:
                text = fetch_article_text(article_id) or ""
            except Exception:
                text = ""
        self.text_entry.insert("0.0", text)

        try:
            user_id = fetch_article_user_id(article_id)
        except Exception:
            user_id = None
        if user_id is not None:
            user_name = next((u[1] for u in self.users_list if u[0] == user_id), None)
            if user_name:
                self.combo_user.set(user_name)

        try:
            tag_ids, cat_ids = fetch_article_taxonomy_ids(article_id)
        except Exception:
            tag_ids, cat_ids = [], []

        for tid, var in self.tag_vars.items():
            if tid in tag_ids:
                var.set(True)
        for cid, var in self.cat_vars.items():
            if cid in cat_ids:
                var.set(True)

        if tag_ids:
            self.toggle_tags()
        if cat_ids:
            self.toggle_cats()

    def toggle_tags(self):
        if self.tags_visible:
            self.tags_frame.pack_forget()
            self.btn_toggle_tags.configure(text="Etiquetas ►")
            self.tags_visible = False
        else:
            self.tags_frame.pack(fill="x", pady=(5, 0))
            self.btn_toggle_tags.configure(text="Etiquetas ▼")
            self.tags_visible = True

    def toggle_cats(self):
        if self.cats_visible:
            self.cats_frame.pack_forget()
            self.btn_toggle_cats.configure(text="Categorías ►")
            self.cats_visible = False
        else:
            self.cats_frame.pack(fill="x", pady=(5, 0))
            self.btn_toggle_cats.configure(text="Categorías ▼")
            self.cats_visible = True

    def guardar(self):
        titulo = self.title_entry.get().strip()
        texto = self.text_entry.get("0.0", "end").strip()
        user_name = self.combo_user.get()

        if not titulo or not texto or not user_name:
            messagebox.showerror("Error", "El título, texto y autor son obligatorios.")
            return

        user_id = next((u[0] for u in self.users_list if u[1] == user_name), None)
        if user_id is None:
            messagebox.showerror("Error", "Usuario no válido.")
            return

        selected_tags = [t_id for t_id, var in self.tag_vars.items() if var.get()]
        selected_categories = [c_id for c_id, var in self.cat_vars.items() if var.get()]

        try:
            if self.editing:
                article_id = self.article["id"]
                call_procedure(
                    "pkg_articles.update_article",
                    [article_id, titulo, texto, user_id],
                )
                call_procedure("pkg_articles.clear_tags", [article_id])
                call_procedure("pkg_articles.clear_categories", [article_id])
                for tag_id in selected_tags:
                    call_procedure("pkg_articles.assign_tag", [article_id, tag_id])
                for cat_id in selected_categories:
                    call_procedure("pkg_articles.assign_category", [article_id, cat_id])
                messagebox.showinfo("Éxito", f"Artículo actualizado (ID: {article_id}).")
            else:
                article_id = call_procedure_returning_id(
                    "pkg_articles.create_article", [titulo, texto, user_id]
                )
                if article_id:
                    for tag_id in selected_tags:
                        call_procedure("pkg_articles.assign_tag", [article_id, tag_id])
                    for cat_id in selected_categories:
                        call_procedure("pkg_articles.assign_category", [article_id, cat_id])
                    messagebox.showinfo(
                        "Éxito", f"Artículo publicado correctamente (ID: {article_id})."
                    )

            self.destroy()
            if self.go_back_callback:
                self.go_back_callback()

        except Exception as e:
            messagebox.showerror("Error de BD", str(e))


def abrir_form_publicar_articulo(parent_frame, on_saved=None):
    return NewArticleView(parent_frame, go_back_callback=on_saved)


def abrir_form_editar_articulo(parent_frame, article, on_saved=None):
    return NewArticleView(parent_frame, go_back_callback=on_saved, article=article)
