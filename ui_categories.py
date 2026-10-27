"""
MoneyTracker 3.0 - Category Management Dialog
Dialog for adding and removing transaction categories.
"""

import customtkinter as ctk
from theme import *
import data_manager


class ManageCategoriesDialog(ctk.CTkToplevel):
    """Dialog to manage expense/income categories."""

    def __init__(self, master, on_save=None):
        super().__init__(master)
        self.on_save = on_save

        self.title("Manage Categories")
        self.geometry("500x600")
        self.resizable(False, False)
        self.configure(fg_color=BG_PRIMARY)
        self.transient(master)
        self.grab_set()

        self.after(10, self._center_on_parent)
        self._build_ui()

    def _center_on_parent(self):
        self.update_idletasks()
        parent = self.master
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        w = self.winfo_width()
        h = self.winfo_height()
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        self.geometry(f"+{x}+{y}")

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(20, 5))

        ctk.CTkLabel(
            header, text="📂 Manage Categories",
            font=FONT_HEADING, text_color=TEXT_PRIMARY
        ).pack(anchor="w")

        ctk.CTkLabel(
            header, text="Add or remove categories for your transactions",
            font=FONT_SMALL, text_color=TEXT_SECONDARY
        ).pack(anchor="w", pady=(2, 0))

        # Tab selector
        self._tab_var = ctk.StringVar(value="expense")
        tab_frame = ctk.CTkFrame(self, fg_color=BG_SECONDARY, corner_radius=8)
        tab_frame.pack(fill="x", padx=25, pady=(15, 0))

        self._expense_tab = ctk.CTkButton(
            tab_frame, text="Expense Categories",
            font=FONT_BODY_BOLD, height=36,
            fg_color=ACCENT_RED, hover_color=ACCENT_RED_HOVER,
            text_color="#FFFFFF", corner_radius=6,
            command=lambda: self._switch_tab("expense")
        )
        self._expense_tab.pack(side="left", fill="x", expand=True, padx=3, pady=3)

        self._income_tab = ctk.CTkButton(
            tab_frame, text="Income Categories",
            font=FONT_BODY_BOLD, height=36,
            fg_color="transparent", hover_color=BG_HOVER,
            text_color=TEXT_SECONDARY, corner_radius=6,
            command=lambda: self._switch_tab("income")
        )
        self._income_tab.pack(side="left", fill="x", expand=True, padx=3, pady=3)

        # Add new category
        add_frame = ctk.CTkFrame(self, fg_color="transparent")
        add_frame.pack(fill="x", padx=25, pady=(15, 0))

        self._new_cat_entry = ctk.CTkEntry(
            add_frame, placeholder_text="New category name...",
            font=FONT_BODY, height=40,
            fg_color=BG_INPUT, border_color=BORDER_COLOR,
            text_color=TEXT_PRIMARY, corner_radius=INPUT_CORNER_RADIUS,
            border_width=1
        )
        self._new_cat_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(
            add_frame, text="+ Add", width=80, height=40,
            font=FONT_BODY_BOLD,
            fg_color=ACCENT_BLUE, hover_color=ACCENT_BLUE_HOVER,
            text_color="#FFFFFF", corner_radius=BUTTON_CORNER_RADIUS,
            command=self._add_category
        ).pack(side="right")

        # Category list (scrollable)
        self._list_frame = ctk.CTkScrollableFrame(
            self, fg_color="transparent",
            scrollbar_button_color=BG_HOVER,
            scrollbar_button_hover_color=ACCENT_BLUE_DIM
        )
        self._list_frame.pack(fill="both", expand=True, padx=25, pady=(15, 20))

        self._refresh_list()

    def _switch_tab(self, tab: str):
        self._tab_var.set(tab)
        if tab == "expense":
            self._expense_tab.configure(fg_color=ACCENT_RED, text_color="#FFFFFF")
            self._income_tab.configure(fg_color="transparent", text_color=TEXT_SECONDARY)
        else:
            self._income_tab.configure(fg_color=ACCENT_GREEN, text_color="#FFFFFF")
            self._expense_tab.configure(fg_color="transparent", text_color=TEXT_SECONDARY)
        self._refresh_list()

    def _refresh_list(self):
        for widget in self._list_frame.winfo_children():
            widget.destroy()

        categories = data_manager.load_categories()
        tab = self._tab_var.get()
        cat_list = categories.get(tab, [])

        for cat_name in cat_list:
            row = ctk.CTkFrame(
                self._list_frame, fg_color=BG_SECONDARY,
                corner_radius=8, height=44
            )
            row.pack(fill="x", pady=2)
            row.pack_propagate(False)

            ctk.CTkLabel(
                row, text=cat_name, font=FONT_BODY,
                text_color=TEXT_PRIMARY, anchor="w"
            ).pack(side="left", padx=15, fill="x", expand=True)

            ctk.CTkButton(
                row, text="✕", width=32, height=32,
                fg_color=BG_HOVER, hover_color=ACCENT_RED_DIM,
                text_color=TEXT_MUTED, font=FONT_SMALL,
                corner_radius=6,
                command=lambda c=cat_name: self._remove_category(c)
            ).pack(side="right", padx=8)

    def _add_category(self):
        name = self._new_cat_entry.get().strip()
        if not name:
            return

        categories = data_manager.load_categories()
        tab = self._tab_var.get()

        if name not in categories.get(tab, []):
            categories.setdefault(tab, []).append(name)
            data_manager.save_categories(categories)

        self._new_cat_entry.delete(0, "end")
        self._refresh_list()

        if self.on_save:
            self.on_save()

    def _remove_category(self, name: str):
        categories = data_manager.load_categories()
        tab = self._tab_var.get()

        if name in categories.get(tab, []):
            categories[tab].remove(name)
            data_manager.save_categories(categories)

        self._refresh_list()

        if self.on_save:
            self.on_save()
