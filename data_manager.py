"""
MoneyTracker 3.0 - Data Manager
Handles all data persistence using SQLite database.
"""

import sqlite3
import os
import sys
from datetime import date, datetime
from typing import Optional


if getattr(sys, 'frozen', False):
    _BASE_DIR = os.path.dirname(sys.executable)
else:
    _BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(_BASE_DIR, "data")
DB_FILE = os.path.join(DATA_DIR, "moneytracker.db")

DEFAULT_EXPENSE_CATEGORIES = [
    "🍔 Food & Dining",
    "🏠 Housing & Rent",
    "🚗 Transportation",
    "🛒 Groceries",
    "💊 Health & Medical",
    "🎭 Entertainment",
    "👕 Clothing",
    "📚 Education",
    "💡 Utilities",
    "📱 Subscriptions",
    "🎁 Gifts",
    "✈️ Travel",
    "🔧 Maintenance",
    "💼 Other Expenses",
]

DEFAULT_INCOME_CATEGORIES = [
    "💰 Salary",
    "💵 Freelance",
    "📈 Investments",
    "🏦 Interest",
    "🎁 Gifts Received",
    "💼 Business Income",
    "📦 Refunds",
    "💸 Other Income",
]


def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def _get_connection():
    _ensure_data_dir()
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def _init_db():
    """Initialize the database schema."""
    conn = _get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            type TEXT NOT NULL CHECK(type IN ('income', 'expense'))
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT DEFAULT '',
            date TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(type)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category)
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL CHECK(amount >= 0),
            UNIQUE(year, category)
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM categories")
    if cursor.fetchone()[0] == 0:
        for cat in DEFAULT_EXPENSE_CATEGORIES:
            cursor.execute("INSERT INTO categories (name, type) VALUES (?, 'expense')", (cat,))
        for cat in DEFAULT_INCOME_CATEGORIES:
            cursor.execute("INSERT INTO categories (name, type) VALUES (?, 'income')", (cat,))
    
    conn.commit()
    conn.close()


def _migrate_from_json():
    """Import data from JSON files if database is empty."""
    json_transactions = os.path.join(DATA_DIR, "transactions.json")
    json_categories = os.path.join(DATA_DIR, "categories.json")
    
    conn = _get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM transactions")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return
    
    import json
    
    if os.path.exists(json_categories):
        with open(json_categories, "r", encoding="utf-8") as f:
            cats = json.load(f)
            for cat in cats.get("expense", []):
                try:
                    cursor.execute("INSERT OR IGNORE INTO categories (name, type) VALUES (?, 'expense')", (cat,))
                except sqlite3.IntegrityError:
                    pass
            for cat in cats.get("income", []):
                try:
                    cursor.execute("INSERT OR IGNORE INTO categories (name, type) VALUES (?, 'income')", (cat,))
                except sqlite3.IntegrityError:
                    pass
            conn.commit()
    
    if os.path.exists(json_transactions):
        with open(json_transactions, "r", encoding="utf-8") as f:
            transactions = json.load(f)
            for t in transactions:
                cursor.execute("""
                    INSERT INTO transactions (id, type, amount, category, description, date, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (t["id"], t["type"], t["amount"], t["category"], 
                      t.get("description", ""), t["date"], t["created_at"]))
        conn.commit()
    
    conn.close()


def _ensure_initialized():
    """Ensure database is initialized."""
    _init_db()
    _migrate_from_json()


def load_categories() -> dict:
    """Load categories from database. Returns dict with 'expense' and 'income' lists."""
    _ensure_initialized()
    conn = _get_connection()
    cursor = conn.cursor()
    
    result = {"expense": [], "income": []}
    
    cursor.execute("SELECT name FROM categories WHERE type = 'expense' ORDER BY name")
    result["expense"] = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT name FROM categories WHERE type = 'income' ORDER BY name")
    result["income"] = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    return result


def save_categories(categories: dict):
    """Save categories to database."""
    _ensure_initialized()
    conn = _get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM categories")
    
    for cat in categories.get("expense", []):
        cursor.execute("INSERT INTO categories (name, type) VALUES (?, 'expense')", (cat,))
    for cat in categories.get("income", []):
        cursor.execute("INSERT INTO categories (name, type) VALUES (?, 'income')", (cat,))

    # Remove budgets of deleted categories
    cursor.execute(
        "DELETE FROM budgets WHERE category NOT IN (SELECT name FROM categories)"
    )

    conn.commit()
    conn.close()


def load_budgets(year: int) -> dict:
    """Load annual budgets for a year. Returns {category: amount}."""
    _ensure_initialized()
    conn = _get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT category, amount FROM budgets WHERE year = ?", (year,))
    result = {row[0]: row[1] for row in cursor.fetchall()}

    conn.close()
    return result


def save_year_budgets(year: int, budgets: dict):
    """Save annual budgets for a year (replaces existing)."""
    _ensure_initialized()
    conn = _get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM budgets WHERE year = ?", (year,))

    for category, amount in budgets.items():
        if amount is None or amount <= 0:
            continue
        cursor.execute(
            "INSERT INTO budgets (year, category, amount) VALUES (?, ?, ?)",
            (year, category, round(amount, 2)),
        )

    conn.commit()
    conn.close()


def get_annual_summary(year: int) -> dict:
    """Get summary statistics for a full year."""
    _ensure_initialized()
    conn = _get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT category, SUM(amount) FROM transactions
        WHERE type = 'expense' AND substr(date, 1, 4) = ?
        GROUP BY category
    """, (f"{year:04d}",))
    category_expenses = {row[0]: row[1] for row in cursor.fetchall()}

    conn.close()
    return {
        "total_expense": round(sum(category_expenses.values()), 2),
        "category_expenses": {k: round(v, 2) for k, v in category_expenses.items()},
    }


def load_transactions() -> list[dict]:
    """Load all transactions from database."""
    _ensure_initialized()
    conn = _get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, type, amount, category, description, date, created_at FROM transactions ORDER BY date DESC, created_at DESC")
    transactions = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return transactions


def save_transactions(transactions: list[dict]):
    """Save all transactions to database (replaces existing)."""
    _ensure_initialized()
    conn = _get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM transactions")
    
    for t in transactions:
        cursor.execute("""
            INSERT INTO transactions (id, type, amount, category, description, date, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (t["id"], t["type"], t["amount"], t["category"], 
              t.get("description", ""), t["date"], t.get("created_at", datetime.now().isoformat())))
    
    conn.commit()
    conn.close()


def add_transaction(
    trans_type: str,
    amount: float,
    category: str,
    description: str = "",
    trans_date: Optional[str] = None,
) -> dict:
    """Add a new transaction."""
    import uuid
    
    if trans_date is None:
        trans_date = date.today().isoformat()
    
    transaction = {
        "id": str(uuid.uuid4()),
        "type": trans_type,
        "amount": round(amount, 2),
        "category": category,
        "description": description,
        "date": trans_date,
        "created_at": datetime.now().isoformat(),
    }
    
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO transactions (id, type, amount, category, description, date, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (transaction["id"], transaction["type"], transaction["amount"], 
          transaction["category"], transaction["description"], 
          transaction["date"], transaction["created_at"]))
    conn.commit()
    conn.close()
    
    return transaction


def delete_transaction(trans_id: str) -> bool:
    """Delete a transaction by ID. Returns True if found and deleted."""
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions WHERE id = ?", (trans_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


def update_transaction(trans_id: str, **kwargs) -> Optional[dict]:
    """Update fields of a transaction. Returns updated transaction or None."""
    conn = _get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, type, amount, category, description, date, created_at FROM transactions WHERE id = ?", (trans_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
    
    current = dict(row)
    for key, value in kwargs.items():
        if key in current and key not in ("id", "created_at"):
            current[key] = value
    
    cursor.execute("""
        UPDATE transactions 
        SET type = ?, amount = ?, category = ?, description = ?, date = ?
        WHERE id = ?
    """, (current["type"], current["amount"], current["category"], 
          current["description"], current["date"], trans_id))
    conn.commit()
    conn.close()
    
    return current


def get_transactions_by_date(target_date: str) -> list[dict]:
    """Get all transactions for a specific date (YYYY-MM-DD)."""
    _ensure_initialized()
    conn = _get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, type, amount, category, description, date, created_at 
        FROM transactions WHERE date = ?
        ORDER BY created_at DESC
    """, (target_date,))
    transactions = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return transactions


def get_transactions_by_month(year: int, month: int) -> list[dict]:
    """Get all transactions for a specific month."""
    _ensure_initialized()
    conn = _get_connection()
    cursor = conn.cursor()
    
    prefix = f"{year:04d}-{month:02d}"
    cursor.execute("""
        SELECT id, type, amount, category, description, date, created_at 
        FROM transactions WHERE date LIKE ?
        ORDER BY date DESC, created_at DESC
    """, (prefix + "%",))
    transactions = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return transactions


def get_monthly_summary(year: int, month: int) -> dict:
    """Get summary statistics for a month."""
    month_transactions = get_transactions_by_month(year, month)
    total_income = sum(t["amount"] for t in month_transactions if t["type"] == "income")
    total_expense = sum(t["amount"] for t in month_transactions if t["type"] == "expense")

    daily = {}
    for t in month_transactions:
        day = t["date"]
        if day not in daily:
            daily[day] = {"income": 0.0, "expense": 0.0}
        daily[day][t["type"]] += t["amount"]

    category_expenses = {}
    category_income = {}
    for t in month_transactions:
        if t["type"] == "expense":
            category_expenses[t["category"]] = (
                category_expenses.get(t["category"], 0) + t["amount"]
            )
        else:
            category_income[t["category"]] = (
                category_income.get(t["category"], 0) + t["amount"]
            )

    return {
        "total_income": round(total_income, 2),
        "total_expense": round(total_expense, 2),
        "balance": round(total_income - total_expense, 2),
        "daily": daily,
        "category_expenses": category_expenses,
        "category_income": category_income,
        "transaction_count": len(month_transactions),
    }


def get_all_time_balance() -> dict:
    """Get the overall balance across all time."""
    _ensure_initialized()
    conn = _get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type = 'income'")
    total_income = cursor.fetchone()[0] or 0.0
    
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type = 'expense'")
    total_expense = cursor.fetchone()[0] or 0.0
    
    conn.close()
    return {
        "total_income": round(total_income, 2),
        "total_expense": round(total_expense, 2),
        "balance": round(total_income - total_expense, 2),
    }


def get_months_with_data() -> list[tuple[int, int]]:
    """Return sorted list of (year, month) tuples that have transactions."""
    _ensure_initialized()
    conn = _get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT DISTINCT substr(date, 1, 7) as ym
        FROM transactions
        ORDER BY ym DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for row in rows:
        ym = row[0]
        year, month = int(ym[:4]), int(ym[5:7])
        result.append((year, month))
    return result