"""
views/new_article.py
Formulario de publicación de artículo. 
Actualizado con CustomTkinter: se reemplazan los Listbox antiguos por 
paneles con Checkboxes modernos y scroll automático.
"""

import customtkinter as ctk
from tkinter import messagebox
from db_connection import fetch_options, call_procedure_returning_id, call_procedure

# Cambiamos CTkFrame por CTkToplevel para que sea una ventana independiente
class NewArticleView(ctk.CTkToplevel):
    def __init__(self, master, go_back_callback=None, **kwargs):
        super().__init__(master, **kwargs)
        self.go_back_callback = go_back_callback
        
        # Configuración de la nueva ventana flotante
        self.title("Publicar Nuevo Artículo")
        self.geometry("550x700")
        self.focus_force() # Obliga a la ventana a aparecer al frente

        # 1. SCROLL MAESTRO
        self.main_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main_scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Campos principales ---
        ctk.CTkLabel(self.main_scroll, text="Título:", font=("Arial", 14, "bold")).pack(anchor="w")
        self.title_entry = ctk.CTkEntry(self.main_scroll, placeholder_text="Escribe el título...")
        self.title_entry.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(self.main_scroll, text="Texto:", font=("Arial", 14, "bold")).pack(anchor="w")
        self.text_entry = ctk.CTkTextbox(self.main_scroll, height=150)
        self.text_entry.pack(fill="x", pady=(0, 15))

        # --- Usuario Autor ---
        ctk.CTkLabel(self.main_scroll, text="Usuario autor:", font=("Arial", 14, "bold")).pack(anchor="w")
        self.users_list = fetch_options("users", "id", "name")
        user_names = [u[1] for u in self.users_list] if self.users_list else []
        self.combo_user = ctk.CTkComboBox(self.main_scroll, values=user_names)
        self.combo_user.pack(fill="x", pady=(0, 15))

        # Variables para acordeón manual
        self.tags_visible = False
        self.cats_visible = False

        # --- 2. SECCIÓN COLAPSABLE DE ETIQUETAS ---
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

        # --- 3. SECCIÓN COLAPSABLE DE CATEGORÍAS ---
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

        # --- Botón Guardar ---
        self.btn_guardar = ctk.CTkButton(
            self.main_scroll, text="Publicar Artículo", 
            font=("Arial", 14, "bold"), fg_color="#28a745", hover_color="#218838",
            command=self.guardar
        )
        self.btn_guardar.pack(pady=20, fill="x")

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

        try:
            article_id = call_procedure_returning_id("pkg_articles.create_article", [titulo, texto, user_id])

            if article_id:
                selected_tags = [t_id for t_id, var in self.tag_vars.items() if var.get()]
                for tag_id in selected_tags:
                    call_procedure("pkg_articles.assign_tag", [article_id, tag_id])

                selected_categories = [c_id for c_id, var in self.cat_vars.items() if var.get()]
                for cat_id in selected_categories:
                    call_procedure("pkg_articles.assign_category", [article_id, cat_id])

                messagebox.showinfo("Éxito", f"Artículo publicado correctamente (ID: {article_id}).")
                
                # Cerramos automáticamente esta ventana flotante tras publicar
                self.destroy()

                # Recargamos la vista del main_gui por debajo
                if self.go_back_callback:
                    self.go_back_callback()
                    
        except Exception as e:
            messagebox.showerror("Error de BD", str(e))

# --- Función puente para main_gui.py ---
def abrir_form_publicar_articulo(parent_frame, on_saved=None):
    # Ya no destruimos la ventana base. Solo abrimos la nueva ventana encima.
    vista = NewArticleView(parent_frame, go_back_callback=on_saved)
    return vista