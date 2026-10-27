"""
MoneyTracker 3.0 - Add/Edit Transaction Dialog
Modern dialog for adding income or expense transactions.
"""

import customtkinter as ctk
from datetime import date, datetime
from theme import *
import data_manager


class AddTransactionDialog(ctk.CTkToplevel):
    """Dialog to add a new transaction."""

    def __init__(self, master, on_save=None, edit_transaction=None):
        super().__init__(master)

        self.on_save = on_save
        self.edit_transaction = edit_transaction
        self._result = None

        # Window setup
        self.title("Add Transaction" if not edit_transaction else "Edit Transaction")
        self.geometry("480x720")
        self.resizable(False, False)
        self.configure(fg_color=BG_PRIMARY)

        # Center on parent
        self.transient(master)
        self.grab_set()

        self.after(10, self._center_on_parent)
        self._build_ui()

        if edit_transaction:
            self._populate_from_transaction(edit_transaction)

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
        # ─── Header ──────────────────────────────
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(20, 5))

        title_text = "Edit Transaction" if self.edit_transaction else "New Transaction"
        ctk.CTkLabel(
            header, text=title_text,
            font=FONT_HEADING, text_color=TEXT_PRIMARY
        ).pack(anchor="w")

        ctk.CTkLabel(
            header, text="Record your income or expense",
            font=FONT_SMALL, text_color=TEXT_SECONDARY
        ).pack(anchor="w", pady=(2, 0))

        # ─── Type Toggle ─────────────────────────
        type_frame = ctk.CTkFrame(self, fg_color="transparent")
        type_frame.pack(fill="x", padx=30, pady=(15, 0))

        ctk.CTkLabel(
            type_frame, text="Type", font=FONT_BODY_BOLD,
            text_color=TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, 8))

        toggle_frame = ctk.CTkFrame(type_frame, fg_color=BG_SECONDARY, corner_radius=8)
        toggle_frame.pack(fill="x")

        self._type_var = ctk.StringVar(value="expense")

        self._expense_btn = ctk.CTkButton(
            toggle_frame, text="💸 Expense",
            font=FONT_BODY_BOLD, height=40,
            fg_color=ACCENT_RED, hover_color=ACCENT_RED_HOVER,
            text_color="#FFFFFF", corner_radius=6,
            command=lambda: self._set_type("expense")
        )
        self._expense_btn.pack(side="left", fill="x", expand=True, padx=3, pady=3)

        self._income_btn = ctk.CTkButton(
            toggle_frame, text="💰 Income",
            font=FONT_BODY_BOLD, height=40,
            fg_color="transparent", hover_color=BG_HOVER,
            text_color=TEXT_SECONDARY, corner_radius=6,
            command=lambda: self._set_type("income")
        )
        self._income_btn.pack(side="left", fill="x", expand=True, padx=3, pady=3)

        # ─── Amount ──────────────────────────────
        amount_frame = ctk.CTkFrame(self, fg_color="transparent")
        amount_frame.pack(fill="x", padx=30, pady=(15, 0))

        ctk.CTkLabel(
            amount_frame, text="Amount (€)", font=FONT_BODY_BOLD,
            text_color=TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, 8))

        self._amount_entry = ctk.CTkEntry(
            amount_frame, placeholder_text="0.00",
            font=FONT_AMOUNT_SMALL, height=48,
            fg_color=BG_INPUT, border_color=BORDER_COLOR,
            text_color=TEXT_PRIMARY, corner_radius=INPUT_CORNER_RADIUS,
            border_width=1
        )
        self._amount_entry.pack(fill="x")

        # ─── Category ────────────────────────────
        cat_frame = ctk.CTkFrame(self, fg_color="transparent")
        cat_frame.pack(fill="x", padx=30, pady=(15, 0))

        ctk.CTkLabel(
            cat_frame, text="Category", font=FONT_BODY_BOLD,
            text_color=TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, 8))

        categories = data_manager.load_categories()
        expense_cats = categories.get("expense", [])

        self._category_var = ctk.StringVar(value=expense_cats[0] if expense_cats else "")
        self._category_menu = ctk.CTkOptionMenu(
            cat_frame, values=expense_cats,
            variable=self._category_var,
            font=FONT_BODY, height=42,
            fg_color=BG_INPUT, button_color=BG_HOVER,
            button_hover_color=ACCENT_BLUE_DIM,
            text_color=TEXT_PRIMARY,
            dropdown_fg_color=BG_CARD,
            dropdown_text_color=TEXT_PRIMARY,
            dropdown_hover_color=BG_HOVER,
            corner_radius=INPUT_CORNER_RADIUS
        )
        self._category_menu.pack(fill="x")

        # ─── Date ────────────────────────────────
        date_frame = ctk.CTkFrame(self, fg_color="transparent")
        date_frame.pack(fill="x", padx=30, pady=(12, 0))

        ctk.CTkLabel(
            date_frame, text="Date", font=FONT_BODY_BOLD,
            text_color=TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, 8))

        self._date_entry = ctk.CTkEntry(
            date_frame, placeholder_text="YYYY-MM-DD",
            font=FONT_BODY, height=42,
            fg_color=BG_INPUT, border_color=BORDER_COLOR,
            text_color=TEXT_PRIMARY, corner_radius=INPUT_CORNER_RADIUS,
            border_width=1
        )
        self._date_entry.pack(fill="x")
        self._date_entry.insert(0, date.today().isoformat())

        # ─── Description ─────────────────────────
        desc_frame = ctk.CTkFrame(self, fg_color="transparent")
        desc_frame.pack(fill="x", padx=30, pady=(12, 0))

        ctk.CTkLabel(
            desc_frame, text="Description (optional)", font=FONT_BODY_BOLD,
            text_color=TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, 8))

        self._desc_entry = ctk.CTkEntry(
            desc_frame, placeholder_text="Add a note...",
            font=FONT_BODY, height=42,
            fg_color=BG_INPUT, border_color=BORDER_COLOR,
            text_color=TEXT_PRIMARY, corner_radius=INPUT_CORNER_RADIUS,
            border_width=1
        )
        self._desc_entry.pack(fill="x")

        # ─── Save Button ─────────────────────────
        self._save_btn = ctk.CTkButton(
            self, text="💾  Save Transaction",
            font=FONT_BODY_BOLD, height=48,
            fg_color=ACCENT_BLUE, hover_color=ACCENT_BLUE_HOVER,
            text_color="#FFFFFF", corner_radius=BUTTON_CORNER_RADIUS,
            command=self._on_save
        )
        self._save_btn.pack(fill="x", padx=30, pady=(20, 10))

        # ─── Error Label ─────────────────────────
        self._error_label = ctk.CTkLabel(
            self, text="", font=FONT_SMALL,
            text_color=ACCENT_RED
        )
        self._error_label.pack(pady=(0, 10))

    def _set_type(self, trans_type: str):
        self._type_var.set(trans_type)
        categories = data_manager.load_categories()

        if trans_type == "expense":
            self._expense_btn.configure(
                fg_color=ACCENT_RED, text_color="#FFFFFF"
            )
            self._income_btn.configure(
                fg_color="transparent", text_color=TEXT_SECONDARY
            )
            cats = categories.get("expense", [])
        else:
            self._income_btn.configure(
                fg_color=ACCENT_GREEN, text_color="#FFFFFF"
            )
            self._expense_btn.configure(
                fg_color="transparent", text_color=TEXT_SECONDARY
            )
            cats = categories.get("income", [])

        self._category_menu.configure(values=cats)
        if cats:
            self._category_var.set(cats[0])

    def _populate_from_transaction(self, t: dict):
        self._set_type(t["type"])
        self._amount_entry.delete(0, "end")
        self._amount_entry.insert(0, str(t["amount"]))
        self._category_var.set(t["category"])
        self._date_entry.delete(0, "end")
        self._date_entry.insert(0, t["date"])
        if t.get("description"):
            self._desc_entry.delete(0, "end")
            self._desc_entry.insert(0, t["description"])

    def _on_save(self):
        # Validate amount
        amount_str = self._amount_entry.get().strip()
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError()
        except ValueError:
            self._error_label.configure(text="⚠ Please enter a valid positive amount")
            return

        # Validate date
        date_str = self._date_entry.get().strip()
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            self._error_label.configure(text="⚠ Please enter a valid date (YYYY-MM-DD)")
            return

        trans_type = self._type_var.get()
        category = self._category_var.get()
        description = self._desc_entry.get().strip()

        if self.edit_transaction:
            data_manager.update_transaction(
                self.edit_transaction["id"],
                type=trans_type,
                amount=amount,
                category=category,
                description=description,
                date=date_str,
            )
        else:
            data_manager.add_transaction(
                trans_type=trans_type,
                amount=amount,
                category=category,
                description=description,
                trans_date=date_str,
            )

        if self.on_save:
            self.on_save()

        self.destroy()
