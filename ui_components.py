"""
MoneyTracker 3.0 - UI Components
Reusable modern UI widgets.
"""

import customtkinter as ctk
from theme import *


class GlassCard(ctk.CTkFrame):
    """A card-style container with subtle border and rounded corners."""

    def __init__(self, master, **kwargs):
        kwargs.setdefault("fg_color", BG_CARD)
        kwargs.setdefault("corner_radius", CORNER_RADIUS)
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("border_color", BORDER_COLOR)
        super().__init__(master, **kwargs)


class StatCard(GlassCard):
    """A stat display card showing a label, value, and optional icon."""

    def __init__(self, master, title: str, value: str, icon: str = "",
                 accent_color: str = ACCENT_BLUE, **kwargs):
        super().__init__(master, **kwargs)

        self._accent = accent_color

        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=CARD_PADDING, pady=CARD_PADDING)

        # Top row with icon and title
        top = ctk.CTkFrame(inner, fg_color="transparent")
        top.pack(fill="x", anchor="w")

        if icon:
            ctk.CTkLabel(
                top, text=icon, font=(FONT_FAMILY, 18),
                text_color=accent_color
            ).pack(side="left")

        ctk.CTkLabel(
            top, text=title, font=FONT_SMALL,
            text_color=TEXT_SECONDARY
        ).pack(side="left", padx=(8, 0))

        # Value
        self._value_label = ctk.CTkLabel(
            inner, text=value, font=FONT_AMOUNT,
            text_color=TEXT_PRIMARY, anchor="w"
        )
        self._value_label.pack(fill="x", pady=(8, 0), anchor="w")

    def set_value(self, value: str):
        self._value_label.configure(text=value)


class TransactionRow(ctk.CTkFrame):
    """A single transaction row in a list."""

    def __init__(self, master, transaction: dict, on_delete=None, **kwargs):
        kwargs.setdefault("fg_color", BG_SECONDARY)
        kwargs.setdefault("corner_radius", 8)
        super().__init__(master, **kwargs)

        self.transaction = transaction
        is_income = transaction["type"] == "income"
        color = ACCENT_GREEN if is_income else ACCENT_RED
        sign = "+" if is_income else "-"

        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="x", expand=True, padx=16, pady=10)

        # Left: category & description
        left = ctk.CTkFrame(inner, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            left, text=transaction["category"],
            font=FONT_BODY_BOLD, text_color=TEXT_PRIMARY, anchor="w"
        ).pack(fill="x")

        if transaction.get("description"):
            ctk.CTkLabel(
                left, text=transaction["description"],
                font=FONT_SMALL, text_color=TEXT_SECONDARY, anchor="w"
            ).pack(fill="x")

        # Right: amount & delete
        right = ctk.CTkFrame(inner, fg_color="transparent")
        right.pack(side="right")

        ctk.CTkLabel(
            right, text=f"{sign}€{transaction['amount']:.2f}",
            font=FONT_BODY_BOLD, text_color=color
        ).pack(side="left", padx=(0, 8))

        if on_delete:
            del_btn = ctk.CTkButton(
                right, text="✕", width=28, height=28,
                fg_color=BG_HOVER, hover_color=ACCENT_RED_DIM,
                text_color=TEXT_MUTED, font=FONT_SMALL,
                corner_radius=6,
                command=lambda: on_delete(transaction["id"])
            )
            del_btn.pack(side="left")


class FloatingActionButton(ctk.CTkButton):
    """A large round floating action button."""

    def __init__(self, master, text="+", command=None, **kwargs):
        kwargs.setdefault("width", 56)
        kwargs.setdefault("height", 56)
        kwargs.setdefault("corner_radius", 28)
        kwargs.setdefault("fg_color", ACCENT_BLUE)
        kwargs.setdefault("hover_color", ACCENT_BLUE_HOVER)
        kwargs.setdefault("text_color", "#FFFFFF")
        kwargs.setdefault("font", (FONT_FAMILY, 24, "bold"))
        super().__init__(master, text=text, command=command, **kwargs)


class PieChart(ctk.CTkFrame):
    """A simple pie chart drawn on a Canvas with a legend."""
    
    def __init__(self, master, title: str, **kwargs):
        kwargs.setdefault("fg_color", BG_CARD)
        kwargs.setdefault("corner_radius", CORNER_RADIUS)
        super().__init__(master, **kwargs)
        
        self.colors = [
            ACCENT_BLUE, ACCENT_PURPLE, ACCENT_ORANGE, 
            ACCENT_YELLOW, ACCENT_GREEN, ACCENT_RED,
            "#FF99CC", "#99FF99", "#99CCFF", "#FFCC99"
        ]
        
        # Title
        self.title_label = ctk.CTkLabel(
            self, text=title, font=FONT_SUBHEADING, text_color=TEXT_PRIMARY
        )
        self.title_label.pack(anchor="w", padx=20, pady=(15, 5))
        
        # Content frame (canvas + legend)
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Canvas - Increased size
        self.canvas_size = 200
        self.canvas = ctk.CTkCanvas(
            self.content_frame, width=self.canvas_size, height=self.canvas_size,
            bg=BG_CARD, highlightthickness=0
        )
        self.canvas.pack(side="top", pady=(0, 15))
        
        # Legend (scrollable if many items) - Moved to bottom
        self.legend_frame = ctk.CTkScrollableFrame(
            self.content_frame, fg_color="transparent",
            scrollbar_button_color=BG_HOVER,
            scrollbar_button_hover_color=ACCENT_BLUE_DIM,
            height=100
        )
        self.legend_frame.pack(side="top", fill="both", expand=True)
        
        self.empty_label = ctk.CTkLabel(
            self.content_frame, text="No data available",
            font=FONT_BODY, text_color=TEXT_MUTED
        )
        
    def set_data(self, data: dict):
        """data format: {'Category': amount, ...}"""
        self.canvas.delete("all")
        for w in self.legend_frame.winfo_children():
            w.destroy()
            
        if not data or sum(data.values()) == 0:
            self.canvas.pack_forget()
            self.legend_frame.pack_forget()
            self.empty_label.pack(expand=True)
            return
            
        self.empty_label.pack_forget()
        self.canvas.pack(side="top", pady=(0, 15))
        self.legend_frame.pack(side="top", fill="both", expand=True)
        
        total = sum(data.values())
        sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)
        
        start_angle = 90
        
        for i, (name, amount) in enumerate(sorted_data):
            percentage = (amount / total) * 100
            extent = (amount / total) * 360
            if extent >= 360:
                extent = 359.99
            color = self.colors[i % len(self.colors)]
            
            # Draw slice
            self.canvas.create_arc(
                10, 10, self.canvas_size-10, self.canvas_size-10,
                start=start_angle, extent=extent,
                fill=color, outline=BG_CARD, width=2
            )
            
            start_angle += extent
            
            # Draw legend item
            row = ctk.CTkFrame(self.legend_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)
            
            # Color box
            color_box = ctk.CTkFrame(row, width=12, height=12, fg_color=color, corner_radius=3)
            color_box.pack(side="left", padx=(0, 8))
            color_box.pack_propagate(False)
            
            # Label
            ctk.CTkLabel(
                row, text=name, font=FONT_SMALL, text_color=TEXT_PRIMARY
            ).pack(side="left")
            
            # Value & %
            ctk.CTkLabel(
                row, text=f"€{amount:.2f} ({percentage:.0f}%)",
                font=FONT_TINY, text_color=TEXT_SECONDARY
            ).pack(side="right")

