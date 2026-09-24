"""Construcción de etiquetas visuales para categorías y tags."""

import tkinter as tk

TAG_COLORS = {"bg": "#e1ecf4", "fg": "#39739d"}
CATEGORY_COLORS = {"bg": "#fbe7c6", "fg": "#a3660a"}


def make_chip(parent, text, kind="tag"):
    """Crea un ``Label`` con color diferenciado según el tipo de taxonomía."""
    colors = TAG_COLORS if kind == "tag" else CATEGORY_COLORS
    return tk.Label(
        parent,
        text=text,
        bg=colors["bg"],
        fg=colors["fg"],
        font=("Segoe UI", 8, "bold"),
        padx=8,
        pady=2,
        bd=0,
    )
