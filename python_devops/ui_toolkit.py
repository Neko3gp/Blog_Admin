"""Fallback UI si Tcl/Tk < 8.6 (CustomTkinter no funciona). No es el path normal en macOS con install_python.sh."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk


def _tcl_ok() -> bool:
    try:
        parts = tk.Tcl().eval("info patchlevel").split(".")
        major, minor = int(parts[0]), int(parts[1])
        return (major, minor) >= (8, 6)
    except Exception:
        return False


USE_CUSTOMTKINTER = _tcl_ok()


if USE_CUSTOMTKINTER:
    import customtkinter as ctk  # noqa: F401
else:
    import theme as _theme

    def _resolve_bg(master, fg_color):
        if fg_color is None:
            return _theme.CONTENT_BG
        if fg_color == "transparent":
            try:
                return master.cget("bg")
            except Exception:
                return _theme.CONTENT_BG
        return fg_color

    class _CTkFont:
        def __init__(self, family="Helvetica", size=12, weight="normal", slant="roman"):
            self.family = family or "Helvetica"
            self.size = size or 12
            self.weight = weight if weight in ("normal", "bold") else "normal"
            self.slant = "italic" if slant in ("italic", "oblique") else "roman"

        def as_tuple(self):
            parts = [self.family, self.size]
            if self.weight == "bold":
                parts.append("bold")
            if self.slant == "italic":
                parts.append("italic")
            return tuple(parts)

    def _font(font=None, size=None, weight=None):
        if isinstance(font, _CTkFont):
            return font.as_tuple()
        if font is not None:
            return font
        style = ["Helvetica", size or 12]
        if weight == "bold":
            style.append("bold")
        return tuple(style)

    class CTk(tk.Tk):
        def __init__(self, fg_color=None, **kwargs):
            super().__init__(**kwargs)
            self.configure(bg=_resolve_bg(self, fg_color or _theme.CONTENT_BG))

        def configure(self, **kwargs):
            if "fg_color" in kwargs:
                kwargs["bg"] = _resolve_bg(self, kwargs.pop("fg_color"))
            return super().configure(**kwargs)

    class CTkToplevel(tk.Toplevel):
        def __init__(self, master=None, fg_color=None, **kwargs):
            super().__init__(master, **kwargs)
            self.configure(bg=_resolve_bg(self, fg_color or _theme.PANEL_BG))

    class CTkFrame(tk.Frame):
        def __init__(
            self,
            master=None,
            fg_color=None,
            corner_radius=None,
            border_width=0,
            border_color=None,
            width=None,
            height=None,
            **kwargs,
        ):
            bg = _resolve_bg(master, fg_color)
            kw = {"bg": bg}
            if width is not None:
                kw["width"] = width
            if height is not None:
                kw["height"] = height
            if border_width:
                kw["highlightthickness"] = border_width
                kw["highlightbackground"] = border_color or _theme.PANEL_BORDER
                kw["bd"] = 0
            kw.update(kwargs)
            super().__init__(master, **kw)

        def configure(self, **kwargs):
            if "fg_color" in kwargs:
                kwargs["bg"] = _resolve_bg(self.master, kwargs.pop("fg_color"))
            if "hover_color" in kwargs:
                kwargs.pop("hover_color")
            if "text_color" in kwargs:
                kwargs.pop("text_color")
            return super().configure(**kwargs)

        def cget(self, key):
            if key == "fg_color":
                return super().cget("bg")
            return super().cget(key)

    class CTkLabel(tk.Label):
        def __init__(
            self,
            master=None,
            text="",
            text_color=None,
            fg_color=None,
            font=None,
            anchor="w",
            justify="left",
            wraplength=0,
            image=None,
            compound="left",
            padx=0,
            pady=0,
            **kwargs,
        ):
            bg = _resolve_bg(master, fg_color) if fg_color is not None else _resolve_bg(master, "transparent")
            super().__init__(
                master,
                text=text,
                fg=text_color or _theme.CONTENT_FG,
                bg=bg,
                font=_font(font),
                anchor=anchor,
                justify=justify,
                wraplength=wraplength,
                image=image,
                compound=compound,
                padx=padx,
                pady=pady,
                **kwargs,
            )

        def configure(self, **kwargs):
            if "text_color" in kwargs:
                kwargs["fg"] = kwargs.pop("text_color")
            if "fg_color" in kwargs:
                kwargs["bg"] = _resolve_bg(self.master, kwargs.pop("fg_color"))
            if "font" in kwargs and isinstance(kwargs["font"], _CTkFont):
                kwargs["font"] = kwargs["font"].as_tuple()
            return super().configure(**kwargs)

    class CTkButton(tk.Button):
        def __init__(
            self,
            master=None,
            text="",
            command=None,
            fg_color=None,
            hover_color=None,
            text_color=None,
            font=None,
            width=None,
            height=None,
            corner_radius=None,
            border_width=0,
            border_color=None,
            anchor="center",
            **kwargs,
        ):
            bg = fg_color if fg_color and fg_color != "transparent" else _theme.BTN_SECONDARY_BG
            if fg_color == "transparent":
                bg = _resolve_bg(master, "transparent")
            kw = {
                "text": text,
                "command": command,
                "fg": text_color or _theme.BTN_SECONDARY_FG,
                "bg": bg,
                "activebackground": hover_color or bg,
                "activeforeground": text_color or _theme.BTN_SECONDARY_FG,
                "font": _font(font),
                "relief": "flat",
                "bd": border_width or 0,
                "highlightthickness": 0,
                "anchor": anchor,
                "cursor": "hand2",
            }
            if width is not None:
                # CTk width is roughly pixels; tk Button width is chars
                kw["width"] = max(1, int(width / 10)) if width > 20 else width
            if border_color and border_width:
                kw["highlightbackground"] = border_color
                kw["highlightthickness"] = border_width
            kw.update(kwargs)
            super().__init__(master, **kw)
            self._hover = hover_color or bg
            self._bg = bg
            self.bind("<Enter>", lambda e: self.configure(bg=self._hover))
            self.bind("<Leave>", lambda e: self.configure(bg=self._bg))

        def configure(self, **kwargs):
            if "fg_color" in kwargs:
                color = kwargs.pop("fg_color")
                if color == "transparent":
                    color = _resolve_bg(self.master, "transparent")
                kwargs["bg"] = color
                self._bg = color
            if "hover_color" in kwargs:
                self._hover = kwargs.pop("hover_color")
                kwargs["activebackground"] = self._hover
            if "text_color" in kwargs:
                kwargs["fg"] = kwargs.pop("text_color")
                kwargs["activeforeground"] = kwargs["fg"]
            if "font" in kwargs and isinstance(kwargs["font"], _CTkFont):
                kwargs["font"] = kwargs["font"].as_tuple()
            return super().configure(**kwargs)

    class CTkEntry(tk.Entry):
        def __init__(
            self,
            master=None,
            fg_color=None,
            border_color=None,
            text_color=None,
            width=20,
            **kwargs,
        ):
            super().__init__(
                master,
                bg=fg_color or _theme.ENTRY_BG,
                fg=text_color or _theme.ENTRY_FG,
                insertbackground=text_color or _theme.ENTRY_FG,
                relief="flat",
                highlightthickness=1,
                highlightbackground=border_color or _theme.ENTRY_BORDER,
                highlightcolor=border_color or _theme.ENTRY_BORDER,
                width=width if width and width < 100 else max(20, int((width or 200) / 8)),
                **kwargs,
            )

    class CTkTextbox(tk.Text):
        def __init__(
            self,
            master=None,
            fg_color=None,
            border_color=None,
            text_color=None,
            height=5,
            border_width=1,
            **kwargs,
        ):
            super().__init__(
                master,
                bg=fg_color or _theme.ENTRY_BG,
                fg=text_color or _theme.ENTRY_FG,
                insertbackground=text_color or _theme.ENTRY_FG,
                relief="flat",
                highlightthickness=border_width or 0,
                highlightbackground=border_color or _theme.ENTRY_BORDER,
                height=max(3, int(height / 20)) if height and height > 20 else height,
                **kwargs,
            )

        def get(self, index1="1.0", index2=tk.END):
            return super().get(index1, index2)

    class CTkComboBox(ttk.Combobox):
        def __init__(
            self,
            master=None,
            values=None,
            command=None,
            state="readonly",
            width=16,
            fg_color=None,
            border_color=None,
            text_color=None,
            dropdown_fg_color=None,
            dropdown_text_color=None,
            button_color=None,
            button_hover_color=None,
            **kwargs,
        ):
            self._command = command
            super().__init__(master, values=values or [], state=state, width=width, **kwargs)
            if command:
                self.bind("<<ComboboxSelected>>", lambda e: self._command(self.get()))

        def set(self, value):
            self.set(value) if False else None  # placate linters
            super().set(value)

        def configure(self, **kwargs):
            if "values" in kwargs:
                return super().configure(values=kwargs.pop("values"), **{
                    k: v for k, v in kwargs.items()
                    if k in ("state", "width", "textvariable")
                })
            # Ignore CTk color kwargs
            for key in list(kwargs):
                if key.endswith("_color") or key.startswith("dropdown") or key.startswith("button"):
                    kwargs.pop(key)
            if "command" in kwargs:
                self._command = kwargs.pop("command")
            return super().configure(**kwargs)

    class CTkScrollableFrame(CTkFrame):
        def __init__(self, master=None, fg_color=None, scrollbar_button_color=None,
                     scrollbar_button_hover_color=None, **kwargs):
            super().__init__(master, fg_color=fg_color, **kwargs)
            bg = _resolve_bg(master, fg_color)
            self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0)
            self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
            self._inner = CTkFrame(self.canvas, fg_color=fg_color or bg)
            self._inner.bind(
                "<Configure>",
                lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
            )
            self._window = self.canvas.create_window((0, 0), window=self._inner, anchor="nw")
            self.canvas.configure(yscrollcommand=self.scrollbar.set)
            self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self._window, width=e.width))
            self.canvas.pack(side="left", fill="both", expand=True)
            self.scrollbar.pack(side="right", fill="y")

        def winfo_children(self):
            return self._inner.winfo_children()

        def pack_propagate(self, flag):
            return self._inner.pack_propagate(flag)

        # Proxy geometry for children: they should parent to inner
        def __getattr__(self, name):
            # Allow CTkScrollableFrame to be used as parent by remapping
            raise AttributeError(name)

    # Make packing into scrollable frame put widgets on inner
    _orig_pack = tk.Pack.pack

    class _ScrollParent(CTkScrollableFrame):

        def pack(self, *args, **kwargs):
            return tk.Frame.pack(self, *args, **kwargs)

    # Fix: children are created with master=scroll_area; redirect via override
    class CTkScrollableFrame(CTkFrame):
        def __init__(self, master=None, fg_color=None, scrollbar_button_color=None,
                     scrollbar_button_hover_color=None, **kwargs):
            super().__init__(master, fg_color=fg_color, **kwargs)
            bg = self.cget("bg")
            self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0)
            self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
            self.inner = CTkFrame(self.canvas, fg_color=bg)
            self.inner.bind(
                "<Configure>",
                lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
            )
            self._window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
            self.canvas.configure(yscrollcommand=self.scrollbar.set)
            self.canvas.bind(
                "<Configure>",
                lambda e: self.canvas.itemconfig(self._window, width=e.width),
            )
            self.canvas.pack(side="left", fill="both", expand=True)
            self.scrollbar.pack(side="right", fill="y")

            # Monkey-patch: when views do Widget(self.scroll_area, ...), they
            # pass this frame as master. We intercept via a proxy property used
            # by feeding children — views use self.scroll_area as parent, so
            # we override __class__ identity by making pack/children use inner.
            self._proxy_master = self.inner

        def winfo_children(self):
            return self.inner.winfo_children()

    class CTkSegmentedButton(CTkFrame):
        def __init__(self, master=None, values=None, variable=None, command=None, **kwargs):
            # strip CTk color kwargs
            for k in list(kwargs):
                if "color" in k:
                    kwargs.pop(k)
            super().__init__(master, fg_color=_theme.ENTRY_BG)
            self._values = values or []
            self._variable = variable or tk.StringVar(value=self._values[0] if self._values else "")
            self._command = command
            self._buttons = []
            for value in self._values:
                btn = CTkButton(
                    self,
                    text=value,
                    command=lambda v=value: self._select(v),
                    fg_color=_theme.ENTRY_BG,
                    text_color=_theme.PAGE_FG,
                    hover_color=_theme.SIDEBAR_HOVER_BG,
                )
                btn.pack(side="left", padx=2)
                self._buttons.append((value, btn))
            self._refresh()

        def _select(self, value):
            self._variable.set(value)
            self._refresh()
            if self._command:
                self._command(value)

        def _refresh(self):
            current = self._variable.get()
            for value, btn in self._buttons:
                if value == current:
                    btn.configure(fg_color=_theme.SIDEBAR_SELECTED_BG, text_color=_theme.SIDEBAR_SELECTED_TEXT)
                else:
                    btn.configure(fg_color=_theme.ENTRY_BG, text_color=_theme.PAGE_FG)

    class StringVar(tk.StringVar):
        pass

    class _Compat:
        CTk = CTk
        CTkToplevel = CTkToplevel
        CTkFrame = CTkFrame
        CTkLabel = CTkLabel
        CTkButton = CTkButton
        CTkEntry = CTkEntry
        CTkTextbox = CTkTextbox
        CTkComboBox = CTkComboBox
        CTkScrollableFrame = CTkScrollableFrame
        CTkSegmentedButton = CTkSegmentedButton
        CTkFont = _CTkFont
        StringVar = StringVar

        @staticmethod
        def set_appearance_mode(_mode):
            return None

        @staticmethod
        def set_default_color_theme(_theme_name):
            return None

    ctk = _Compat()
