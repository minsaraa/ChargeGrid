"""
chargegrid_app.py - ChargeGrid user interface (Streamlit)

Run with:   python -m streamlit run chargegrid_app.py

This file only draws the interface and calls functions from database.py.
It contains NO SQL.
"""

import streamlit as st
import database as db

st.set_page_config(
    page_title="ChargeGrid",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------------------------
# STYLE (your original ChargeGrid CSS, plus small additions for tabs/forms)
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');

header[data-testid="stHeader"] {
    background: transparent !important;
    box-shadow: none !important;
    border-bottom: none !important;
}

[data-testid="stAppDeployButton"],
.stDeployButton {
    display: none !important;
}

[data-testid="stExpandSidebarButton"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    z-index: 999999 !important;
    background: #E5F8CC !important;
    border: 1px solid #B8E58A !important;
    border-radius: 8px !important;
}

[data-testid="stExpandSidebarButton"] *,
[data-testid="stSidebarCollapsedControl"] *,
[data-testid="collapsedControl"] *,
[data-testid="stSidebarCollapseButton"] * {
    color: #263528 !important;
    fill: #263528 !important;
    opacity: 1 !important;
    visibility: visible !important;
}

[data-testid="stSidebarCollapseButton"] {
    opacity: 1 !important;
    visibility: visible !important;
}

[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
#MainMenu,
footer {
    display: none !important;
}

section[data-testid="stSidebar"] {
    display: block !important;
    visibility: visible !important;
    background: #F5F8F2 !important;
    border-right: 1px solid #E4EBDD !important;
}

section[data-testid="stSidebar"] > div {
    visibility: visible !important;
    background: #F5F8F2 !important;
}

[data-testid="stAppViewBlockContainer"],
[data-testid="stMainBlockContainer"],
.main .block-container {
    padding-top: 3.5rem !important;
    margin-top: 0 !important;
}

[data-testid="stAppViewBlockContainer"] {
    padding-bottom: 1.5rem !important;
    max-width: 1250px;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background: #FFFFFF;
    color: #263528;
}

h1, h2, h3 {
    font-family: 'DM Sans', sans-serif !important;
    color: #263528 !important;
    letter-spacing: -0.01em;
}

h1 {
    margin-top: 0 !important;
    padding-top: 0 !important;
    margin-bottom: 0.2rem !important;
    font-size: 2rem !important;
}

p, label {
    color: #263528;
}

.brand {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 18px;
}

.brand-logo {
    width: 42px;
    height: 42px;
    flex-shrink: 0;
    background-color: #202820;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'%3E%3Cpolygon points='13,2 4,14 11,14 10,22 20,9 13,9' fill='%23B8FF4D' stroke='%23B8FF4D' stroke-width='1.2' stroke-linejoin='round'/%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: center;
    background-size: 24px 24px;
    border-radius: 12px;
}

.brand-name {
    font-family: 'DM Sans', sans-serif;
    font-size: 28px;
    font-weight: 700;
    color: #263528;
    line-height: 1;
}

[data-testid="stSidebar"] * {
    color: #263528;
}

[data-testid="stSidebar"] [role="radiogroup"] {
    gap: 8px;
}

[data-testid="stSidebar"] [role="radiogroup"] label {
    background: transparent !important;
    border-radius: 8px;
    padding: 10px 12px;
    border: 1px solid transparent;
}

[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background: #EAF4E1 !important;
}

[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
    background: #E5F8CC !important;
    border: 1px solid #B8E58A;
    font-weight: 700;
}

input[type="radio"] {
    accent-color: #548D00;
}

div[data-testid="stTextInput"] div[data-baseweb="input"],
div[data-testid="stTextInput"] div[data-baseweb="base-input"],
div[data-testid="stTextInputRootElement"] {
    background: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    box-shadow: none !important;
    outline: none !important;
}

div[data-testid="stTextInput"] div[data-baseweb="input"] {
    position: relative !important;
    height: 44px !important;
    overflow: visible !important;
}

div[data-testid="stTextInput"] input {
    background: #FFFFFF !important;
    color: #263528 !important;
    border: 1px solid #D8E2D1 !important;
    border-radius: 10px !important;
    height: 44px !important;
    padding: 0 52px 0 14px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    caret-color: #548D00 !important;
}

div[data-testid="stTextInput"] input::placeholder {
    color: #8A968A !important;
    -webkit-text-fill-color: #8A968A !important;
    opacity: 1 !important;
}

div[data-testid="stTextInput"] input:focus {
    border: 1.5px solid #548D00 !important;
    box-shadow: 0 0 0 2px rgba(84, 141, 0, 0.12) !important;
    outline: none !important;
}

div[data-testid="stNumberInput"] div[data-baseweb="input"],
div[data-testid="stNumberInput"] div[data-baseweb="base-input"] {
    background: #FFFFFF !important;
    border-radius: 10px !important;
}

div[data-testid="stNumberInput"] div[data-baseweb="input"] {
    border: 1px solid #D8E2D1 !important;
}

div[data-testid="stNumberInput"] input {
    background: #FFFFFF !important;
    color: #263528 !important;
}

div[data-testid="stNumberInput"] button {
    background: #F5F8F2 !important;
    color: #263528 !important;
    border: none !important;
}

div[data-testid="stNumberInput"] button svg {
    fill: #263528 !important;
    color: #263528 !important;
}

div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    background: #FFFFFF !important;
    color: #263528 !important;
    border: 1px solid #D8E2D1 !important;
    border-radius: 10px !important;
    min-height: 44px !important;
    cursor: pointer !important;
}

div[data-testid="stSelectbox"] svg {
    fill: #263528 !important;
    color: #263528 !important;
    opacity: 1 !important;
}

div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:focus-within {
    border-color: #548D00 !important;
    box-shadow: 0 0 0 2px rgba(84, 141, 0, 0.12) !important;
}

div[data-baseweb="popover"],
div[data-baseweb="menu"] {
    background: #FFFFFF !important;
}

div[role="option"] {
    color: #263528 !important;
}

div[role="option"]:hover {
    background: #EAF4E1 !important;
}

.stButton > button,
.stFormSubmitButton > button {
    background: #B8FF4D;
    color: #263528 !important;
    border: 1px solid #A8ED43;
    border-radius: 999px;
    padding: 0.55rem 1.5rem;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600;
}

.stButton > button p,
.stFormSubmitButton > button p {
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    background: #A8ED43;
    border-color: #8FCB32;
}

.stButton > button:disabled {
    background: #EEF2EA;
    color: #8A968A !important;
    border: 1px solid #D8E2D1;
}

[class*="st-key-card_"] {
    border: 1px solid #C9D6BF;
    border-radius: 14px;
    padding: 16px 18px;
    background: #FFFFFF;
    box-sizing: border-box;
}

.station-title {
    font-family: 'DM Sans', sans-serif;
    font-size: 20px;
    font-weight: 700;
    color: #263528;
}

.station-location {
    color: #667366;
    font-size: 14px;
}

.station-detail {
    color: #425142;
    font-size: 13px;
}

.price {
    color: #548D00;
    font-size: 20px;
    font-weight: 700;
}

.available {
    color: #387A12;
    background: #E9F8DE;
    border-radius: 20px;
    padding: 5px 10px;
    font-size: 12px;
    font-weight: 700;
}

.unavailable {
    color: #B42318;
    background: #FDECEC;
    border-radius: 20px;
    padding: 5px 10px;
    font-size: 12px;
    font-weight: 700;
}

.occupied {
    color: #8A5A00;
    background: #FFF4DB;
    border-radius: 20px;
    padding: 5px 10px;
    font-size: 12px;
    font-weight: 700;
}

hr {
    border-color: #E4EBDD;
}

[data-testid="stMetric"] {
    background: #F7FAF4;
    border: 1px solid #E4EBDD;
    border-radius: 12px;
    padding: 14px;
}

[data-testid="stMetricLabel"],
[data-testid="stMetricValue"] {
    color: #263528 !important;
}

/* Additions for tabs and forms so they match the green theme */
button[data-baseweb="tab"] {
    color: #425142 !important;
    font-weight: 600;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #387A12 !important;
}

div[data-baseweb="tab-highlight"] {
    background-color: #548D00 !important;
}

div[data-baseweb="tab-border"] {
    background-color: #E4EBDD !important;
}

[data-testid="stForm"] {
    border: 1px solid #C9D6BF;
    border-radius: 14px;
    background: #FFFFFF;
}

/* Rounded pill buttons everywhere */
[data-testid="stExpandSidebarButton"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] {
    border-radius: 999px !important;
}

[data-testid="stSidebar"] [role="radiogroup"] label {
    border-radius: 999px !important;
    padding: 10px 18px;
}

div[data-testid="stNumberInput"] button {
    border-radius: 999px !important;
}

button[data-baseweb="tab"] {
    border-radius: 999px !important;
}

/* Logout confirmation dialog: Cancel = red, Logout = black */
.st-key-cancel_logout_btn button {
    background: #D92D20 !important;
    border: 1px solid #B42318 !important;
}

.st-key-cancel_logout_btn button:hover {
    background: #B42318 !important;
    border-color: #912018 !important;
}

.st-key-confirm_logout_btn button {
    background: #000000 !important;
    border: 1px solid #000000 !important;
}

.st-key-confirm_logout_btn button:hover {
    background: #263528 !important;
    border-color: #263528 !important;
}

.st-key-cancel_logout_btn button,
.st-key-cancel_logout_btn button p,
.st-key-confirm_logout_btn button,
.st-key-confirm_logout_btn button p {
    color: #FFFFFF !important;
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# START-UP: make sure the database exists (safe to run on every rerun)
# ---------------------------------------------------------------------------
db.init_database()

DRIVER_PAGES = ["Charge Here", "My Sessions", "My Wallet", "Bills & Transactions"]
OPERATOR_PAGES = ["Dashboard", "Charger Management", "Charging Sessions",
                  "Billing & Revenue", "Reports"]

# Streamlit reruns this whole file after every click, so anything that must
# be remembered lives in st.session_state.
defaults = {
    "user": None,               # the logged-in user (dictionary) or None
    "page": None,               # current sidebar page
    "last_page": None,
    "nav_target": None,         # set this to jump to another page
    "charging_charger": None,   # charger chosen on "Charge Here"
    "flash": "",                # one-time message shown on the next page
    "flash_kind": "success",
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ---------------------------------------------------------------------------
# Small helper functions
# ---------------------------------------------------------------------------
def money(amount):
    return f"₹{amount:,.2f}"


def signed_money(amount):
    if amount >= 0:
        return f"+₹{amount:,.2f}"
    return f"-₹{abs(amount):,.2f}"


def set_flash(text, kind="success"):
    st.session_state.flash = text
    st.session_state.flash_kind = kind


def show_flash():
    if st.session_state.flash:
        if st.session_state.flash_kind == "error":
            st.error(st.session_state.flash)
        else:
            st.success(st.session_state.flash)
        st.session_state.flash = ""


def go_to(page_name):
    st.session_state.nav_target = page_name
    st.rerun()


def log_out():
    st.session_state.user = None
    st.session_state.last_page = None
    st.session_state.charging_charger = None
    st.session_state.nav_target = None
    st.session_state.flash = ""


@st.dialog("Logout")
def confirm_logout():
    """Pop-up that asks before the user is logged out."""
    st.write("Are you sure you want to logout?")
    cancel_col, logout_col = st.columns(2)
    with cancel_col:
        if st.button("Cancel", key="cancel_logout_btn", use_container_width=True):
            st.rerun()          # closes the pop-up, user stays logged in
    with logout_col:
        if st.button("Logout", key="confirm_logout_btn", use_container_width=True):
            log_out()
            st.rerun()


def show_brand():
    st.markdown("""
    <div class="brand">
        <div class="brand-logo"></div>
        <div class="brand-name">ChargeGrid</div>
    </div>
    """, unsafe_allow_html=True)


def status_badge(status):
    if status == "Available":
        return '<span class="available">● Available</span>'
    if status == "Occupied":
        return '<span class="occupied">● Occupied</span>'
    return '<span class="unavailable">● Out of Service</span>'


def format_minutes(minutes):
    minutes = int(minutes)
    if minutes >= 60:
        return f"{minutes // 60} h {minutes % 60} min"
    return f"{minutes} min"


def sessions_table(sessions, include_driver=False):
    """Turn session dictionaries into rows with friendly column names."""
    rows = []
    for s in sessions:
        row = {"Session": s["session_id"]}
        if include_driver:
            row["Driver"] = s["driver_name"]
        row["Charger"] = s["charger_id"]
        row["Type"] = s["charger_type"]
        row["Started"] = s["start_time"]
        row["Ended"] = s["end_time"] if s["end_time"] else "-"
        row["Energy (kWh)"] = round(s["energy_kwh"], 2)
        row["Rate (₹/kWh)"] = s["rate_per_kwh"]
        row["Cost (₹)"] = round(s["total_cost"], 2)
        row["Status"] = s["session_status"]
        rows.append(row)
    return rows


def transactions_table(transactions, include_driver=False):
    rows = []
    for t in transactions:
        row = {"ID": t["transaction_id"]}
        if include_driver:
            row["Driver"] = t["driver_name"]
        row["Date"] = t["transaction_date"]
        row["Type"] = t["transaction_type"]
        row["Amount"] = signed_money(t["amount"])
        row["Description"] = t["description"]
        row["Session"] = t["session_id"] if t["session_id"] else "-"
        rows.append(row)
    return rows


def show_table(rows, empty_message):
    if rows:
        st.dataframe(rows, use_container_width=True, hide_index=True)
    else:
        st.info(empty_message)


def operator_back_button(page_name):
    """Every operator page except the dashboard gets a quick way back."""
    if page_name != "Dashboard":
        if st.button("← Back to Dashboard", key="back_dashboard_" + page_name):
            go_to("Dashboard")


# ---------------------------------------------------------------------------
# Refresh the logged-in user from the database on every rerun
# (so the balance and role are always current and cannot be faked)
# ---------------------------------------------------------------------------
if st.session_state.user is not None:
    fresh_user = db.get_user(st.session_state.user["user_id"])
    if fresh_user is None:
        log_out()
    else:
        st.session_state.user = fresh_user

user = st.session_state.user

# Choose the sidebar pages for this role and handle page jumps.
# This must happen BEFORE the sidebar radio is drawn.
if user is not None:
    if user["role"] == "operator":
        page_options = OPERATOR_PAGES
    else:
        page_options = DRIVER_PAGES

    if st.session_state.nav_target:
        st.session_state.page = st.session_state.nav_target
        st.session_state.nav_target = None

    if st.session_state.page not in page_options:
        st.session_state.page = page_options[0]

    if st.session_state.page != st.session_state.last_page:
        st.session_state.charging_charger = None
        st.session_state.last_page = st.session_state.page


# ---------------------------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# SIDEBAR - SHOW ONLY AFTER LOGIN
# ---------------------------------------------------------------------------

if user is not None:
    with st.sidebar:
        st.markdown("""
        <div style="padding:8px 0 20px 0;">
            <div style="font-family:'DM Sans',sans-serif;font-size:28px;font-weight:700;color:#263528;">
                ⚡ ChargeGrid
            </div>
            <div style="font-size:12px;color:#667366;">
                POWERING SMARTER JOURNEYS
            </div>
        </div>
        """, unsafe_allow_html=True)

        role_label = "Operator" if user["role"] == "operator" else "Driver"

        st.markdown(f"""
        <div style="background:#FFFFFF;border:1px solid #E4EBDD;border-radius:10px;padding:10px 12px;margin-bottom:14px;">
            <div style="font-size:14px;font-weight:700;">{user['name']}</div>
            <div style="font-size:12px;color:#667366;">{role_label} · {user['email']}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### MENU")

        st.radio(
            "Navigation",
            page_options,
            key="page",
            label_visibility="collapsed"
        )

        st.write("")

        if st.button("Logout", key="logout_btn", use_container_width=True):
            confirm_logout()

        st.divider()

        st.markdown(f"""
        <div style="background:#E9F8DE;border:1px solid #D7EBC8;border-radius:10px;padding:12px;">
            <div style="font-size:13px;font-weight:700;">● {db.SITE_NAME}</div>
            <div style="font-size:12px;margin-top:4px;">Demo charging site</div>
        </div>
        """, unsafe_allow_html=True)

        st.caption("ChargeGrid · Student Project")

else:
    # Hide the sidebar completely on the login/register page.
    st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }

        [data-testid="stSidebarCollapsedControl"] {
            display: none;
        }

        [data-testid="stExpandSidebarButton"] {
            display: none;
        }

        section[data-testid="stMain"] {
            margin-left: 0;
        }
    </style>
    """, unsafe_allow_html=True)


# ===========================================================================
# LOGIN / REGISTER PAGE
# ===========================================================================
def show_login_page():
    # Three columns: the middle one holds the whole login screen, so it sits
    # in the centre of the page and is not stretched across the full width.
    # Change the numbers to make the middle column wider or narrower.
    left_space, center, right_space = st.columns([1, 1.3, 1])

    with center:
        show_brand()
        st.title("Welcome to ChargeGrid")
        st.write(f"**{db.SITE_NAME}** · {db.SITE_NOTE}")
        show_flash()

        login_tab, register_tab = st.tabs(["Log in", "Create driver account"])

        with login_tab:
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="you@example.com")
                password = st.text_input("Password", type="password", placeholder="Your password")
                login_clicked = st.form_submit_button("Log in")

            if login_clicked:
                found_user = db.login_user(email, password)
                if found_user is None:
                    st.error("Incorrect email or password.")
                else:
                    st.session_state.user = found_user
                    if found_user["role"] == "operator":
                        st.session_state.page = "Dashboard"
                    else:
                        st.session_state.page = "Charge Here"
                    st.session_state.last_page = st.session_state.page
                    st.rerun()

            with st.expander("Demo operator account"):
                st.write(f"Email: `{db.DEMO_OPERATOR_EMAIL}`")
                st.write(f"Password: `{db.DEMO_OPERATOR_PASSWORD}`")
                st.caption("For classroom demonstration only.")

        with register_tab:
            with st.form("register_form"):
                new_name = st.text_input("Full name", placeholder="Your name")
                new_email = st.text_input("Email address", placeholder="you@example.com", key="reg_email")
                new_password = st.text_input("Password (min 6 characters)", type="password", key="reg_pw")
                confirm_password = st.text_input("Confirm password", type="password", key="reg_pw2")
                register_clicked = st.form_submit_button("Create account")

            if register_clicked:
                if new_password != confirm_password:
                    st.error("The two passwords do not match.")
                else:
                    ok, message = db.register_user(new_name, new_email, new_password)
                    if ok:
                        st.success(message + " Use the 'Log in' tab.")
                    else:
                        st.error(message)


# ===========================================================================
# DRIVER PAGES
# ===========================================================================
def show_active_session(user, active):
    """Panel with the running session and the Stop button."""
    charger = db.make_charger(db.get_charger(active["charger_id"]))
    session = db.ChargingSession(
        active["session_id"], user["user_id"], charger, active["start_time"],
        active["rate_per_kwh"], active["spending_limit"], active["max_energy_kwh"]
    )

    with st.container(key="card_active_session"):
        st.markdown(
            f'<div class="station-title">Active session · {active["charger_id"]}</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            f'<div class="station-location">{charger.describe()} · started {active["start_time"]}</div>',
            unsafe_allow_html=True
        )
        st.write("")

        a1, a2, a3, a4 = st.columns(4)
        a1.metric("Elapsed (real time)", format_minutes(session.get_elapsed_seconds() // 60)
                  if session.get_elapsed_seconds() >= 60 else f"{session.get_elapsed_seconds()} s")
        a2.metric("Rate", f"₹{active['rate_per_kwh']:.2f}/kWh")
        a3.metric("Max energy", f"{active['max_energy_kwh']:.2f} kWh")
        a4.metric("Spending limit", money(active["spending_limit"]))

        st.markdown("**Charging simulation (demo data)**")
        st.caption(
            "ChargeGrid cannot control real hardware. In this demo, 1 real second counts as "
            "1 minute of charging. Press refresh to update the simulated reading, or enter "
            "the energy by hand."
        )

        simulated = session.simulate_energy()
        reading_mode = st.radio(
            "Energy reading",
            ["Use simulated reading", "Enter energy manually"],
            horizontal=True,
            key=f"reading_mode_{active['session_id']}"
        )

        if reading_mode == "Use simulated reading":
            energy_value = simulated
        else:
            energy_value = st.number_input(
                "Energy consumed (kWh) - demo value",
                min_value=0.0,
                max_value=float(active["max_energy_kwh"]),
                value=float(simulated),
                step=0.5,
                key=f"manual_energy_{active['session_id']}"
            )

        final_cost = session.calculate_final_cost(energy_value)

        e1, e2, e3 = st.columns(3)
        e1.metric("Energy so far", f"{energy_value:.2f} kWh")
        e2.metric("Cost so far", money(final_cost))
        e3.metric("Wallet after stopping", money(user["wallet_balance"] - final_cost))

        b1, b2 = st.columns(2)
        with b1:
            st.button("↻ Refresh reading", key="refresh_reading", use_container_width=True)
        with b2:
            if st.button("Stop charging", key="stop_charging", use_container_width=True):
                ok, message, result = db.stop_session(
                    active["session_id"], user["user_id"], energy_value
                )
                if ok:
                    set_flash(
                        f"Session complete: {result['energy_kwh']:.2f} kWh at "
                        f"{result['charger_id']} for {money(result['total_cost'])} "
                        f"(demo charging)."
                    )
                    go_to("My Sessions")
                else:
                    st.error(message)


def show_start_charging(user):
    """The 'choose your limit and start' screen for one charger."""
    charger_row = db.get_charger(st.session_state.charging_charger)

    if st.button("← Back", key="back_btn"):
        st.session_state.charging_charger = None
        st.rerun()

    st.title("Start Charging")

    if charger_row is None or charger_row["status"] != "Available":
        st.info("This charger is no longer available. Use the back button to pick another one.")
        return

    charger = db.make_charger(charger_row)
    rate = charger.rate_per_kwh
    balance = user["wallet_balance"]

    st.markdown(f'<div class="station-title">{charger.charger_id}</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="station-location">{db.SITE_NAME} · {charger.get_speed_label()}</div>',
        unsafe_allow_html=True
    )
    st.write("")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Charger type", charger.charger_type)
    c2.metric("Charging power", f"{charger.power_kw:g} kW")
    c3.metric("Rate", f"₹{rate:.2f}/kWh")
    c4.metric("Your wallet", money(balance))

    st.divider()
    st.subheader("Charging limit")

    min_spend = 10.0
    if balance < min_spend:
        st.warning("Your wallet balance is too low to start charging. Add demo credit first.")
        if st.button("Go to My Wallet", key="go_wallet_low"):
            go_to("My Wallet")
        return

    mode = st.radio(
        "Limit by",
        ["Spending limit (₹)", "Energy limit (kWh)"],
        horizontal=True,
        label_visibility="collapsed"
    )

    if mode == "Spending limit (₹)":
        spend = st.number_input(
            "Maximum amount to spend (₹)",
            min_value=min_spend,
            max_value=float(balance),
            value=float(min(200.0, balance)),
            step=10.0
        )
        spending_limit = round(spend, 2)
        energy_limit = None
        max_energy = spending_limit / rate
    else:
        most_energy = float(int(balance / rate * 100) / 100)
        if most_energy < 1.0:
            st.warning("Your wallet balance is too low for an energy limit. Add demo credit first.")
            return
        energy_limit = st.number_input(
            "Maximum energy (kWh)",
            min_value=1.0,
            max_value=most_energy,
            value=float(min(20.0, most_energy)),
            step=1.0
        )
        energy_limit = round(energy_limit, 2)
        spending_limit = None
        max_energy = energy_limit

    max_cost = charger.calculate_cost(max_energy)
    if spending_limit is not None:
        max_cost = min(max_cost, spending_limit)

    st.markdown("### Summary")
    s1, s2, s3 = st.columns(3)
    s1.metric("Up to", f"{max_energy:.2f} kWh")
    s2.metric("Cost will not exceed", money(max_cost))
    s3.metric("Est. time", format_minutes(charger.estimate_minutes(max_energy)))
    st.caption(
        "You only pay for the energy actually delivered when you stop. "
        "Time is an estimate; this is a demo with simulated values."
    )

    if st.button("Start Charging", key="start_charging_btn", use_container_width=True):
        ok, message, session_id = db.start_session(
            user["user_id"], charger.charger_id,
            spending_limit=spending_limit, energy_limit_kwh=energy_limit
        )
        if ok:
            set_flash(f"{message} Press 'Stop charging' when you are done.")
            st.session_state.charging_charger = None
            st.rerun()
        else:
            st.error(message)


def page_charge_here(user):
    show_brand()

    if st.session_state.charging_charger and not db.get_active_session(user["user_id"]):
        show_start_charging(user)
        return
    st.session_state.charging_charger = None

    st.title("Charge Here")
    st.markdown(f"**{db.SITE_NAME}** · {db.SITE_NOTE}")
    show_flash()

    chargers = db.get_available_chargers()
    active = db.get_active_session(user["user_id"])

    m1, m2 = st.columns(2)
    m1.metric("Wallet balance", money(user["wallet_balance"]))
    m2.metric("Chargers available now", len(chargers))

    if active:
        st.write("")
        show_active_session(user, active)

    st.write("")
    st.subheader("Available chargers")

    if active:
        st.caption("You have an active session. Stop it before starting another one.")
    elif not chargers:
        st.info("All chargers are busy or out of service right now. Please check back soon.")

    for row in chargers:
        charger = db.make_charger(row)
        with st.container(key="card_" + charger.charger_id):
            info_col, power_col, rate_col, action_col = st.columns(
                [1, 1, 1, 1], vertical_alignment="center"
            )

            with info_col:
                st.markdown(f'<div class="station-title">{charger.charger_id}</div>',
                            unsafe_allow_html=True)
                st.markdown(f'<div class="station-location">{charger.charger_type}</div>',
                            unsafe_allow_html=True)

            with power_col:
                st.markdown('<div class="station-detail">POWER</div>', unsafe_allow_html=True)
                st.write(f"**{charger.power_kw:g} kW**")

            with rate_col:
                st.markdown(f'<div class="price">₹{charger.rate_per_kwh:.2f}/kWh</div>',
                            unsafe_allow_html=True)
                st.markdown(status_badge(charger.status), unsafe_allow_html=True)

            with action_col:
                if st.button("Charge →", key="charge_" + charger.charger_id,use_container_width=True):
                    current_active = db.get_active_session(user["user_id"])

                    if current_active is not None:
                        st.warning("You cannot have two charging sessions running "
                                   "simultaneously. Please stop your current session "
                                   "before starting another one.")
                    else:
                        st.session_state.charging_charger = charger.charger_id
                        st.rerun()


def page_my_sessions(user):
    st.title("My Sessions")
    st.write("View your charging session history.")
    show_flash()

    active = db.get_active_session(user["user_id"])
    if active:
        st.info(f"You have an active session on {active['charger_id']}.")
        if st.button("Go to the active session", key="goto_active"):
            go_to("Charge Here")

    sessions = db.get_user_sessions(user["user_id"])
    completed = [s for s in sessions if s["session_status"] == "Completed"]

    m1, m2, m3 = st.columns(3)
    m1.metric("Completed sessions", len(completed))
    m2.metric("Total energy", f"{sum(s['energy_kwh'] for s in completed):.2f} kWh")
    m3.metric("Total spent", money(sum(s["total_cost"] for s in completed)))

    st.subheader("Session History")
    show_table(sessions_table(sessions), "You haven't started any sessions yet.")

    if st.button("Start a new session", key="new_session_btn"):
        go_to("Charge Here")


def page_my_wallet(user):
    st.title("My Wallet")
    st.write("Add demo credit and see your latest wallet activity.")
    show_flash()

    st.metric("Current balance", money(user["wallet_balance"]))

    st.subheader("Add demo credit")
    with st.form("topup_form"):
        amount = st.number_input(
            f"Amount (₹{db.MIN_TOPUP:.0f} to ₹{db.MAX_TOPUP:,.0f})",
            min_value=db.MIN_TOPUP,
            max_value=db.MAX_TOPUP,
            value=500.0,
            step=50.0
        )
        topup_clicked = st.form_submit_button("Add demo credit")
    st.caption("This is a simulated top-up. No real money is transferred.")

    if topup_clicked:
        ok, message = db.add_funds(user["user_id"], amount)
        if ok:
            set_flash(message)
            st.rerun()
        else:
            st.error(message)

    st.subheader("Recent wallet activity")
    show_table(
        transactions_table(db.get_user_transactions(user["user_id"], limit=10)),
        "No wallet activity yet."
    )


def page_bills(user):
    st.title("Bills & Transactions")
    st.write("Review the cost of each completed session and your wallet history.")

    bills_tab, transactions_tab = st.tabs(["Bills", "Wallet transactions"])

    with bills_tab:
        sessions = db.get_user_sessions(user["user_id"])
        completed = [s for s in sessions if s["session_status"] == "Completed"]

        b1, b2 = st.columns(2)
        b1.metric("Total energy charged", f"{sum(s['energy_kwh'] for s in completed):.2f} kWh")
        b2.metric("Total billed", money(sum(s["total_cost"] for s in completed)))

        show_table(sessions_table(completed), "No bills yet. Complete a charging session first.")
        st.caption("Bill = energy (kWh) × rate (₹/kWh). All amounts are simulated.")

    with transactions_tab:
        show_table(
            transactions_table(db.get_user_transactions(user["user_id"])),
            "No transactions yet."
        )
        st.caption("Top-ups and refunds are positive, charging deductions are negative.")


# ===========================================================================
# OPERATOR PAGES
# ===========================================================================
def page_dashboard(user):
    show_brand()
    st.title("Operator Dashboard")
    st.write(f"**{db.SITE_NAME}** · {db.SITE_NOTE}")
    show_flash()

    stats = db.get_site_stats()

    r1 = st.columns(4)
    r1[0].metric("Total chargers", stats["total_chargers"])
    r1[1].metric("Available", stats["available"])
    r1[2].metric("Occupied", stats["occupied"])
    r1[3].metric("Out of service", stats["out_of_service"])

    r2 = st.columns(3)
    r2[0].metric("Active sessions", stats["active_sessions"])
    r2[1].metric("Energy delivered", f"{stats['total_energy']:.2f} kWh")
    r2[2].metric("Charging revenue (net)", money(stats["net_revenue"]))

    st.subheader("Charger status")
    charger_rows = []
    for c in db.get_all_chargers():
        charger_rows.append({
            "Charger": c["charger_id"],
            "Type": c["charger_type"],
            "Power (kW)": c["power_kw"],
            "Rate (₹/kWh)": c["rate_per_kwh"],
            "Status": c["status"],
        })
    show_table(charger_rows, "No chargers yet.")

    st.subheader("Recent sessions")
    show_table(
        sessions_table(db.get_all_sessions(limit=8), include_driver=True),
        "No charging sessions yet."
    )


def page_charger_management(user):
    operator_back_button("Charger Management")
    st.title("Charger Management")
    st.write("Add chargers, change rates and manage availability.")
    show_flash()

    all_tab, add_tab, edit_tab = st.tabs(["All chargers", "Add charger", "Update rate & status"])

    with all_tab:
        rows = []
        for c in db.get_all_chargers():
            rows.append({
                "Charger": c["charger_id"],
                "Type": c["charger_type"],
                "Power (kW)": c["power_kw"],
                "Rate (₹/kWh)": c["rate_per_kwh"],
                "Status": c["status"],
            })
        show_table(rows, "No chargers yet.")

    with add_tab:
        with st.form("add_charger_form"):
            new_id = st.text_input("Charger ID", value=db.next_charger_id())
            new_type = st.selectbox("Charger type", db.CHARGER_TYPES)
            new_power = st.number_input("Power (kW)", min_value=1.0, max_value=500.0,
                                        value=22.0, step=1.0)
            new_rate = st.number_input("Price per kWh (₹)", min_value=1.0, max_value=100.0,
                                       value=12.0, step=0.5)
            add_clicked = st.form_submit_button("Add charger")

        if add_clicked:
            ok, message = db.add_charger(user["user_id"], new_id, new_type, new_power, new_rate)
            if ok:
                set_flash(message)
                st.rerun()
            else:
                st.error(message)

    with edit_tab:
        charger_ids = [c["charger_id"] for c in db.get_all_chargers()]
        if not charger_ids:
            st.info("Add a charger first.")
        else:
            chosen_id = st.selectbox("Choose a charger", charger_ids, key="edit_charger_select")
            chosen = db.get_charger(chosen_id)
            has_active = db.charger_has_active_session(chosen_id)

            st.write(
                f"Current: **{chosen['charger_type']}** · {chosen['power_kw']:g} kW · "
                f"₹{chosen['rate_per_kwh']:.2f}/kWh · **{chosen['status']}**"
            )
            if has_active:
                st.warning("This charger has an active session, so its status is locked. "
                           "You can still change the rate for future sessions.")

            with st.form("rate_form_" + chosen_id):
                rate_value = st.number_input("New price per kWh (₹)", min_value=1.0,
                                             max_value=100.0, value=float(chosen["rate_per_kwh"]),
                                             step=0.5)
                rate_clicked = st.form_submit_button("Update rate")
            if rate_clicked:
                ok, message = db.update_charger_rate(user["user_id"], chosen_id, rate_value)
                if ok:
                    set_flash(message)
                    st.rerun()
                else:
                    st.error(message)

            with st.form("status_form_" + chosen_id):
                status_value = st.selectbox(
                    "New status", db.CHARGER_STATUSES,
                    index=db.CHARGER_STATUSES.index(chosen["status"])
                )
                status_clicked = st.form_submit_button("Update status")
            if status_clicked:
                ok, message = db.update_charger_status(user["user_id"], chosen_id, status_value)
                if ok:
                    set_flash(message)
                    st.rerun()
                else:
                    st.error(message)


def page_charging_sessions(user):
    operator_back_button("Charging Sessions")
    st.title("Charging Sessions")
    st.write("Monitor active and completed sessions.")
    show_flash()

    choice = st.selectbox("Show", ["All", "Active", "Completed", "Cancelled"])
    if choice == "All":
        sessions = db.get_all_sessions()
    else:
        sessions = db.get_all_sessions(status=choice)

    st.caption(f"{len(sessions)} sessions listed")
    show_table(sessions_table(sessions, include_driver=True), "No sessions match this filter.")

    st.subheader("Cancel an active session")
    st.caption("Use this if a session is stuck. The driver is not charged and the charger is released.")
    active_sessions = db.get_all_sessions(status="Active")

    if not active_sessions:
        st.info("There are no active sessions.")
    else:
        labels = {}
        for s in active_sessions:
            labels[s["session_id"]] = f"Session {s['session_id']} · {s['charger_id']} · {s['driver_name']}"

        chosen_session = st.selectbox(
            "Active session", list(labels.keys()), format_func=lambda sid: labels[sid]
        )
        if st.button("Cancel selected session", key="cancel_session_btn"):
            ok, message = db.cancel_session(user["user_id"], chosen_session)
            if ok:
                set_flash(message)
                st.rerun()
            else:
                st.error(message)


def page_billing_revenue(user):
    operator_back_button("Billing & Revenue")
    st.title("Billing & Revenue")
    st.write("Payment records and revenue (all amounts are simulated).")
    show_flash()

    stats = db.get_site_stats()
    m = st.columns(4)
    m[0].metric("Net charging revenue", money(stats["net_revenue"]))
    m[1].metric("Refunds issued", money(stats["total_refunds"]))
    m[2].metric("Demo top-ups added", money(stats["total_topups"]))
    m[3].metric("Completed bills", stats["completed_sessions"])

    records_tab, bills_tab, refund_tab = st.tabs(["Payment records", "Completed bills", "Refund a session"])

    with records_tab:
        show_table(
            transactions_table(db.get_all_transactions(), include_driver=True),
            "No payment records yet."
        )

    with bills_tab:
        show_table(
            sessions_table(db.get_all_sessions(status="Completed"), include_driver=True),
            "No completed bills yet."
        )

    with refund_tab:
        refundable = db.get_refundable_sessions()
        if not refundable:
            st.info("There are no sessions available to refund.")
        else:
            labels = {}
            for s in refundable:
                labels[s["session_id"]] = (
                    f"Session {s['session_id']} · {s['driver_name']} · "
                    f"{s['charger_id']} · {money(s['total_cost'])}"
                )
            chosen_session = st.selectbox(
                "Session to refund", list(labels.keys()), format_func=lambda sid: labels[sid]
            )
            if st.button("Refund full amount", key="refund_btn"):
                ok, message = db.refund_session(user["user_id"], chosen_session)
                if ok:
                    set_flash(message)
                    st.rerun()
                else:
                    st.error(message)
            st.caption("A refund returns the money to the driver's demo wallet. Each session can be refunded once.")


def page_reports(user):
    operator_back_button("Reports")
    st.title("Reports")
    st.write("Summaries calculated from the ChargeGrid database.")

    stats = db.get_site_stats()
    m = st.columns(4)
    m[0].metric("Registered drivers", stats["driver_count"])
    m[1].metric("Completed sessions", stats["completed_sessions"])
    m[2].metric("Energy delivered", f"{stats['total_energy']:.2f} kWh")
    m[3].metric("Net revenue", money(stats["net_revenue"]))

    st.subheader("Charger utilisation")
    utilisation = db.get_charger_utilisation()
    total_minutes = sum(u["minutes"] for u in utilisation)
    rows = []
    for u in utilisation:
        if total_minutes > 0:
            share = f"{u['minutes'] / total_minutes * 100:.1f}%"
        else:
            share = "0.0%"
        rows.append({
            "Charger": u["charger_id"],
            "Type": u["charger_type"],
            "Status now": u["status"],
            "Sessions": u["sessions"],
            "Energy (kWh)": round(u["energy_kwh"], 2),
            "Billed (₹)": round(u["billed"], 2),
            "Charging time": format_minutes(u["minutes"]),
            "Share of charging time": share,
        })
    show_table(rows, "No chargers yet.")
    st.caption("Billed amounts are before refunds. Charging time is measured from session start to stop.")

    left, right = st.columns(2)
    with left:
        st.subheader("By charger type")
        type_rows = []
        for t in db.get_type_summary():
            type_rows.append({
                "Type": t["charger_type"],
                "Sessions": t["sessions"],
                "Energy (kWh)": round(t["energy_kwh"], 2),
                "Billed (₹)": round(t["billed"], 2),
            })
        show_table(type_rows, "No data yet.")

    with right:
        st.subheader("Top drivers")
        driver_rows = []
        for d in db.get_top_drivers():
            driver_rows.append({
                "Driver": d["name"],
                "Sessions": d["sessions"],
                "Energy (kWh)": round(d["energy_kwh"], 2),
                "Billed (₹)": round(d["billed"], 2),
            })
        show_table(driver_rows, "No completed sessions yet.")

    st.subheader("Daily summary")
    daily_rows = []
    for d in db.get_daily_summary():
        daily_rows.append({
            "Date": d["day"],
            "Sessions": d["sessions"],
            "Energy (kWh)": round(d["energy_kwh"], 2),
            "Billed (₹)": round(d["billed"], 2),
        })
    show_table(daily_rows, "No completed sessions yet.")


# ===========================================================================
# PAGE ROUTER - the page shown depends on the role stored in the database
# ===========================================================================
if user is None:
    show_login_page()

elif user["role"] == "driver":
    page = st.session_state.page
    if page == "Charge Here":
        page_charge_here(user)
    elif page == "My Sessions":
        page_my_sessions(user)
    elif page == "My Wallet":
        page_my_wallet(user)
    elif page == "Bills & Transactions":
        page_bills(user)

elif user["role"] == "operator":
    page = st.session_state.page
    if page == "Dashboard":
        page_dashboard(user)
    elif page == "Charger Management":
        page_charger_management(user)
    elif page == "Charging Sessions":
        page_charging_sessions(user)
    elif page == "Billing & Revenue":
        page_billing_revenue(user)
    elif page == "Reports":
        page_reports(user)
