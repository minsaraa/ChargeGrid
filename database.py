"""
database.py - ChargeGrid backend
=================================
This file contains EVERYTHING that touches the SQLite database, plus the
OOP classes (Charger, ACCharger, DCCharger, ChargingSession).

The Streamlit file (chargegrid_app.py) never writes SQL. It only calls the
functions in this file.

Most "action" functions return (success, message) so the UI can show a
clear message. Functions that read data return dictionaries or lists of
dictionaries (no Pandas needed).

All money and top-ups are SIMULATED (student demo project).
"""

import sqlite3
import hashlib
import secrets
import hmac
import os
from datetime import datetime

# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

# The database file is created next to this Python file.
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chargegrid.db")

SITE_NAME = "ChargeGrid Central Charging Hub"
SITE_NOTE = "Demonstration site - simulated data, not a real deployment"

CHARGER_TYPES = ["AC Standard", "DC Fast", "DC Ultra-fast"]
CHARGER_STATUSES = ["Available", "Occupied", "Out of Service"]

# Demo operator account (documented in the README / login page)
DEMO_OPERATOR_NAME = "ChargeGrid Operator"
DEMO_OPERATOR_EMAIL = "operator@chargegrid.demo"
DEMO_OPERATOR_PASSWORD = "Operator@123"

# In the demo, 1 real second counts as 1 simulated minute of charging.
SIMULATION_SPEEDUP = 60

MIN_TOPUP = 10.0
MAX_TOPUP = 10000.0

# Sample chargers: (charger_id, type, power_kw, rate_per_kwh, status)
SAMPLE_CHARGERS = [
    ("CG-C01", "AC Standard", 22, 10, "Available"),
    ("CG-C02", "AC Standard", 22, 10, "Available"),
    ("CG-C03", "AC Standard", 22, 10, "Available"),
    ("CG-C04", "DC Fast", 60, 14, "Available"),
    ("CG-C05", "DC Fast", 120, 14, "Available"),
    ("CG-C06", "DC Fast", 150, 15, "Available"),
    ("CG-C07", "DC Ultra-fast", 250, 18, "Available"),
    ("CG-C08", "DC Ultra-fast", 250, 18, "Out of Service"),
]


# ---------------------------------------------------------------------------
# OOP CLASSES
# ---------------------------------------------------------------------------

class Charger:
    """
    Base class for every charging port.

    ENCAPSULATION: the data is stored in "private" attributes that start
    with an underscore (_rate_per_kwh, _status ...). Other code reads them
    through properties and changes the rate only through set_rate(), which
    checks that the new value is valid.
    """

    def __init__(self, charger_id, charger_type, power_kw, rate_per_kwh, status):
        self._charger_id = charger_id
        self._charger_type = charger_type
        self._power_kw = float(power_kw)
        self._rate_per_kwh = float(rate_per_kwh)
        self._status = status

    # Read-only properties (getters)
    @property
    def charger_id(self):
        return self._charger_id

    @property
    def charger_type(self):
        return self._charger_type

    @property
    def power_kw(self):
        return self._power_kw

    @property
    def rate_per_kwh(self):
        return self._rate_per_kwh

    @property
    def status(self):
        return self._status

    def set_rate(self, new_rate):
        """Encapsulation: the rate can only change through this checked method."""
        if new_rate <= 0:
            raise ValueError("Rate must be greater than zero.")
        self._rate_per_kwh = float(new_rate)

    def is_available(self):
        return self._status == "Available"

    # These three methods are OVERRIDDEN in the subclasses (polymorphism)
    def get_effective_power(self):
        """Average power the car really receives (kW)."""
        return self._power_kw

    def get_speed_label(self):
        return "Standard"

    def describe(self):
        return f"{self._charger_id} - {self._charger_type} ({self._power_kw:g} kW)"

    # Shared by all chargers (inherited, not overridden)
    def calculate_cost(self, energy_kwh):
        """Total cost = Energy consumed in kWh x Price per kWh"""
        return round(energy_kwh * self._rate_per_kwh, 2)

    def estimate_minutes(self, energy_kwh):
        """Rough charging time estimate using the effective power."""
        hours = energy_kwh / self.get_effective_power()
        return max(1, round(hours * 60))


class ACCharger(Charger):
    """INHERITANCE: an AC charger IS-A Charger. It overrides three methods."""

    def get_effective_power(self):
        # Demo assumption: AC charging delivers about 95% of rated power.
        return self._power_kw * 0.95

    def get_speed_label(self):
        return "Standard speed"

    def describe(self):
        # super() reuses the parent's text and adds to it
        return "AC | " + super().describe()


class DCCharger(Charger):
    """INHERITANCE: a DC charger IS-A Charger. It overrides three methods."""

    def get_effective_power(self):
        # Demo assumption: DC charging slows down near full, so ~85% average.
        return self._power_kw * 0.85

    def get_speed_label(self):
        if "Ultra" in self._charger_type:
            return "Ultra-fast"
        return "Fast"

    def describe(self):
        return "DC | " + super().describe()


def make_charger(charger_row):
    """
    Build the correct class from a database row (a dictionary).
    AC types become ACCharger, everything else becomes DCCharger.
    """
    if charger_row["charger_type"].startswith("AC"):
        charger_class = ACCharger
    else:
        charger_class = DCCharger
    return charger_class(
        charger_row["charger_id"],
        charger_row["charger_type"],
        charger_row["power_kw"],
        charger_row["rate_per_kwh"],
        charger_row["status"],
    )


class ChargingSession:
    """
    Represents one charging session. It knows how to:
    - work out how long it has been running
    - simulate the energy delivered (demo only)
    - calculate the final cost without exceeding the driver's limit
    """

    def __init__(self, session_id, user_id, charger, start_time,
                 rate_per_kwh, spending_limit, max_energy_kwh):
        self.session_id = session_id
        self.user_id = user_id
        self.charger = charger                  # a Charger / ACCharger / DCCharger object
        self.start_time = start_time            # text like "2026-10-14 10:30:00"
        self.rate_per_kwh = rate_per_kwh        # rate locked in when the session started
        self.spending_limit = spending_limit
        self.max_energy_kwh = max_energy_kwh

    def get_elapsed_seconds(self):
        started = datetime.strptime(self.start_time, "%Y-%m-%d %H:%M:%S")
        seconds = (datetime.now() - started).total_seconds()
        return max(0, int(seconds))

    def simulate_energy(self):
        """DEMO ONLY: energy = effective power x simulated hours, capped at the limit."""
        simulated_hours = self.get_elapsed_seconds() * SIMULATION_SPEEDUP / 3600
        energy = self.charger.get_effective_power() * simulated_hours   # polymorphic call
        return round(min(energy, self.max_energy_kwh), 2)

    def calculate_final_cost(self, energy_kwh):
        """Cost = kWh x rate, but never more than the spending limit."""
        cost = round(energy_kwh * self.rate_per_kwh, 2)
        return min(cost, self.spending_limit)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_connection():
    """Open a connection. Rows can be read by column name. Foreign keys ON."""
    connection = sqlite3.connect(DB_FILE, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def rows_to_dicts(rows):
    return [dict(row) for row in rows]


def get_one_value(connection, sql, params=()):
    """Run a query that returns a single number (COUNT / SUM)."""
    row = connection.execute(sql, params).fetchone()
    return row[0] if row and row[0] is not None else 0


# ---------------------------------------------------------------------------
# Password hashing (standard library only)
# ---------------------------------------------------------------------------

def hash_password(password):
    """
    Salted PBKDF2-SHA256 hash. The result is stored as one text value:
    pbkdf2$iterations$salt$hash
    """
    iterations = 200000
    salt = secrets.token_hex(16)                      # random salt
    hash_bytes = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt), iterations
    )
    return f"pbkdf2${iterations}${salt}${hash_bytes.hex()}"


def verify_password(password, stored_hash):
    """Hash the typed password with the stored salt and compare safely."""
    try:
        method, iterations, salt, saved_hash = stored_hash.split("$")
        new_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), bytes.fromhex(salt), int(iterations)
        )
        return hmac.compare_digest(new_hash.hex(), saved_hash)
    except (ValueError, AttributeError):
        return False


# ---------------------------------------------------------------------------
# Database creation (safe to run every time the app starts)
# ---------------------------------------------------------------------------

def init_database():
    """Create tables if missing, then add the sample chargers and operator."""
    connection = get_connection()
    try:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id        INTEGER PRIMARY KEY AUTOINCREMENT,
                name           TEXT NOT NULL,
                email          TEXT NOT NULL UNIQUE,
                password_hash  TEXT NOT NULL,
                role           TEXT NOT NULL CHECK (role IN ('driver', 'operator')),
                wallet_balance REAL NOT NULL DEFAULT 0 CHECK (wallet_balance >= 0)
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS chargers (
                charger_id    TEXT PRIMARY KEY,
                charger_type  TEXT NOT NULL
                              CHECK (charger_type IN ('AC Standard', 'DC Fast', 'DC Ultra-fast')),
                power_kw      REAL NOT NULL CHECK (power_kw > 0),
                rate_per_kwh  REAL NOT NULL CHECK (rate_per_kwh > 0),
                status        TEXT NOT NULL DEFAULT 'Available'
                              CHECK (status IN ('Available', 'Occupied', 'Out of Service'))
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS charging_sessions (
                session_id     INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id        INTEGER NOT NULL,
                charger_id     TEXT NOT NULL,
                start_time     TEXT NOT NULL,
                end_time       TEXT,
                energy_kwh     REAL NOT NULL DEFAULT 0 CHECK (energy_kwh >= 0),
                rate_per_kwh   REAL NOT NULL,
                spending_limit REAL NOT NULL,
                max_energy_kwh REAL NOT NULL,
                total_cost     REAL NOT NULL DEFAULT 0 CHECK (total_cost >= 0),
                session_status TEXT NOT NULL DEFAULT 'Active'
                               CHECK (session_status IN ('Active', 'Completed', 'Cancelled')),
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (charger_id) REFERENCES chargers (charger_id)
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS wallet_transactions (
                transaction_id   INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id          INTEGER NOT NULL,
                transaction_type TEXT NOT NULL
                                 CHECK (transaction_type IN ('Top-up', 'Charging', 'Refund')),
                amount           REAL NOT NULL,
                transaction_date TEXT NOT NULL,
                description      TEXT,
                session_id       INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (session_id) REFERENCES charging_sessions (session_id)
            )
        """)

        # Safety nets: the database itself refuses two ACTIVE sessions on the
        # same charger, or two ACTIVE sessions for the same driver.
        connection.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS one_active_session_per_charger
            ON charging_sessions (charger_id) WHERE session_status = 'Active'
        """)
        connection.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS one_active_session_per_driver
            ON charging_sessions (user_id) WHERE session_status = 'Active'
        """)

        # Sample chargers (INSERT OR IGNORE skips ones that already exist)
        for charger in SAMPLE_CHARGERS:
            connection.execute(
                "INSERT OR IGNORE INTO chargers "
                "(charger_id, charger_type, power_kw, rate_per_kwh, status) "
                "VALUES (?, ?, ?, ?, ?)",
                charger,
            )

        # Default operator (only created if it does not exist yet)
        existing = connection.execute(
            "SELECT user_id FROM users WHERE email = ?", (DEMO_OPERATOR_EMAIL,)
        ).fetchone()
        if existing is None:
            connection.execute(
                "INSERT INTO users (name, email, password_hash, role, wallet_balance) "
                "VALUES (?, ?, ?, 'operator', 0)",
                (DEMO_OPERATOR_NAME, DEMO_OPERATOR_EMAIL, hash_password(DEMO_OPERATOR_PASSWORD)),
            )

        connection.commit()
    finally:
        connection.close()


# ---------------------------------------------------------------------------
# Users: register, login, lookup
# ---------------------------------------------------------------------------

def register_user(name, email, password):
    """Create a DRIVER account. Returns (success, message)."""
    name = name.strip()
    email = email.strip().lower()

    if name == "":
        return False, "Please enter your name."
    if " " in email or "@" not in email or "." not in email.split("@")[-1]:
        return False, "Please enter a valid email address."
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."

    connection = get_connection()
    try:
        connection.execute(
            "INSERT INTO users (name, email, password_hash, role, wallet_balance) "
            "VALUES (?, ?, ?, 'driver', 0)",
            (name, email, hash_password(password)),
        )
        connection.commit()
        return True, "Account created. You can log in now."
    except sqlite3.IntegrityError:
        return False, "An account with this email already exists."
    finally:
        connection.close()


def login_user(email, password):
    """Returns the user as a dictionary (without the hash), or None."""
    email = email.strip().lower()
    connection = get_connection()
    try:
        row = connection.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
    finally:
        connection.close()

    if row is None:
        return None
    if not verify_password(password, row["password_hash"]):
        return None
    return get_user(row["user_id"])


def get_user(user_id):
    connection = get_connection()
    try:
        row = connection.execute(
            "SELECT user_id, name, email, role, wallet_balance FROM users WHERE user_id = ?",
            (user_id,),
        ).fetchone()
    finally:
        connection.close()
    return dict(row) if row else None


def is_operator(user_id):
    """Server-side role check used by every operator-only function below."""
    user = get_user(user_id)
    return user is not None and user["role"] == "operator"


# ---------------------------------------------------------------------------
# Chargers
# ---------------------------------------------------------------------------

def get_all_chargers():
    connection = get_connection()
    try:
        rows = connection.execute("SELECT * FROM chargers ORDER BY charger_id").fetchall()
    finally:
        connection.close()
    return rows_to_dicts(rows)


def get_available_chargers():
    connection = get_connection()
    try:
        rows = connection.execute(
            "SELECT * FROM chargers WHERE status = 'Available' ORDER BY charger_id"
        ).fetchall()
    finally:
        connection.close()
    return rows_to_dicts(rows)


def get_charger(charger_id):
    connection = get_connection()
    try:
        row = connection.execute(
            "SELECT * FROM chargers WHERE charger_id = ?", (charger_id,)
        ).fetchone()
    finally:
        connection.close()
    return dict(row) if row else None


def next_charger_id():
    """Suggest the next free ID, e.g. CG-C09."""
    highest = 0
    for charger in get_all_chargers():
        last_part = charger["charger_id"].split("-C")[-1]
        if last_part.isdigit() and int(last_part) > highest:
            highest = int(last_part)
    return f"CG-C{highest + 1:02d}"


def charger_has_active_session(charger_id):
    connection = get_connection()
    try:
        count = get_one_value(
            connection,
            "SELECT COUNT(*) FROM charging_sessions "
            "WHERE charger_id = ? AND session_status = 'Active'",
            (charger_id,),
        )
    finally:
        connection.close()
    return count > 0


def add_charger(operator_id, charger_id, charger_type, power_kw, rate_per_kwh):
    """Operator only. Returns (success, message)."""
    if not is_operator(operator_id):
        return False, "Only operators can add chargers."

    charger_id = charger_id.strip().upper()
    if charger_id == "" or " " in charger_id:
        return False, "Charger ID cannot be empty or contain spaces."
    if charger_type not in CHARGER_TYPES:
        return False, "Please choose a valid charger type."
    if power_kw <= 0:
        return False, "Power must be greater than zero."
    if rate_per_kwh <= 0:
        return False, "Rate must be greater than zero."

    connection = get_connection()
    try:
        connection.execute(
            "INSERT INTO chargers (charger_id, charger_type, power_kw, rate_per_kwh, status) "
            "VALUES (?, ?, ?, ?, 'Available')",
            (charger_id, charger_type, float(power_kw), float(rate_per_kwh)),
        )
        connection.commit()
        return True, f"Charger {charger_id} added."
    except sqlite3.IntegrityError:
        return False, f"A charger with ID {charger_id} already exists."
    finally:
        connection.close()


def update_charger_rate(operator_id, charger_id, new_rate):
    """Operator only. Running sessions keep the rate they started with."""
    if not is_operator(operator_id):
        return False, "Only operators can change rates."
    if new_rate <= 0:
        return False, "Rate must be greater than zero."

    connection = get_connection()
    try:
        cursor = connection.execute(
            "UPDATE chargers SET rate_per_kwh = ? WHERE charger_id = ?",
            (float(new_rate), charger_id),
        )
        connection.commit()
        if cursor.rowcount == 0:
            return False, "Charger not found."
        return True, f"Rate for {charger_id} updated to {new_rate:.2f} per kWh."
    finally:
        connection.close()


def update_charger_status(operator_id, charger_id, new_status):
    """Operator only. A charger with an active session cannot be changed."""
    if not is_operator(operator_id):
        return False, "Only operators can change charger status."
    if new_status not in CHARGER_STATUSES:
        return False, "Invalid status."
    if charger_has_active_session(charger_id):
        return False, "This charger has an active charging session. Cancel or finish it first."

    connection = get_connection()
    try:
        cursor = connection.execute(
            "UPDATE chargers SET status = ? WHERE charger_id = ?",
            (new_status, charger_id),
        )
        connection.commit()
        if cursor.rowcount == 0:
            return False, "Charger not found."
        return True, f"{charger_id} is now marked '{new_status}'."
    finally:
        connection.close()


# ---------------------------------------------------------------------------
# Wallet
# ---------------------------------------------------------------------------

def add_funds(user_id, amount):
    """
    SIMULATED top-up for a driver. No real money is involved.
    Balance update + transaction record happen in ONE database transaction.
    """
    try:
        amount = round(float(amount), 2)
    except (TypeError, ValueError):
        return False, "Please enter a valid amount."
    if amount < MIN_TOPUP or amount > MAX_TOPUP:
        return False, f"Top-up must be between {MIN_TOPUP:.0f} and {MAX_TOPUP:.0f}."

    user = get_user(user_id)
    if user is None or user["role"] != "driver":
        return False, "Only drivers have a wallet."

    connection = get_connection()
    try:
        connection.execute(
            "UPDATE users SET wallet_balance = ROUND(wallet_balance + ?, 2) WHERE user_id = ?",
            (amount, user_id),
        )
        connection.execute(
            "INSERT INTO wallet_transactions "
            "(user_id, transaction_type, amount, transaction_date, description, session_id) "
            "VALUES (?, 'Top-up', ?, ?, 'Demo credit (simulated top-up)', NULL)",
            (user_id, amount, now_text()),
        )
        connection.commit()
        return True, f"Added {amount:.2f} demo credit to your wallet."
    except Exception as error:
        connection.rollback()
        return False, f"Top-up failed: {error}"
    finally:
        connection.close()


# ---------------------------------------------------------------------------
# Charging sessions
# ---------------------------------------------------------------------------

def start_session(user_id, charger_id, spending_limit=None, energy_limit_kwh=None):
    """
    Start a charging session. Give EITHER a spending limit OR an energy limit.
    Returns (success, message, session_id).

    BEGIN IMMEDIATE locks the database for writing, so two people cannot
    grab the same charger at the same moment.
    """
    connection = get_connection()
    try:
        connection.execute("BEGIN IMMEDIATE")

        user = connection.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        ).fetchone()
        if user is None or user["role"] != "driver":
            raise ValueError("Only drivers can start charging sessions.")

        charger = connection.execute(
            "SELECT * FROM chargers WHERE charger_id = ?", (charger_id,)
        ).fetchone()
        if charger is None:
            raise ValueError("Charger not found.")
        if charger["status"] != "Available":
            raise ValueError(f"Charger {charger_id} is not available right now.")

        active_count = get_one_value(
            connection,
            "SELECT COUNT(*) FROM charging_sessions "
            "WHERE user_id = ? AND session_status = 'Active'",
            (user_id,),
        )
        if active_count > 0:
            raise ValueError("You already have an active charging session.")

        rate = charger["rate_per_kwh"]

        # Work out the limits
        if energy_limit_kwh is not None:
            if energy_limit_kwh <= 0:
                raise ValueError("Energy limit must be greater than zero.")
            max_energy = round(float(energy_limit_kwh), 2)
            limit = round(max_energy * rate, 2)
        elif spending_limit is not None:
            if spending_limit <= 0:
                raise ValueError("Spending limit must be greater than zero.")
            limit = round(float(spending_limit), 2)
            max_energy = round(limit / rate, 2)
        else:
            raise ValueError("Please choose a spending limit or an energy limit.")

        if limit > round(user["wallet_balance"], 2):
            raise ValueError("Your wallet balance is too low for this limit. Add demo credit first.")

        cursor = connection.execute(
            "INSERT INTO charging_sessions "
            "(user_id, charger_id, start_time, rate_per_kwh, spending_limit, "
            " max_energy_kwh, session_status) "
            "VALUES (?, ?, ?, ?, ?, ?, 'Active')",
            (user_id, charger_id, now_text(), rate, limit, max_energy),
        )
        session_id = cursor.lastrowid

        changed = connection.execute(
            "UPDATE chargers SET status = 'Occupied' "
            "WHERE charger_id = ? AND status = 'Available'",
            (charger_id,),
        ).rowcount
        if changed != 1:
            raise ValueError("Charger was taken by someone else. Please try another one.")

        connection.commit()
        return True, f"Charging started on {charger_id}.", session_id

    except ValueError as error:                 # expected problems -> clear message
        connection.rollback()
        return False, str(error), None
    except sqlite3.IntegrityError:              # database safety nets
        connection.rollback()
        return False, "Could not start: the charger or your account already has an active session.", None
    except Exception as error:
        connection.rollback()
        return False, f"Could not start the session: {error}", None
    finally:
        connection.close()


def stop_session(session_id, user_id, energy_kwh):
    """
    Finish a session. In ONE transaction we:
      1. mark the session Completed (only if it is still Active)
      2. deduct the final cost from the wallet
      3. record the wallet transaction
      4. release the charger
    If anything fails, everything is rolled back (no double charge).
    Returns (success, message, result_dictionary).
    """
    connection = get_connection()
    try:
        connection.execute("BEGIN IMMEDIATE")

        session = connection.execute(
            "SELECT * FROM charging_sessions WHERE session_id = ?", (session_id,)
        ).fetchone()
        if session is None:
            raise ValueError("Session not found.")
        if session["user_id"] != user_id:
            raise ValueError("This session belongs to another driver.")
        if session["session_status"] != "Active":
            raise ValueError("This session has already ended.")

        try:
            energy = round(float(energy_kwh), 2)
        except (TypeError, ValueError):
            raise ValueError("Please enter a valid energy value.")
        if energy < 0:
            raise ValueError("Energy cannot be negative.")

        # Respect the driver's limit
        if energy > session["max_energy_kwh"]:
            energy = session["max_energy_kwh"]
        cost = round(energy * session["rate_per_kwh"], 2)
        if cost > session["spending_limit"]:
            cost = session["spending_limit"]

        # 1. Complete the session (the WHERE stops double completion)
        changed = connection.execute(
            "UPDATE charging_sessions "
            "SET end_time = ?, energy_kwh = ?, total_cost = ?, session_status = 'Completed' "
            "WHERE session_id = ? AND session_status = 'Active'",
            (now_text(), energy, cost, session_id),
        ).rowcount
        if changed != 1:
            raise ValueError("This session has already ended.")

        # 2 and 3. Deduct from the wallet and record it
        if cost > 0:
            changed = connection.execute(
                "UPDATE users SET wallet_balance = ROUND(wallet_balance - ?, 2) "
                "WHERE user_id = ? AND wallet_balance >= ?",
                (cost, user_id, cost),
            ).rowcount
            if changed != 1:
                raise ValueError("Wallet balance is too low to complete this session.")

            connection.execute(
                "INSERT INTO wallet_transactions "
                "(user_id, transaction_type, amount, transaction_date, description, session_id) "
                "VALUES (?, 'Charging', ?, ?, ?, ?)",
                (user_id, -cost, now_text(),
                 f"Charging at {session['charger_id']} ({energy:.2f} kWh)", session_id),
            )

        # 4. Release the charger
        connection.execute(
            "UPDATE chargers SET status = 'Available' WHERE charger_id = ?",
            (session["charger_id"],),
        )

        connection.commit()
        result = {
            "charger_id": session["charger_id"],
            "energy_kwh": energy,
            "rate_per_kwh": session["rate_per_kwh"],
            "total_cost": cost,
        }
        return True, "Charging session completed.", result

    except ValueError as error:
        connection.rollback()
        return False, str(error), None
    except Exception as error:
        connection.rollback()
        return False, f"Could not complete the session: {error}", None
    finally:
        connection.close()


def cancel_session(operator_id, session_id):
    """Operator only: end a stuck active session, charge nothing, free the charger."""
    if not is_operator(operator_id):
        return False, "Only operators can cancel sessions."

    connection = get_connection()
    try:
        connection.execute("BEGIN IMMEDIATE")
        session = connection.execute(
            "SELECT * FROM charging_sessions WHERE session_id = ?", (session_id,)
        ).fetchone()
        if session is None or session["session_status"] != "Active":
            raise ValueError("Only active sessions can be cancelled.")

        connection.execute(
            "UPDATE charging_sessions "
            "SET end_time = ?, energy_kwh = 0, total_cost = 0, session_status = 'Cancelled' "
            "WHERE session_id = ? AND session_status = 'Active'",
            (now_text(), session_id),
        )
        connection.execute(
            "UPDATE chargers SET status = 'Available' WHERE charger_id = ?",
            (session["charger_id"],),
        )
        connection.commit()
        return True, f"Session {session_id} cancelled. {session['charger_id']} is available again."
    except ValueError as error:
        connection.rollback()
        return False, str(error)
    except Exception as error:
        connection.rollback()
        return False, f"Could not cancel the session: {error}"
    finally:
        connection.close()


def refund_session(operator_id, session_id):
    """Operator only: refund a completed session ONCE, back to the driver's wallet."""
    if not is_operator(operator_id):
        return False, "Only operators can issue refunds."

    connection = get_connection()
    try:
        connection.execute("BEGIN IMMEDIATE")
        session = connection.execute(
            "SELECT * FROM charging_sessions WHERE session_id = ?", (session_id,)
        ).fetchone()
        if session is None or session["session_status"] != "Completed" or session["total_cost"] <= 0:
            raise ValueError("Only completed, paid sessions can be refunded.")

        already_refunded = get_one_value(
            connection,
            "SELECT COUNT(*) FROM wallet_transactions "
            "WHERE session_id = ? AND transaction_type = 'Refund'",
            (session_id,),
        )
        if already_refunded > 0:
            raise ValueError("This session has already been refunded.")

        amount = session["total_cost"]
        connection.execute(
            "UPDATE users SET wallet_balance = ROUND(wallet_balance + ?, 2) WHERE user_id = ?",
            (amount, session["user_id"]),
        )
        connection.execute(
            "INSERT INTO wallet_transactions "
            "(user_id, transaction_type, amount, transaction_date, description, session_id) "
            "VALUES (?, 'Refund', ?, ?, ?, ?)",
            (session["user_id"], amount, now_text(),
             f"Refund for session {session_id}", session_id),
        )
        connection.commit()
        return True, f"Refunded {amount:.2f} for session {session_id}."
    except ValueError as error:
        connection.rollback()
        return False, str(error)
    except Exception as error:
        connection.rollback()
        return False, f"Refund failed: {error}"
    finally:
        connection.close()


# ---------------------------------------------------------------------------
# Reading sessions and transactions
# ---------------------------------------------------------------------------

def get_active_session(user_id):
    """The driver's current active session (with charger details) or None."""
    connection = get_connection()
    try:
        row = connection.execute(
            "SELECT s.*, c.charger_type, c.power_kw "
            "FROM charging_sessions s "
            "JOIN chargers c ON c.charger_id = s.charger_id "
            "WHERE s.user_id = ? AND s.session_status = 'Active'",
            (user_id,),
        ).fetchone()
    finally:
        connection.close()
    return dict(row) if row else None


def get_user_sessions(user_id, limit=None):
    sql = (
        "SELECT s.*, c.charger_type "
        "FROM charging_sessions s "
        "JOIN chargers c ON c.charger_id = s.charger_id "
        "WHERE s.user_id = ? ORDER BY s.session_id DESC"
    )
    params = [user_id]
    if limit is not None:
        sql += " LIMIT ?"
        params.append(limit)

    connection = get_connection()
    try:
        rows = connection.execute(sql, params).fetchall()
    finally:
        connection.close()
    return rows_to_dicts(rows)


def get_user_transactions(user_id, limit=None):
    sql = (
        "SELECT * FROM wallet_transactions "
        "WHERE user_id = ? ORDER BY transaction_id DESC"
    )
    params = [user_id]
    if limit is not None:
        sql += " LIMIT ?"
        params.append(limit)

    connection = get_connection()
    try:
        rows = connection.execute(sql, params).fetchall()
    finally:
        connection.close()
    return rows_to_dicts(rows)


def get_all_sessions(status=None, limit=None):
    """Operator view: every session with the driver's name and charger type."""
    sql = (
        "SELECT s.*, u.name AS driver_name, c.charger_type "
        "FROM charging_sessions s "
        "JOIN users u ON u.user_id = s.user_id "
        "JOIN chargers c ON c.charger_id = s.charger_id "
    )
    params = []
    if status is not None:
        sql += "WHERE s.session_status = ? "
        params.append(status)
    sql += "ORDER BY s.session_id DESC"
    if limit is not None:
        sql += " LIMIT ?"
        params.append(limit)

    connection = get_connection()
    try:
        rows = connection.execute(sql, params).fetchall()
    finally:
        connection.close()
    return rows_to_dicts(rows)


def get_all_transactions(limit=None):
    """Operator view: all payment / wallet records with the driver's name."""
    sql = (
        "SELECT t.*, u.name AS driver_name "
        "FROM wallet_transactions t "
        "JOIN users u ON u.user_id = t.user_id "
        "ORDER BY t.transaction_id DESC"
    )
    params = []
    if limit is not None:
        sql += " LIMIT ?"
        params.append(limit)

    connection = get_connection()
    try:
        rows = connection.execute(sql, params).fetchall()
    finally:
        connection.close()
    return rows_to_dicts(rows)


def get_refundable_sessions():
    """Completed, paid sessions that have no refund yet."""
    connection = get_connection()
    try:
        rows = connection.execute(
            "SELECT s.session_id, s.charger_id, s.energy_kwh, s.total_cost, "
            "       s.end_time, u.name AS driver_name "
            "FROM charging_sessions s "
            "JOIN users u ON u.user_id = s.user_id "
            "WHERE s.session_status = 'Completed' AND s.total_cost > 0 "
            "AND s.session_id NOT IN ("
            "    SELECT session_id FROM wallet_transactions "
            "    WHERE transaction_type = 'Refund' AND session_id IS NOT NULL) "
            "ORDER BY s.session_id DESC"
        ).fetchall()
    finally:
        connection.close()
    return rows_to_dicts(rows)


# ---------------------------------------------------------------------------
# Operator statistics and reports (all calculated from real data)
# ---------------------------------------------------------------------------

def get_site_stats():
    connection = get_connection()
    try:
        stats = {
            "total_chargers": get_one_value(connection, "SELECT COUNT(*) FROM chargers"),
            "available": get_one_value(
                connection, "SELECT COUNT(*) FROM chargers WHERE status = 'Available'"),
            "occupied": get_one_value(
                connection, "SELECT COUNT(*) FROM chargers WHERE status = 'Occupied'"),
            "out_of_service": get_one_value(
                connection, "SELECT COUNT(*) FROM chargers WHERE status = 'Out of Service'"),
            "active_sessions": get_one_value(
                connection,
                "SELECT COUNT(*) FROM charging_sessions WHERE session_status = 'Active'"),
            "completed_sessions": get_one_value(
                connection,
                "SELECT COUNT(*) FROM charging_sessions WHERE session_status = 'Completed'"),
            "total_energy": get_one_value(
                connection,
                "SELECT SUM(energy_kwh) FROM charging_sessions WHERE session_status = 'Completed'"),
            # Charging amounts are stored as negatives, refunds as positives,
            # so net revenue = minus the sum of both types.
            "net_revenue": -get_one_value(
                connection,
                "SELECT SUM(amount) FROM wallet_transactions "
                "WHERE transaction_type IN ('Charging', 'Refund')"),
            "total_refunds": get_one_value(
                connection,
                "SELECT SUM(amount) FROM wallet_transactions WHERE transaction_type = 'Refund'"),
            "total_topups": get_one_value(
                connection,
                "SELECT SUM(amount) FROM wallet_transactions WHERE transaction_type = 'Top-up'"),
            "driver_count": get_one_value(
                connection, "SELECT COUNT(*) FROM users WHERE role = 'driver'"),
        }
    finally:
        connection.close()
    return stats


def get_charger_utilisation():
    """
    One row per charger: number of completed sessions, energy, billed amount
    and total charging minutes.

    LEFT JOIN keeps chargers that have NO sessions yet (they show 0).
    GROUP BY gives one result row per charger.
    julianday() turns a date-time into a number of days, so subtracting two
    of them and multiplying by 24*60 gives minutes.
    """
    connection = get_connection()
    try:
        rows = connection.execute(
            "SELECT c.charger_id, c.charger_type, c.status, "
            "       COUNT(s.session_id) AS sessions, "
            "       COALESCE(SUM(s.energy_kwh), 0) AS energy_kwh, "
            "       COALESCE(SUM(s.total_cost), 0) AS billed, "
            "       COALESCE(SUM((julianday(s.end_time) - julianday(s.start_time)) * 24 * 60), 0) "
            "           AS minutes "
            "FROM chargers c "
            "LEFT JOIN charging_sessions s "
            "       ON s.charger_id = c.charger_id AND s.session_status = 'Completed' "
            "GROUP BY c.charger_id "
            "ORDER BY c.charger_id"
        ).fetchall()
    finally:
        connection.close()
    return rows_to_dicts(rows)


def get_daily_summary():
    """Sessions, energy and billed amount per day (last 14 days with activity)."""
    connection = get_connection()
    try:
        rows = connection.execute(
            "SELECT substr(end_time, 1, 10) AS day, "
            "       COUNT(*) AS sessions, "
            "       SUM(energy_kwh) AS energy_kwh, "
            "       SUM(total_cost) AS billed "
            "FROM charging_sessions "
            "WHERE session_status = 'Completed' "
            "GROUP BY substr(end_time, 1, 10) "
            "ORDER BY day DESC LIMIT 14"
        ).fetchall()
    finally:
        connection.close()
    return rows_to_dicts(rows)


def get_type_summary():
    """Energy and billed amount grouped by charger type."""
    connection = get_connection()
    try:
        rows = connection.execute(
            "SELECT c.charger_type, COUNT(s.session_id) AS sessions, "
            "       COALESCE(SUM(s.energy_kwh), 0) AS energy_kwh, "
            "       COALESCE(SUM(s.total_cost), 0) AS billed "
            "FROM chargers c "
            "LEFT JOIN charging_sessions s "
            "       ON s.charger_id = c.charger_id AND s.session_status = 'Completed' "
            "GROUP BY c.charger_type "
            "ORDER BY c.charger_type"
        ).fetchall()
    finally:
        connection.close()
    return rows_to_dicts(rows)


def get_top_drivers(limit=5):
    """Drivers ranked by total billed amount."""
    connection = get_connection()
    try:
        rows = connection.execute(
            "SELECT u.name, COUNT(s.session_id) AS sessions, "
            "       SUM(s.energy_kwh) AS energy_kwh, SUM(s.total_cost) AS billed "
            "FROM users u "
            "JOIN charging_sessions s ON s.user_id = u.user_id "
            "WHERE s.session_status = 'Completed' "
            "GROUP BY u.user_id "
            "ORDER BY billed DESC LIMIT ?",
            (limit,),
        ).fetchall()
    finally:
        connection.close()
    return rows_to_dicts(rows)
