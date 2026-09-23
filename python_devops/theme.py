"""
theme.py
Paleta de colores centralizada de toda la GUI. Cambia un valor aquí y se
refleja en todas las vistas.

Los colores van EN PAREJAS fondo/texto (ej. PAGE_BG + PAGE_FG). Si cambias
un fondo, revisa que su texto emparejado siga teniendo buen contraste —
por eso viven juntos aquí y no sueltos en cada archivo.
"""

# ---------- Superficie de "página" ----------
# Fondo del feed, el detalle de artículo, y del fondo detrás de las listas.
# Este es el que edita quien quiera un modo oscuro/claro distinto.
PAGE_BG = "#ffffff"
# Texto que va SOBRE PAGE_BG (títulos de tarjetas, cuerpo de artículos).
# Si vuelves PAGE_BG oscuro, sube este a un tono claro para que no
# desaparezca el texto (igual que le pasó al panel antes de este cambio).
PAGE_FG = "#1a1a1b"

# Fondo del área de contenido, detrás de las tarjetas del feed.
CONTENT_BG = "#f6f7f8"
CONTENT_FG = "#1a1a1b"

# ---------- Panel / tarjetas secundarias ----------
# Fondo fijo del panel lateral de formularios (Nuevo usuario, Nueva
# categoría, etc.) y de las filas de listas y comentarios. A propósito NO
# depende de PAGE_BG: así el panel siempre se distingue como una "tarjeta"
# aparte, sin importar qué tan oscuro pongas el fondo de página.
PANEL_BG = "#f6f7f8"
PANEL_FG = "#1a1a1b"
PANEL_BORDER = "#d8dadd"

# Fondo/texto de los campos de captura (Entry/Text) dentro de esos paneles.
ENTRY_BG = "#ffffff"
ENTRY_FG = "#1a1a1b"

# Texto secundario (metadatos, fechas, autores) — funciona razonablemente
# sobre fondos claros u oscuros de esta paleta.
TEXT_MUTED = "#7c7c7c"
TEXT_PLACEHOLDER = "#8a8a8a"

# Bordes de tarjeta
CARD_BORDER = "#e3e3e3"

# ---------- Sidebar de navegación ----------
SIDEBAR_BG = "#1a1a1b"
SIDEBAR_TEXT = "#e6e6e6"
SIDEBAR_TEXT_ACTIVE = "#ffffff"
SIDEBAR_HOVER_BG = "#343536"
SIDEBAR_SELECTED_BG = "#3a6df0"
SIDEBAR_DIVIDER = "#343536"
SIDEBAR_MUTED = "#8a8a8a"
