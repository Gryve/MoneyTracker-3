"""
MoneyTracker 3.0 - Main Application
Modern expense/income tracker with calendar view and dashboard.
"""

import customtkinter as ctk
from datetime import date, datetime, timedelta
import calendar as cal_module
from theme import *
import data_manager
from ui_components import GlassCard, StatCard, TransactionRow, FloatingActionButton, PieChart
from ui_dialogs import AddTransactionDialog
from ui_categories import ManageCategoriesDialog


class MoneyTrackerApp(ctk.CTk):
    """Main application window."""

    def __init__(self):
        super().__init__()

        # Window setup
        self.title("MoneyTracker 3.0")
        self.geometry("1200x780")
        self.minsize(1000, 650)
        self.configure(fg_color=BG_DARK)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # State
        today = date.today()
        self._current_year = today.year
        self._current_month = today.month
        self._selected_date = today.isoformat()

        # Dashboard has its own month selector
        self._dash_year = today.year
        self._dash_month = today.month

        # Year overview
        self._view_year = today.year

        # Build UI
        self._build_sidebar()
        self._build_main_area()

        # Initial data load
        self._refresh_all()

    # ══════════════════════════════════════════
    #  SIDEBAR
    # ══════════════════════════════════════════
    def _build_sidebar(self):
        self._sidebar = ctk.CTkFrame(
            self, width=SIDEBAR_WIDTH, fg_color=BG_PRIMARY,
            corner_radius=0, border_width=0
        )
        self._sidebar.pack(side="left", fill="y")
        self._sidebar.pack_propagate(False)

        # Logo area
        logo_frame = ctk.CTkFrame(self._sidebar, fg_color="transparent")
        logo_frame.pack(fill="x", padx=20, pady=(25, 5))

        ctk.CTkLabel(
            logo_frame, text="💎", font=(FONT_FAMILY, 32)
        ).pack(side="left")

        title_frame = ctk.CTkFrame(logo_frame, fg_color="transparent")
        title_frame.pack(side="left", padx=(10, 0))

        ctk.CTkLabel(
            title_frame, text="MoneyTracker",
            font=(FONT_FAMILY, 18, "bold"), text_color=TEXT_PRIMARY
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_frame, text="v3.0",
            font=FONT_TINY, text_color=TEXT_MUTED
        ).pack(anchor="w")

        # Divider
        ctk.CTkFrame(
            self._sidebar, fg_color=BORDER_COLOR, height=1
        ).pack(fill="x", padx=20, pady=(20, 15))

        # Nav buttons
        nav_frame = ctk.CTkFrame(self._sidebar, fg_color="transparent")
        nav_frame.pack(fill="x", padx=12)

        self._nav_buttons = {}
        nav_items = [
            ("📊", "Dashboard", "dashboard"),
            ("📝", "Transactions", "transactions"),
            ("📅", "Calendar", "calendar"),
            ("📆", "Year Overview", "year"),
        ]

        for icon, label, key in nav_items:
            btn = ctk.CTkButton(
                nav_frame,
                text=f"  {icon}  {label}",
                font=FONT_BODY, height=42,
                fg_color="transparent",
                hover_color=BG_HOVER,
                text_color=TEXT_SECONDARY,
                anchor="w", corner_radius=8,
                command=lambda k=key: self._switch_view(k)
            )
            btn.pack(fill="x", pady=1)
            self._nav_buttons[key] = btn

        # Initially select dashboard
        self._current_view = "dashboard"
        self._nav_buttons["dashboard"].configure(
            fg_color=BG_SECONDARY, text_color=TEXT_PRIMARY
        )

        # Divider
        ctk.CTkFrame(
            self._sidebar, fg_color=BORDER_COLOR, height=1
        ).pack(fill="x", padx=20, pady=15)

        # Quick actions
        ctk.CTkLabel(
            self._sidebar, text="QUICK ACTIONS",
            font=FONT_TINY, text_color=TEXT_MUTED
        ).pack(anchor="w", padx=20, pady=(0, 8))

        actions_frame = ctk.CTkFrame(self._sidebar, fg_color="transparent")
        actions_frame.pack(fill="x", padx=12)

        ctk.CTkButton(
            actions_frame,
            text="  ➕  Add Transaction",
            font=FONT_BODY, height=42,
            fg_color=ACCENT_BLUE_DIM,
            hover_color=ACCENT_BLUE,
            text_color=ACCENT_BLUE,
            anchor="w", corner_radius=8,
            command=self._open_add_transaction
        ).pack(fill="x", pady=1)

        ctk.CTkButton(
            actions_frame,
            text="  📂  Manage Categories",
            font=FONT_BODY, height=42,
            fg_color="transparent",
            hover_color=BG_HOVER,
            text_color=TEXT_SECONDARY,
            anchor="w", corner_radius=8,
            command=self._open_manage_categories
        ).pack(fill="x", pady=1)

        # Bottom spacer with balance
        self._sidebar.pack_propagate(True)
        spacer = ctk.CTkFrame(self._sidebar, fg_color="transparent")
        spacer.pack(fill="both", expand=True)

        # All-time balance at bottom
        balance_card = ctk.CTkFrame(
            self._sidebar, fg_color=BG_SECONDARY,
            corner_radius=CORNER_RADIUS
        )
        balance_card.pack(fill="x", padx=15, pady=(10, 20))

        ctk.CTkLabel(
            balance_card, text="All-time Balance",
            font=FONT_SMALL, text_color=TEXT_SECONDARY
        ).pack(anchor="w", padx=15, pady=(12, 0))

        self._balance_label = ctk.CTkLabel(
            balance_card, text="€0.00",
            font=FONT_AMOUNT, text_color=ACCENT_GREEN
        )
        self._balance_label.pack(anchor="w", padx=15, pady=(2, 12))

    # ══════════════════════════════════════════
    #  MAIN AREA
    # ══════════════════════════════════════════
    def _build_main_area(self):
        self._main_container = ctk.CTkFrame(self, fg_color=BG_DARK, corner_radius=0)
        self._main_container.pack(side="right", fill="both", expand=True)

        # Dashboard view
        self._dashboard_frame = ctk.CTkFrame(self._main_container, fg_color="transparent")
        # Transactions view
        self._transactions_frame = ctk.CTkFrame(self._main_container, fg_color="transparent")
        # Calendar view
        self._calendar_frame = ctk.CTkFrame(self._main_container, fg_color="transparent")
        # Year overview view
        self._year_frame = ctk.CTkFrame(self._main_container, fg_color="transparent")

        self._build_dashboard()
        self._build_transactions()
        self._build_calendar()
        self._build_year()

        # Show dashboard by default
        self._dashboard_frame.pack(fill="both", expand=True)

    # ── Dashboard ─────────────────────────────
    def _build_dashboard(self):
        # Scrollable content
        scroll = ctk.CTkScrollableFrame(
            self._dashboard_frame, fg_color="transparent",
            scrollbar_button_color=BG_HOVER,
            scrollbar_button_hover_color=ACCENT_BLUE_DIM
        )
        scroll.pack(fill="both", expand=True, padx=0, pady=0)

        # Header
        header = ctk.CTkFrame(scroll, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(25, 5))

        ctk.CTkLabel(
            header, text="Dashboard",
            font=FONT_HEADING_XL, text_color=TEXT_PRIMARY
        ).pack(side="left")

        # Month selector dropdown
        dash_nav = ctk.CTkFrame(header, fg_color="transparent")
        dash_nav.pack(side="right")

        self._dash_month_select = ctk.CTkComboBox(
            dash_nav, width=160, height=36,
            fg_color=BG_SECONDARY, border_color=BG_HOVER,
            button_color=BG_HOVER, button_hover_color=ACCENT_BLUE_DIM,
            text_color=TEXT_PRIMARY, dropdown_fg_color=BG_SECONDARY,
            dropdown_hover_color=BG_HOVER, dropdown_text_color=TEXT_PRIMARY,
            corner_radius=8, font=FONT_SUBHEADING,
            state="readonly",
            command=self._on_dash_month_selected,
        )
        self._dash_month_select.pack(side="left", padx=2)

        ctk.CTkButton(
            dash_nav, text="Today", width=70, height=36,
            fg_color=ACCENT_BLUE_DIM, hover_color=ACCENT_BLUE,
            text_color=ACCENT_BLUE, corner_radius=8,
            font=FONT_SMALL,
            command=self._dash_go_today
        ).pack(side="left", padx=(10, 0))

        # Stats row
        stats_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        stats_frame.pack(fill="x", padx=25, pady=(20, 0))
        stats_frame.columnconfigure((0, 1, 2), weight=1)

        self._stat_income = StatCard(
            stats_frame, title="Monthly Income", value="€0.00",
            icon="📈", accent_color=ACCENT_GREEN
        )
        self._stat_income.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self._stat_expense = StatCard(
            stats_frame, title="Monthly Expenses", value="€0.00",
            icon="📉", accent_color=ACCENT_RED
        )
        self._stat_expense.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        self._stat_balance = StatCard(
            stats_frame, title="Monthly Balance", value="€0.00",
            icon="💰", accent_color=ACCENT_BLUE
        )
        self._stat_balance.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)

        # Charts section
        charts_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        charts_frame.pack(fill="x", padx=25, pady=(30, 20))
        charts_frame.columnconfigure((0, 1), weight=1)
        
        self._expense_chart = PieChart(charts_frame, title="Expense Breakdown")
        self._expense_chart.grid(row=0, column=0, sticky="nsew", padx=(5, 10))
        
        self._income_chart = PieChart(charts_frame, title="Income Breakdown")
        self._income_chart.grid(row=0, column=1, sticky="nsew", padx=(10, 5))

    # ── Transactions ──────────────────────────
    def _build_transactions(self):
        scroll = ctk.CTkScrollableFrame(
            self._transactions_frame, fg_color="transparent",
            scrollbar_button_color=BG_HOVER,
            scrollbar_button_hover_color=ACCENT_BLUE_DIM
        )
        scroll.pack(fill="both", expand=True, padx=0, pady=0)

        # Header
        header = ctk.CTkFrame(scroll, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(25, 5))

        self._trans_header = ctk.CTkLabel(
            header, text="Transactions",
            font=FONT_HEADING_XL, text_color=TEXT_PRIMARY
        )
        self._trans_header.pack(side="left")

        # Month selector dropdown
        trans_nav = ctk.CTkFrame(header, fg_color="transparent")
        trans_nav.pack(side="right")

        self._trans_month_select = ctk.CTkComboBox(
            trans_nav, width=160, height=36,
            fg_color=BG_SECONDARY, border_color=BG_HOVER,
            button_color=BG_HOVER, button_hover_color=ACCENT_BLUE_DIM,
            text_color=TEXT_PRIMARY, dropdown_fg_color=BG_SECONDARY,
            dropdown_hover_color=BG_HOVER, dropdown_text_color=TEXT_PRIMARY,
            corner_radius=8, font=FONT_SUBHEADING,
            state="readonly",
            command=self._on_dash_month_selected,
        )
        self._trans_month_select.pack(side="left", padx=2)

        ctk.CTkButton(
            trans_nav, text="Today", width=70, height=36,
            fg_color=ACCENT_BLUE_DIM, hover_color=ACCENT_BLUE,
            text_color=ACCENT_BLUE, corner_radius=8,
            font=FONT_SMALL,
            command=self._dash_go_today
        ).pack(side="left", padx=(10, 0))

        # Transaction list container
        self._trans_list = ctk.CTkFrame(scroll, fg_color="transparent")
        self._trans_list.pack(fill="x", padx=25, pady=(20, 20))

    # ── Calendar ──────────────────────────────
    def _build_calendar(self):
        # Top bar with month navigation
        nav = ctk.CTkFrame(self._calendar_frame, fg_color="transparent")
        nav.pack(fill="x", padx=30, pady=(25, 15))

        ctk.CTkLabel(
            nav, text="Calendar",
            font=FONT_HEADING_XL, text_color=TEXT_PRIMARY
        ).pack(side="left")

        nav_buttons = ctk.CTkFrame(nav, fg_color="transparent")
        nav_buttons.pack(side="right")

        self._cal_month_select = ctk.CTkComboBox(
            nav_buttons, width=160, height=36,
            fg_color=BG_SECONDARY, border_color=BG_HOVER,
            button_color=BG_HOVER, button_hover_color=ACCENT_BLUE_DIM,
            text_color=TEXT_PRIMARY, dropdown_fg_color=BG_SECONDARY,
            dropdown_hover_color=BG_HOVER, dropdown_text_color=TEXT_PRIMARY,
            corner_radius=8, font=FONT_SUBHEADING,
            state="readonly",
            command=self._on_cal_month_selected,
        )
        self._cal_month_select.pack(side="left", padx=2)

        ctk.CTkButton(
            nav_buttons, text="Today", width=70, height=36,
            fg_color=ACCENT_BLUE_DIM, hover_color=ACCENT_BLUE,
            text_color=ACCENT_BLUE, corner_radius=8,
            font=FONT_SMALL,
            command=self._go_today
        ).pack(side="left", padx=(10, 0))

        # Calendar grid + day detail split
        content = ctk.CTkFrame(self._calendar_frame, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=25, pady=(0, 20))
        content.columnconfigure(0, weight=3)
        content.columnconfigure(1, weight=2)
        content.rowconfigure(0, weight=1)

        # Calendar grid
        cal_card = GlassCard(content)
        cal_card.grid(row=0, column=0, sticky="nsew", padx=(5, 10), pady=5)

        self._cal_grid_frame = ctk.CTkFrame(cal_card, fg_color="transparent")
        self._cal_grid_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Day detail panel
        detail_card = GlassCard(content)
        detail_card.grid(row=0, column=1, sticky="nsew", padx=(10, 5), pady=5)

        self._day_detail_frame = ctk.CTkFrame(detail_card, fg_color="transparent")
        self._day_detail_frame.pack(fill="both", expand=True, padx=15, pady=15)

    # ── Year Overview ────────────────────────
    def _build_year(self):
        nav = ctk.CTkFrame(self._year_frame, fg_color="transparent")
        nav.pack(fill="x", padx=30, pady=(25, 15))

        ctk.CTkLabel(
            nav, text="Year Overview",
            font=FONT_HEADING_XL, text_color=TEXT_PRIMARY
        ).pack(side="left")

        nav_buttons = ctk.CTkFrame(nav, fg_color="transparent")
        nav_buttons.pack(side="right")

        ctk.CTkButton(
            nav_buttons, text="◀", width=40, height=36,
            fg_color=BG_SECONDARY, hover_color=BG_HOVER,
            text_color=TEXT_PRIMARY, corner_radius=8,
            font=FONT_BODY_BOLD,
            command=self._prev_year
        ).pack(side="left", padx=2)

        self._year_label = ctk.CTkLabel(
            nav_buttons, text="", font=FONT_SUBHEADING,
            text_color=TEXT_PRIMARY, width=120
        )
        self._year_label.pack(side="left", padx=10)

        ctk.CTkButton(
            nav_buttons, text="▶", width=40, height=36,
            fg_color=BG_SECONDARY, hover_color=BG_HOVER,
            text_color=TEXT_PRIMARY, corner_radius=8,
            font=FONT_BODY_BOLD,
            command=self._next_year
        ).pack(side="left", padx=2)

        scroll = ctk.CTkScrollableFrame(
            self._year_frame, fg_color="transparent",
            scrollbar_button_color=BG_HOVER,
            scrollbar_button_hover_color=ACCENT_BLUE_DIM
        )
        scroll.pack(fill="both", expand=True, padx=25, pady=(0, 20))

        self._year_months_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        self._year_months_frame.pack(fill="x", pady=10)

    # ══════════════════════════════════════════
    #  NAVIGATION
    # ══════════════════════════════════════════
    def _switch_view(self, view: str):
        self._current_view = view

        for key, btn in self._nav_buttons.items():
            if key == view:
                btn.configure(fg_color=BG_SECONDARY, text_color=TEXT_PRIMARY)
            else:
                btn.configure(fg_color="transparent", text_color=TEXT_SECONDARY)

        self._dashboard_frame.pack_forget()
        self._transactions_frame.pack_forget()
        self._calendar_frame.pack_forget()
        self._year_frame.pack_forget()

        if view == "dashboard":
            self._dashboard_frame.pack(fill="both", expand=True)
        elif view == "transactions":
            self._transactions_frame.pack(fill="both", expand=True)
        elif view == "calendar":
            self._calendar_frame.pack(fill="both", expand=True)
        elif view == "year":
            self._year_frame.pack(fill="both", expand=True)

        self._refresh_all()

    # ══════════════════════════════════════════
    #  REFRESH / DATA
    # ══════════════════════════════════════════
    def _refresh_all(self):
        self._refresh_balance()
        self._refresh_dashboard()
        self._refresh_transactions()
        self._refresh_calendar()
        self._refresh_day_detail()
        self._refresh_year()

    def _refresh_balance(self):
        totals = data_manager.get_all_time_balance()
        balance = totals["balance"]
        color = ACCENT_GREEN if balance >= 0 else ACCENT_RED
        sign = "+" if balance >= 0 else ""
        self._balance_label.configure(
            text=f"{sign}€{balance:.2f}", text_color=color
        )

    def _refresh_dashboard(self):
        year = self._dash_year
        month = self._dash_month
        month_name = date(year, month, 1).strftime("%B %Y")

        # Populate dropdown with months that have data
        months_data = data_manager.get_months_with_data()
        month_options = [f"{date(y, m, 1):%B %Y}" for y, m in months_data]
        if month_name not in month_options:
            month_options.append(month_name)
            month_options.sort(key=lambda s: datetime.strptime(s, "%B %Y"), reverse=True)
        self._dash_month_select.configure(values=month_options)
        self._dash_month_select.set(month_name)

        summary = data_manager.get_monthly_summary(year, month)

        self._stat_income.set_value(f"€{summary['total_income']:.2f}")
        self._stat_expense.set_value(f"€{summary['total_expense']:.2f}")

        balance = summary["balance"]
        sign = "+" if balance >= 0 else ""
        self._stat_balance.set_value(f"{sign}€{balance:.2f}")

        # Pie charts
        self._expense_chart.set_data(summary.get("category_expenses", {}))
        self._income_chart.set_data(summary.get("category_income", {}))

    def _refresh_transactions(self):
        year = self._dash_year
        month = self._dash_month
        month_name = date(year, month, 1).strftime("%B %Y")
        
        self._trans_header.configure(text=f"Transactions — {month_name}")

        # Sync dropdown
        months_data = data_manager.get_months_with_data()
        month_options = [f"{date(y, m, 1):%B %Y}" for y, m in months_data]
        if month_name not in month_options:
            month_options.append(month_name)
            month_options.sort(key=lambda s: datetime.strptime(s, "%B %Y"), reverse=True)
        self._trans_month_select.configure(values=month_options)
        self._trans_month_select.set(month_name)

        # Month transactions
        for w in self._trans_list.winfo_children():
            w.destroy()

        month_trans = data_manager.get_transactions_by_month(year, month)
        month_trans.sort(key=lambda t: t.get("date", ""), reverse=True)

        if not month_trans:
            ctk.CTkLabel(
                self._trans_list,
                text="No transactions this month. Add your first one! 🎉",
                font=FONT_BODY, text_color=TEXT_MUTED
            ).pack(pady=30)
        else:
            for t in month_trans:
                row = TransactionRow(
                    self._trans_list, t,
                    on_delete=self._delete_transaction
                )
                row.pack(fill="x", pady=2)

    def _refresh_calendar(self):
        for w in self._cal_grid_frame.winfo_children():
            w.destroy()

        year = self._current_year
        month = self._current_month
        month_name = date(year, month, 1).strftime("%B %Y")

        # Populate dropdown
        months_data = data_manager.get_months_with_data()
        month_options = [f"{date(y, m, 1):%B %Y}" for y, m in months_data]
        if month_name not in month_options:
            month_options.append(month_name)
            month_options.sort(key=lambda s: datetime.strptime(s, "%B %Y"), reverse=True)
        self._cal_month_select.configure(values=month_options)
        self._cal_month_select.set(month_name)

        # Day name headers
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for col, name in enumerate(day_names):
            lbl = ctk.CTkLabel(
                self._cal_grid_frame, text=name,
                font=FONT_TINY, text_color=TEXT_MUTED
            )
            lbl.grid(row=0, column=col, sticky="nsew", padx=1, pady=(0, 5))

        self._cal_grid_frame.columnconfigure(tuple(range(7)), weight=1)

        # Get month data
        summary = data_manager.get_monthly_summary(year, month)
        daily_data = summary.get("daily", {})

        # Calendar days
        month_cal = cal_module.monthcalendar(year, month)
        today = date.today()

        for row_idx, week in enumerate(month_cal):
            self._cal_grid_frame.rowconfigure(row_idx + 1, weight=1)
            for col_idx, day_num in enumerate(week):
                if day_num == 0:
                    # Empty cell
                    empty = ctk.CTkFrame(
                        self._cal_grid_frame, fg_color="transparent"
                    )
                    empty.grid(row=row_idx + 1, column=col_idx, sticky="nsew", padx=1, pady=1)
                    continue

                day_str = f"{year:04d}-{month:02d}-{day_num:02d}"
                is_today = (day_str == today.isoformat())
                is_selected = (day_str == self._selected_date)
                day_info = daily_data.get(day_str, None)

                # Choose cell appearance
                if is_selected:
                    cell_fg = ACCENT_BLUE_DIM
                    border_c = ACCENT_BLUE
                    border_w = 2
                elif is_today:
                    cell_fg = BG_HOVER
                    border_c = ACCENT_PURPLE
                    border_w = 1
                else:
                    cell_fg = BG_SECONDARY
                    border_c = BORDER_COLOR
                    border_w = 0

                cell = ctk.CTkFrame(
                    self._cal_grid_frame, fg_color=cell_fg,
                    corner_radius=8, border_width=border_w,
                    border_color=border_c
                )
                cell.grid(row=row_idx + 1, column=col_idx, sticky="nsew", padx=1, pady=1)

                # Make clickable
                cell.bind("<Button-1>", lambda e, d=day_str: self._select_date(d))

                # Day number
                day_label = ctk.CTkLabel(
                    cell, text=str(day_num),
                    font=FONT_CALENDAR_DAY,
                    text_color=TEXT_PRIMARY if not is_today else ACCENT_PURPLE
                )
                day_label.pack(anchor="nw", padx=6, pady=(4, 0))
                day_label.bind("<Button-1>", lambda e, d=day_str: self._select_date(d))

                # Income/expense indicators
                if day_info:
                    if day_info.get("income", 0) > 0:
                        inc_label = ctk.CTkLabel(
                            cell, text=f"+{day_info['income']:.0f}",
                            font=FONT_CALENDAR_AMOUNT,
                            text_color=ACCENT_GREEN
                        )
                        inc_label.pack(anchor="w", padx=6)
                        inc_label.bind("<Button-1>", lambda e, d=day_str: self._select_date(d))

                    if day_info.get("expense", 0) > 0:
                        exp_label = ctk.CTkLabel(
                            cell, text=f"-{day_info['expense']:.0f}",
                            font=FONT_CALENDAR_AMOUNT,
                            text_color=ACCENT_RED
                        )
                        exp_label.pack(anchor="w", padx=6)
                        exp_label.bind("<Button-1>", lambda e, d=day_str: self._select_date(d))

    def _refresh_day_detail(self):
        for w in self._day_detail_frame.winfo_children():
            w.destroy()

        try:
            selected = date.fromisoformat(self._selected_date)
            day_title = selected.strftime("%A, %B %d")
        except ValueError:
            day_title = self._selected_date

        ctk.CTkLabel(
            self._day_detail_frame, text=day_title,
            font=FONT_SUBHEADING, text_color=TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 5))

        ctk.CTkLabel(
            self._day_detail_frame, text=self._selected_date,
            font=FONT_SMALL, text_color=TEXT_MUTED
        ).pack(anchor="w", pady=(0, 15))

        transactions = data_manager.get_transactions_by_date(self._selected_date)

        if not transactions:
            ctk.CTkLabel(
                self._day_detail_frame,
                text="No transactions\nfor this day",
                font=FONT_BODY, text_color=TEXT_MUTED,
                justify="center"
            ).pack(expand=True)
            return

        # Day totals
        day_income = sum(t["amount"] for t in transactions if t["type"] == "income")
        day_expense = sum(t["amount"] for t in transactions if t["type"] == "expense")

        totals = ctk.CTkFrame(self._day_detail_frame, fg_color=BG_SECONDARY, corner_radius=8)
        totals.pack(fill="x", pady=(0, 10))

        t_inner = ctk.CTkFrame(totals, fg_color="transparent")
        t_inner.pack(fill="x", padx=12, pady=8)

        if day_income > 0:
            ctk.CTkLabel(
                t_inner, text=f"📈 +€{day_income:.2f}",
                font=FONT_BODY_BOLD, text_color=ACCENT_GREEN
            ).pack(anchor="w")

        if day_expense > 0:
            ctk.CTkLabel(
                t_inner, text=f"📉 -€{day_expense:.2f}",
                font=FONT_BODY_BOLD, text_color=ACCENT_RED
            ).pack(anchor="w")

        # Transaction list
        scroll = ctk.CTkScrollableFrame(
            self._day_detail_frame, fg_color="transparent",
            scrollbar_button_color=BG_HOVER,
            scrollbar_button_hover_color=ACCENT_BLUE_DIM
        )
        scroll.pack(fill="both", expand=True)

        for t in transactions:
            row = TransactionRow(
                scroll, t, on_delete=self._delete_transaction
            )
            row.pack(fill="x", pady=2)

    # ══════════════════════════════════════════
    #  ACTIONS
    # ══════════════════════════════════════════
    def _select_date(self, day_str: str):
        self._selected_date = day_str
        self._refresh_calendar()
        self._refresh_day_detail()

    def _go_today(self):
        today = date.today()
        self._current_year = today.year
        self._current_month = today.month
        self._selected_date = today.isoformat()
        self._refresh_calendar()
        self._refresh_day_detail()

    def _on_dash_month_selected(self, value):
        dt = datetime.strptime(value, "%B %Y")
        self._dash_year = dt.year
        self._dash_month = dt.month
        self._refresh_dashboard()
        self._refresh_transactions()

    def _on_cal_month_selected(self, value):
        dt = datetime.strptime(value, "%B %Y")
        self._current_year = dt.year
        self._current_month = dt.month
        self._refresh_calendar()
        self._refresh_day_detail()

    def _dash_go_today(self):
        today = date.today()
        self._dash_year = today.year
        self._dash_month = today.month
        self._refresh_dashboard()
        self._refresh_transactions()

    def _prev_year(self):
        self._view_year -= 1
        self._refresh_year()

    def _next_year(self):
        self._view_year += 1
        self._refresh_year()

    def _refresh_year(self):
        self._year_label.configure(text=str(self._view_year))

        for w in self._year_months_frame.winfo_children():
            w.destroy()

        for month in range(1, 13):
            summary = data_manager.get_monthly_summary(self._view_year, month)
            income = summary.get("total_income", 0)
            expense = summary.get("total_expense", 0)
            balance = summary.get("balance", 0)

            month_name = date(self._view_year, month, 1).strftime("%B")

            row = ctk.CTkFrame(self._year_months_frame, fg_color=BG_SECONDARY, corner_radius=8)
            row.pack(fill="x", pady=3)

            inner = ctk.CTkFrame(row, fg_color="transparent")
            inner.pack(fill="x", padx=15, pady=12)

            ctk.CTkLabel(
                inner, text=month_name, font=FONT_BODY,
                text_color=TEXT_PRIMARY, width=100
            ).pack(side="left")

            income_text = f"+€{income:.2f}" if income > 0 else "€0.00"
            ctk.CTkLabel(
                inner, text=income_text, font=FONT_SMALL,
                text_color=ACCENT_GREEN
            ).pack(side="left", padx=15)

            expense_text = f"-€{expense:.2f}"
            ctk.CTkLabel(
                inner, text=expense_text, font=FONT_SMALL,
                text_color=ACCENT_RED
            ).pack(side="left", padx=15)

            if balance >= 0:
                balance_text = f"+€{balance:.2f}"
                balance_color = ACCENT_GREEN
            else:
                balance_text = f"€{balance:.2f}"
                balance_color = ACCENT_RED

            ctk.CTkLabel(
                inner, text=balance_text, font=FONT_BODY_BOLD,
                text_color=balance_color
            ).pack(side="right")

    def _open_add_transaction(self):
        AddTransactionDialog(self, on_save=self._refresh_all)

    def _open_manage_categories(self):
        ManageCategoriesDialog(self, on_save=self._refresh_all)

    def _delete_transaction(self, trans_id: str):
        data_manager.delete_transaction(trans_id)
        self._refresh_all()
