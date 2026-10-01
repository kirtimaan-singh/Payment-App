import streamlit as st
import datetime
import random
import qrcode
from io import BytesIO

# --- Page Setup ---
st.set_page_config(
    page_title="Pocket Pay Simulator",
    page_icon="🔵",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# --- Pocket Pay Style CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap');

    html, body, [class*="st-emotion-cache"], .stApp {
        font-family: 'Google Sans', 'Plus Jakarta Sans', sans-serif;
        background-color: #f8fafd !important;
        color: #1f1f1f !important;
    }
    .block-container { max-width: 440px; padding: 1rem 1rem 3rem 1rem; }
    #MainMenu, header, footer { visibility: hidden; }

    .pocketpay-top-bar {
        display: flex; align-items: center; justify-content: space-between;
        background: #ffffff; border: 1px solid #e1e7ee; border-radius: 28px;
        padding: 8px 16px; margin-bottom: 1.2rem; box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    .pocketpay-logo { font-weight: 700; font-size: 17px; letter-spacing: -0.5px; color: #1f1f1f;
        display: flex; align-items: center; gap: 6px; }
    .g-blue { color: #4285F4; } .g-red { color: #EA4335; }
    .g-yellow { color: #FBBC04; } .g-green { color: #34A853; }

    .sec-title { font-size: 14px; font-weight: 700; color: #1f1f1f; margin-bottom: 10px; }

    .balance-card {
        background: linear-gradient(135deg, #1a73e8, #0d47a1); border-radius: 20px;
        padding: 18px 20px; color: white; margin-bottom: 1.2rem;
        box-shadow: 0 8px 20px -6px rgba(26, 115, 232, 0.45);
    }
    .balance-val { font-size: 28px; font-weight: 700; letter-spacing: -0.5px; }
    .vpa-tag { font-size: 12px; background: rgba(255,255,255,0.2); padding: 2px 8px;
        border-radius: 12px; display: inline-block; margin-top: 6px; }

    .reward-box {
        background: linear-gradient(135deg, #ea4335, #fbbc04); border-radius: 16px;
        padding: 14px 16px; color: white; margin-bottom: 0.6rem;
    }

    .contact-circle {
        width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center;
        justify-content: center; font-weight: 700; font-size: 16px; color: white;
        margin: 0 auto 6px auto;
    }

    .txn-item {
        background: #ffffff; border: 1px solid #edf2f7; border-radius: 14px;
        padding: 12px 14px; margin-bottom: 8px; display: flex;
        justify-content: space-between; align-items: center;
    }

    /* Payment success receipt */
    .receipt {
        background: #ffffff; border: 1px solid #e5eaf2; border-radius: 20px;
        padding: 22px 18px; text-align: center; margin: 8px 0 12px 0;
        box-shadow: 0 4px 14px -6px rgba(0,0,0,0.12);
    }
    .receipt-tick {
        width: 56px; height: 56px; border-radius: 50%; background: #1e8e3e; color: #fff;
        font-size: 30px; display: flex; align-items: center; justify-content: center;
        margin: 0 auto 10px auto;
    }
    .receipt-amt { font-size: 30px; font-weight: 700; color: #1f1f1f; }
    .receipt-row { display: flex; justify-content: space-between; font-size: 12px;
        color: #5f6368; padding: 4px 0; border-top: 1px dashed #e5eaf2; }
</style>
""", unsafe_allow_html=True)


# --- Global In-Memory Database (Demo Pre-populated) ---
if "users" not in st.session_state:
    st.session_state.users = {
        "9876543210": {
            "name": "Kirtimaan Singh", "mobile": "9876543210", "vpa": "kirtimaan@okaxis",
            "pin": "1234", "balance": 3500.0, "rewards_won": 45.0, "scratch_cards_available": 1,
            "bank_accounts": [
                {"bank": "Axis Bank", "acc_no": "••••4921", "ifsc": "UTIB0000123", "is_primary": True},
                {"bank": "HDFC Bank", "acc_no": "••••8812", "ifsc": "HDFC0000456", "is_primary": False},
            ],
            "transactions": [
                {"id": "UPI789123", "type": "DEBIT", "title": "Starbucks Coffee", "amount": 280.0,
                 "date": "Today, 10:15 AM", "status": "Success"},
                {"id": "UPI789124", "type": "CREDIT", "title": "Salary Credit", "amount": 5000.0,
                 "date": "Yesterday, 6:00 PM", "status": "Success"},
            ],
        },
        "9998887771": {
            "name": "Rohan Sharma", "mobile": "9998887771", "vpa": "rohan@okhdfcbank",
            "pin": "0000", "balance": 1200.0, "rewards_won": 0.0, "scratch_cards_available": 0,
            "bank_accounts": [{"bank": "HDFC Bank", "acc_no": "••••1144", "ifsc": "HDFC0000100", "is_primary": True}],
            "transactions": [],
        },
        "9998887772": {
            "name": "Priya Patel", "mobile": "9998887772", "vpa": "priya@okicici",
            "pin": "0000", "balance": 2100.0, "rewards_won": 0.0, "scratch_cards_available": 0,
            "bank_accounts": [{"bank": "ICICI Bank", "acc_no": "••••7733", "ifsc": "ICIC0000200", "is_primary": True}],
            "transactions": [],
        },
        "9998887773": {
            "name": "Blinkit Store", "mobile": "9998887773", "vpa": "blinkit@okaxis",
            "pin": "0000", "balance": 45000.0, "rewards_won": 0.0, "scratch_cards_available": 0,
            "bank_accounts": [{"bank": "Axis Bank", "acc_no": "••••9020", "ifsc": "UTIB0000999", "is_primary": True}],
            "transactions": [],
        },
    }

# --- Session defaults ---
DEFAULTS = {
    "logged_in_mobile": "9876543210",
    "recipient_input": "9998887771",
    "amount_input": 150.0,
    "pin_input": "",
    "pay_flash": None,
    "top_flash": None,
    "auth_flash": None,
    "last_receipt": None,
    "show_balloons": False,
    "collect_requests": [
        {
            "id": "REQ981001",
            "from_mobile": "9998887771",
            "to_mobile": "9876543210",
            "amount": 350.0,
            "note": "Lunch split 🍕",
            "status": "PENDING",
            "timestamp": "Today, 11:30 AM"
        }
    ],
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

MAX_TXN_AMOUNT = 25000.0
AVATAR_COLORS = ["#1a73e8", "#e91e63", "#00897b", "#f4511e", "#8e24aa", "#3949ab"]
AVAILABLE_BANKS = ["State Bank of India", "HDFC Bank", "ICICI Bank", "Axis Bank", "Punjab National Bank", "Kotak Mahindra Bank"]


# --- Helpers ---
def get_user():
    mobile = st.session_state.logged_in_mobile
    return st.session_state.users.get(mobile)


def new_txn_id(prefix="UPI"):
    return f"{prefix}{datetime.datetime.now().strftime('%y%m%d%H%M%S')}{random.randint(100, 999)}"


def show_flash(slot):
    flash = st.session_state.get(slot)
    if flash:
        kind, msg = flash
        getattr(st, kind)(msg)
        st.session_state[slot] = None


# --- Callbacks ---
def select_recipient(mobile):
    st.session_state.recipient_input = mobile
    st.session_state.last_receipt = None
    st.session_state.pay_flash = None


def set_amount(amount):
    st.session_state.amount_input = float(amount)


def process_payment():
    user = get_user()
    if not user:
        return
    users = st.session_state.users
    target = str(st.session_state.recipient_input).strip()
    amount = round(float(st.session_state.amount_input or 0), 2)
    pin = st.session_state.pin_input

    st.session_state.pin_input = ""

    error = None
    if not target:
        error = "Please enter a mobile number or pick a contact."
    elif not (target.isdigit() and len(target) == 10):
        error = "Enter a valid 10-digit mobile number."
    elif target == user["mobile"]:
        error = "You cannot send money to your own number."
    elif target not in users:
        error = "Mobile number not found on UPI network."
    elif amount <= 0:
        error = "Enter an amount greater than ₹0."
    elif amount > MAX_TXN_AMOUNT:
        error = f"Maximum per-transaction limit is ₹{MAX_TXN_AMOUNT:,.0f}."
    elif amount > user["balance"]:
        error = f"Insufficient balance. Available: ₹{user['balance']:,.2f}"
    elif not pin:
        error = "Please enter your UPI PIN."
    elif pin != user["pin"]:
        error = "Incorrect UPI PIN. Please try again."

    if error:
        st.session_state.pay_flash = ("error", error)
        return

    rec = users[target]
    now = datetime.datetime.now()
    now_str = now.strftime("%d %b, %I:%M %p")
    tx_id = new_txn_id()

    user["balance"] = round(user["balance"] - amount, 2)
    rec["balance"] = round(rec["balance"] + amount, 2)

    user["transactions"].insert(0, {
        "id": tx_id, "type": "DEBIT", "title": f"Paid to {rec['name']}",
        "amount": amount, "date": now_str, "status": "Success",
    })
    rec["transactions"].insert(0, {
        "id": tx_id, "type": "CREDIT", "title": f"Received from {user['name']}",
        "amount": amount, "date": now_str, "status": "Success",
    })

    earned_card = amount >= 100.0
    if earned_card:
        user["scratch_cards_available"] = user.get("scratch_cards_available", 0) + 1

    st.session_state.last_receipt = {
        "amount": amount, "name": rec["name"], "vpa": rec["vpa"],
        "id": tx_id, "date": now.strftime("%d %b %Y, %I:%M %p"),
        "earned_card": earned_card, "sender": user["mobile"],
    }
    st.session_state.amount_input = 150.0


def close_receipt():
    st.session_state.last_receipt = None


def scratch_card():
    user = get_user()
    if not user or user.get("scratch_cards_available", 0) <= 0:
        return
    win_amt = float(random.choice([5, 10, 25, 50, 100]))
    user["balance"] = round(user["balance"] + win_amt, 2)
    user["rewards_won"] = round(user.get("rewards_won", 0) + win_amt, 2)
    user["scratch_cards_available"] -= 1
    user["transactions"].insert(0, {
        "id": new_txn_id("RW"), "type": "CREDIT", "title": "Pocket Pay Cashback",
        "amount": win_amt, "date": datetime.datetime.now().strftime("%d %b, %I:%M %p"),
        "status": "Success",
    })
    st.session_state.show_balloons = True
    st.session_state.top_flash = ("success", f"🎉 You won ₹{win_amt:,.0f} cashback! Added to your balance.")


def switch_profile():
    new_mobile = st.session_state.switch_select
    st.session_state.logged_in_mobile = new_mobile
    others = [m for m in st.session_state.users if m != new_mobile]
    st.session_state.recipient_input = others[0] if others else ""
    st.session_state.pin_input = ""
    st.session_state.amount_input = 150.0
    st.session_state.last_receipt = None
    st.session_state.pay_flash = None
    st.session_state.top_flash = ("success", f"Switched to {st.session_state.users[new_mobile]['name']}")
    del st.session_state["switch_select"]


def logout_user():
    st.session_state.logged_in_mobile = None
    st.session_state.last_receipt = None
    st.session_state.pay_flash = None
    st.session_state.auth_flash = ("info", "You have been signed out.")


def handle_login():
    mobile = st.session_state.login_mobile.strip()
    pin = st.session_state.login_pin.strip()
    users = st.session_state.users

    if not (mobile.isdigit() and len(mobile) == 10):
        st.session_state.auth_flash = ("error", "Please enter a valid 10-digit mobile number.")
        return
    if mobile not in users:
        st.session_state.auth_flash = ("error", "Mobile number not registered. Please create an account.")
        return
    if users[mobile]["pin"] != pin:
        st.session_state.auth_flash = ("error", "Incorrect UPI PIN.")
        return

    st.session_state.logged_in_mobile = mobile
    st.session_state.top_flash = ("success", f"Welcome back, {users[mobile]['name']}!")


def handle_registration():
    name = st.session_state.reg_name.strip()
    mobile = st.session_state.reg_mobile.strip()
    pin = st.session_state.reg_pin.strip()
    bank = st.session_state.reg_bank
    acc_no = st.session_state.reg_acc.strip()
    users = st.session_state.users

    if not name:
        st.session_state.auth_flash = ("error", "Please enter your full name.")
        return
    if not (mobile.isdigit() and len(mobile) == 10):
        st.session_state.auth_flash = ("error", "Enter a valid 10-digit mobile number.")
        return
    if mobile in users:
        st.session_state.auth_flash = ("error", "Mobile number already registered. Please log in.")
        return
    if not (pin.isdigit() and len(pin) == 4):
        st.session_state.auth_flash = ("error", "Set a 4-digit numeric UPI PIN.")
        return
    if not (acc_no.isdigit() and len(acc_no) >= 4):
        st.session_state.auth_flash = ("error", "Enter a valid bank account number (min 4 digits).")
        return

    username = name.lower().replace(" ", "")
    vpa = f"{username}@okaxis"
    masked_acc = f"••••{acc_no[-4:]}"

    users[mobile] = {
        "name": name,
        "mobile": mobile,
        "vpa": vpa,
        "pin": pin,
        "balance": 2000.0,
        "rewards_won": 0.0,
        "scratch_cards_available": 1,
        "bank_accounts": [
            {"bank": bank, "acc_no": masked_acc, "ifsc": f"{bank[:4].upper()}0001234", "is_primary": True}
        ],
        "transactions": [
            {"id": new_txn_id("CR"), "type": "CREDIT", "title": "Welcome Bonus", "amount": 2000.0,
             "date": datetime.datetime.now().strftime("%d %b, %I:%M %p"), "status": "Success"}
        ],
    }
    st.session_state.logged_in_mobile = mobile
    st.session_state.show_balloons = True
    st.session_state.top_flash = ("success", "Account created! ₹2,000 welcome balance credited.")


def add_bank_account():
    user = get_user()
    bank = st.session_state.new_bank_name
    acc_no = st.session_state.new_bank_acc.strip()

    if not (acc_no.isdigit() and len(acc_no) >= 4):
        st.session_state.top_flash = ("error", "Enter a valid bank account number.")
        return

    masked_acc = f"••••{acc_no[-4:]}"
    user.setdefault("bank_accounts", []).append({
        "bank": bank, "acc_no": masked_acc, "ifsc": f"{bank[:4].upper()}0005678", "is_primary": False
    })
    st.session_state.top_flash = ("success", f"{bank} account linked successfully!")


def update_upi_pin():
    user = get_user()
    curr_pin = st.session_state.old_pin.strip()
    next_pin = st.session_state.new_pin.strip()

    if curr_pin != user["pin"]:
        st.session_state.top_flash = ("error", "Current PIN does not match.")
        return
    if not (next_pin.isdigit() and len(next_pin) == 4):
        st.session_state.top_flash = ("error", "New PIN must be 4 digits.")
        return
    if next_pin == curr_pin:
        st.session_state.top_flash = ("warning", "New PIN cannot be the same as current PIN.")
        return

    user["pin"] = next_pin
    st.session_state.top_flash = ("success", "UPI PIN updated successfully!")


def send_money_request(to_mobile, amount, note=""):
    user = get_user()
    users = st.session_state.users
    target = str(to_mobile).strip()

    if not (target.isdigit() and len(target) == 10):
        st.session_state.top_flash = ("error", "Enter a valid 10-digit mobile number.")
        return
    if target == user["mobile"]:
        st.session_state.top_flash = ("error", "You cannot request money from yourself.")
        return
    if target not in users:
        st.session_state.top_flash = ("error", "Recipient mobile number is not registered on Pocket Pay.")
        return
    if amount <= 0:
        st.session_state.top_flash = ("error", "Enter an amount greater than ₹0.")
        return

    req_id = new_txn_id(prefix="REQ")
    st.session_state.collect_requests.insert(0, {
        "id": req_id,
        "from_mobile": user["mobile"],
        "to_mobile": target,
        "amount": round(float(amount), 2),
        "note": note.strip() or "Payment Request",
        "status": "PENDING",
        "timestamp": datetime.datetime.now().strftime("%d %b, %I:%M %p")
    })
    st.session_state.top_flash = ("success", f"Request for ₹{amount:,.2f} sent to {users[target]['name']}!")


def approve_collect_request(req_id, pin):
    user = get_user()
    users = st.session_state.users

    req = next((r for r in st.session_state.collect_requests if r["id"] == req_id), None)
    if not req or req["status"] != "PENDING":
        st.session_state.top_flash = ("error", "Request not found or already processed.")
        return

    if pin != user["pin"]:
        st.session_state.top_flash = ("error", "Incorrect UPI PIN.")
        return
    if user["balance"] < req["amount"]:
        st.session_state.top_flash = ("error", f"Insufficient balance to pay ₹{req['amount']:,.2f}.")
        return

    amount = req["amount"]
    requester = users[req["from_mobile"]]
    now_str = datetime.datetime.now().strftime("%d %b, %I:%M %p")
    tx_id = new_txn_id()

    user["balance"] = round(user["balance"] - amount, 2)
    requester["balance"] = round(requester["balance"] + amount, 2)

    user["transactions"].insert(0, {
        "id": tx_id, "type": "DEBIT", "title": f"Paid Request to {requester['name']}",
        "amount": amount, "date": now_str, "status": "Success"
    })
    requester["transactions"].insert(0, {
        "id": tx_id, "type": "CREDIT", "title": f"Request paid by {user['name']}",
        "amount": amount, "date": now_str, "status": "Success"
    })

    req["status"] = "PAID"
    st.session_state.top_flash = ("success", f"Paid ₹{amount:,.2f} to {requester['name']} successfully!")


def decline_collect_request(req_id):
    req = next((r for r in st.session_state.collect_requests if r["id"] == req_id), None)
    if req:
        req["status"] = "DECLINED"
        st.session_state.top_flash = ("info", "Collect request declined.")


def process_custom_split_bill(allocations, note):
    user = get_user()
    now_str = datetime.datetime.now().strftime("%d %b, %I:%M %p")
    created_count = 0

    for mobile, share_amt in allocations.items():
        if mobile == user["mobile"]:
            continue
        amt = round(float(share_amt or 0), 2)
        if amt <= 0:
            continue
        req_id = new_txn_id(prefix="SPLIT")
        st.session_state.collect_requests.insert(0, {
            "id": req_id,
            "from_mobile": user["mobile"],
            "to_mobile": mobile,
            "amount": amt,
            "note": f"Split: {note.strip() or 'Custom Split'} (₹{amt:,.2f})",
            "status": "PENDING",
            "timestamp": now_str,
        })
        created_count += 1

    my_share = allocations.get(user["mobile"], 0.0)
    my_share_note = f" Your share: ₹{my_share:,.2f}." if my_share > 0 else ""
    st.session_state.top_flash = (
        "success",
        f"Sent {created_count} custom collect requests.{my_share_note}"
    )


# ================= VIEW ROUTING: AUTH VS MAIN APP =================
user = get_user()

if not user:
    # --- Authentication Screen ---
    st.markdown("""
        <div class="pocketpay-top-bar" style="justify-content: center;">
            <div class="pocketpay-logo">
                <span class="g-blue">P</span><span class="g-red">o</span><span class="g-yellow">c</span><span class="g-blue">k</span><span class="g-green">e</span><span class="g-red">t</span>&nbsp;Pay
            </div>
        </div>
    """, unsafe_allow_html=True)

    auth_tab1, auth_tab2 = st.tabs(["🔑 Sign In", "📝 Create Account"])
    show_flash("auth_flash")

    with auth_tab1:
        st.text_input("Mobile Number", key="login_mobile", max_chars=10, placeholder="e.g. 9876543210")
        st.text_input("4-Digit UPI PIN", key="login_pin", max_chars=4, type="password", placeholder="Demo PIN: 1234")
        st.button("Sign In to Pocket Pay", type="primary", use_container_width=True, on_click=handle_login)
        st.caption("Demo user: Mobile `9876543210` | PIN `1234`")

    with auth_tab2:
        st.text_input("Full Name", key="reg_name", placeholder="e.g. Amit Verma")
        st.text_input("10-Digit Mobile Number", key="reg_mobile", max_chars=10, placeholder="e.g. 9811223344")
        st.selectbox("Select Primary Bank", AVAILABLE_BANKS, key="reg_bank")
        st.text_input("Bank Account Number", key="reg_acc", placeholder="e.g. 1002349811")
        st.text_input("Set 4-Digit UPI PIN", key="reg_pin", max_chars=4, type="password", placeholder="4 digits")
        st.button("Register & Create UPI ID", type="primary", use_container_width=True, on_click=handle_registration)

else:
    # ================= MAIN UI =================
    # --- Top Navigation Bar ---
    st.markdown(f"""
        <div class="pocketpay-top-bar">
            <div class="pocketpay-logo">
                <span class="g-blue">P</span><span class="g-red">o</span><span class="g-yellow">c</span><span class="g-blue">k</span><span class="g-green">e</span><span class="g-red">t</span>&nbsp;Pay
            </div>
            <div style="font-size: 13px; font-weight: 600; color: #5f6368;">
                👤 {user['name'].split()[0]}
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- Account Balance Card ---
    st.markdown(f"""
        <div class="balance-card">
            <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.8px; opacity: 0.85;">Bank Account Balance</div>
            <div class="balance-val">₹{user['balance']:,.2f}</div>
            <div class="vpa-tag">UPI ID: {user['vpa']}</div>
        </div>
    """, unsafe_allow_html=True)

    show_flash("top_flash")
    if st.session_state.show_balloons:
        st.balloons()
        st.session_state.show_balloons = False

    # --- Scratch Card Banner ---
    cards = user.get("scratch_cards_available", 0)
    if cards > 0:
        st.markdown(f"""
            <div class="reward-box">
                <div style="font-weight: 700; font-size: 14px;">🎁 You have {cards} unscratched card{'s' if cards > 1 else ''}!</div>
                <div style="font-size: 11px; opacity: 0.9;">Claim your cashback reward now</div>
            </div>
        """, unsafe_allow_html=True)
        st.button("Scratch Card Now ✨", use_container_width=True, on_click=scratch_card)

    # --- Incoming Payment Requests Notification Card ---
    pending_requests = [
        r for r in st.session_state.collect_requests
        if r["to_mobile"] == user["mobile"] and r["status"] == "PENDING"
    ]
    if pending_requests:
        st.markdown('<div class="sec-title">🔔 Incoming Payment Requests</div>', unsafe_allow_html=True)
        for req in pending_requests:
            requester_name = st.session_state.users[req["from_mobile"]]["name"]
            with st.expander(f"⚠️ {requester_name} requested ₹{req['amount']:,.2f}", expanded=True):
                st.write(f"**Note:** {req['note']}")
                st.caption(f"Received: {req['timestamp']} • ID: {req['id']}")
                c_pin, c_pay, c_dec = st.columns([2, 1.2, 1.2])
                with c_pin:
                    pin_val = st.text_input("UPI PIN", type="password", max_chars=4, key=f"req_pin_{req['id']}")
                with c_pay:
                    st.write("")
                    st.button("Approve", key=f"app_{req['id']}", type="primary", use_container_width=True,
                              on_click=approve_collect_request, args=(req["id"], pin_val))
                with c_dec:
                    st.write("")
                    st.button("Decline", key=f"dec_{req['id']}", use_container_width=True,
                              on_click=decline_collect_request, args=(req["id"],))

    # --- People & Businesses ---
    st.markdown('<div class="sec-title">People & Businesses</div>', unsafe_allow_html=True)
    contacts = [u for m, u in st.session_state.users.items() if m != user["mobile"]]
    if contacts:
        contact_cols = st.columns(min(len(contacts), 4))
        for idx, c in enumerate(contacts[:4]):
            with contact_cols[idx]:
                st.markdown(f"""
                    <div class="contact-circle" style="background-color: {AVATAR_COLORS[idx % len(AVATAR_COLORS)]};">
                        {c['name'][0]}
                    </div>
                    <div style="font-size: 11px; font-weight: 600; text-align: center; margin-bottom: 4px;">{c['name'].split()[0]}</div>
                """, unsafe_allow_html=True)
                st.button("Pay", key=f"btn_{c['mobile']}", use_container_width=True,
                          on_click=select_recipient, args=(c["mobile"],))
    else:
        st.caption("No other users found on the network.")

    # --- Tabs ---
    tab_pay, tab_request, tab_split, tab_scan, tab_activity, tab_profile = st.tabs(
        ["💸 Send", "📩 Request", "👥 Split Bill", "📲 QR Code", "📜 History", "⚙️ Account"]
    )

    # 1. Send Money
    with tab_pay:
        st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
        receipt = st.session_state.last_receipt

        if receipt and receipt["sender"] == user["mobile"]:
            st.markdown(f"""
                <div class="receipt">
                    <div class="receipt-tick">✓</div>
                    <div style="font-size: 13px; color: #5f6368;">Paid to {receipt['name']}</div>
                    <div class="receipt-amt">₹{receipt['amount']:,.2f}</div>
                    <div style="font-size: 12px; color: #1e8e3e; font-weight: 600; margin-bottom: 12px;">Payment Successful</div>
                    <div class="receipt-row"><span>To</span><span>{receipt['vpa']}</span></div>
                    <div class="receipt-row"><span>Transaction ID</span><span>{receipt['id']}</span></div>
                    <div class="receipt-row"><span>Date</span><span>{receipt['date']}</span></div>
                </div>
            """, unsafe_allow_html=True)
            if receipt["earned_card"]:
                st.info("🎁 You earned a scratch card! Scratch it from the banner above.")
            st.button("Make Another Payment", type="primary", use_container_width=True, on_click=close_receipt)
        else:
            st.text_input("Enter Phone number or select contact above", key="recipient_input", max_chars=10)

            target = str(st.session_state.recipient_input).strip()
            recipient_obj = st.session_state.users.get(target)
            if recipient_obj and target != user["mobile"]:
                st.caption(f"Paying to: *{recipient_obj['name']}* ({recipient_obj['vpa']})")
            elif target == user["mobile"]:
                st.caption("⚠️ That's your own number.")
            elif len(target) == 10:
                st.caption("⚠️ Number not found on UPI network.")

            chip_cols = st.columns(4)
            for col, amt in zip(chip_cols, [100, 250, 500, 1000]):
                col.button(f"₹{amt:,}", key=f"chip_{amt}", use_container_width=True,
                           on_click=set_amount, args=(amt,))

            st.number_input("Amount (₹)", min_value=1.0, max_value=MAX_TXN_AMOUNT,
                            step=50.0, key="amount_input")

            st.text_input(f"Enter 4-Digit UPI PIN (Demo PIN: {user['pin']})",
                          max_chars=4, type="password", key="pin_input")

            st.button("Proceed to Pay", type="primary", use_container_width=True, on_click=process_payment)
            show_flash("pay_flash")

    # 2. Request Money
    with tab_request:
        st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
        st.markdown('<div class="sec-title">Create a Collect Request</div>', unsafe_allow_html=True)

        req_target = st.text_input("Payer's 10-Digit Mobile Number", key="req_mobile_input", max_chars=10)
        req_amount = st.number_input("Request Amount (₹)", min_value=1.0, max_value=MAX_TXN_AMOUNT, step=50.0, key="req_amount_input")
        req_note = st.text_input("Add a note (e.g., Dinner, Rent)", key="req_note_input", max_chars=40)

        if st.button("Send Payment Request", type="primary", use_container_width=True):
            send_money_request(req_target, req_amount, req_note)
            st.rerun()

        sent_requests = [r for r in st.session_state.collect_requests if r["from_mobile"] == user["mobile"]]
        if sent_requests:
            st.divider()
            st.markdown('<div class="sec-title">Sent Requests</div>', unsafe_allow_html=True)
            for sr in sent_requests[:5]:
                status_colors = {"PENDING": "orange", "PAID": "green", "DECLINED": "red"}
                color = status_colors.get(sr['status'], 'gray')
                to_name = st.session_state.users.get(sr['to_mobile'], {}).get('name', sr['to_mobile'])
                st.markdown(f"""
                    <div class="txn-item">
                        <div>
                            <div style="font-size: 13px; font-weight: 600;">To: {to_name}</div>
                            <div style="font-size: 11px; color: #5f6368;">{sr['note']} • {sr['timestamp']}</div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 14px; font-weight: 700;">₹{sr['amount']:,.2f}</div>
                            <span style="font-size: 11px; color: {color}; font-weight: 600;">{sr['status']}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    # 3. Split Bill Calculator
    with tab_split:
        st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
        st.markdown('<div class="sec-title">Split Bill with Friends</div>', unsafe_allow_html=True)

        split_total = st.number_input(
            "Total Bill Amount (₹)", min_value=1.0, max_value=MAX_TXN_AMOUNT, step=100.0, key="split_total_input"
        )
        split_note = st.text_input("What is this for?", placeholder="e.g. Dinner & Drinks", key="split_note_input")

        eligible_users = [m for m in st.session_state.users if m != user["mobile"]]
        selected_friends = st.multiselect(
            "Select friends to split with",
            options=eligible_users,
            format_func=lambda m: f"{st.session_state.users[m]['name']} (+91 {m})",
            key="split_contacts_select"
        )

        include_self = st.checkbox("Include myself in the split", value=True)
        participants = ([user["mobile"]] if include_self else []) + selected_friends

        if not participants:
            st.caption("Select at least one contact to configure the split.")
        else:
            split_mode = st.radio(
                "Split Method",
                ["Equally", "Unequally (₹)", "By Percentage (%)"],
                horizontal=True
            )

            allocations = {}

            if split_mode == "Equally":
                equal_share = round(split_total / len(participants), 2)
                for p in participants:
                    allocations[p] = equal_share
                st.info(f"Each person pays: **₹{equal_share:,.2f}** ({len(participants)} people)")

            elif split_mode == "Unequally (₹)":
                st.markdown("<div style='font-size: 12px; font-weight: 600; margin-top: 8px;'>ENTER RUPEE AMOUNT PER PERSON:</div>", unsafe_allow_html=True)
                allocated_sum = 0.0
                for p in participants:
                    name_label = f"You ({user['name'].split()[0]})" if p == user["mobile"] else st.session_state.users[p]["name"]
                    share = st.number_input(
                        f"{name_label}",
                        min_value=0.0,
                        max_value=float(split_total),
                        step=10.0,
                        key=f"unequal_{p}"
                    )
                    allocations[p] = share
                    allocated_sum += share

                remaining = round(split_total - allocated_sum, 2)
                if remaining == 0:
                    st.success("✅ Total amounts match exactly!")
                elif remaining > 0:
                    st.warning(f"₹{remaining:,.2f} remaining to allocate.")
                else:
                    st.error(f"Exceeded total by ₹{abs(remaining):,.2f}!")

            elif split_mode == "By Percentage (%)":
                st.markdown("<div style='font-size: 12px; font-weight: 600; margin-top: 8px;'>ENTER PERCENTAGE PER PERSON:</div>", unsafe_allow_html=True)
                pct_sum = 0.0
                for p in participants:
                    name_label = f"You ({user['name'].split()[0]})" if p == user["mobile"] else st.session_state.users[p]["name"]
                    pct = st.number_input(
                        f"{name_label} (%)",
                        min_value=0.0,
                        max_value=100.0,
                        step=5.0,
                        key=f"pct_{p}"
                    )
                    share_amt = round((pct / 100.0) * split_total, 2)
                    allocations[p] = share_amt
                    pct_sum += pct
                    st.caption(f"↳ Equals ₹{share_amt:,.2f}")

                remaining_pct = round(100.0 - pct_sum, 1)
                if remaining_pct == 0.0:
                    st.success("✅ Percentages equal 100%!")
                elif remaining_pct > 0:
                    st.warning(f"{remaining_pct}% remaining to assign.")
                else:
                    st.error(f"Total is {pct_sum}% (exceeds 100%)!")

            total_assigned = round(sum(allocations.values()), 2)
            can_submit = abs(total_assigned - round(split_total, 2)) < 0.05 and split_total > 0

            if st.button("Send Split Requests", type="primary", use_container_width=True, disabled=not can_submit):
                process_custom_split_bill(allocations, split_note)
                st.rerun()

    # 4. QR Code
    with tab_scan:
        st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
        st.caption("Show this QR to receive instant payments via any UPI app.")

        upi_string = f"upi://pay?pa={user['vpa']}&pn={user['name'].replace(' ', '%20')}&cu=INR"
        qr = qrcode.QRCode(version=1, box_size=8, border=2)
        qr.add_data(upi_string)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="#1a73e8", back_color="#ffffff")

        buf = BytesIO()
        qr_img.save(buf, format="PNG")
        st.image(buf.getvalue(), caption=f"Scanning: {user['vpa']}", use_container_width=True)

    # 5. Transaction History
    with tab_activity:
        st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
        st.markdown('<div class="sec-title">Recent Transactions</div>', unsafe_allow_html=True)

        if not user["transactions"]:
            st.info("No transaction history yet.")
        else:
            for t in user["transactions"]:
                is_cr = t["type"] == "CREDIT"
                color = "#137333" if is_cr else "#d93025"
                sign = "+" if is_cr else "-"
                icon = "🟢" if is_cr else "🔴"
                st.markdown(f"""
                    <div class="txn-item">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <div style="font-size: 16px;">{icon}</div>
                            <div>
                                <div style="font-size: 13px; font-weight: 600; color: #202124;">{t['title']}</div>
                                <div style="font-size: 11px; color: #5f6368;">{t['date']} • {t['id']}</div>
                            </div>
                        </div>
                        <div style="font-size: 14px; font-weight: 700; color: {color};">
                            {sign}₹{t['amount']:,.2f}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    # 6. Account, Bank Accounts & Settings
    with tab_profile:
        st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
        st.write(f"*Logged in as:* **{user['name']}**")
        st.write(f"*Mobile:* +91 {user['mobile']}")
        st.write(f"*UPI ID:* `{user['vpa']}`")
        st.write(f"*Total Cashback Won:* ₹{user.get('rewards_won', 0):,.2f}")

        st.divider()
        st.markdown('<div class="sec-title">Linked Bank Accounts</div>', unsafe_allow_html=True)
        bank_accounts = user.get("bank_accounts", [])
        if not bank_accounts:
            st.caption("No bank account linked.")
        else:
            for acc in bank_accounts:
                primary_badge = " *(Primary)*" if acc.get("is_primary") else ""
                st.write(f"🏦 **{acc['bank']}** ({acc['acc_no']}){primary_badge}")

        with st.expander("➕ Link New Bank Account"):
            st.selectbox("Bank", AVAILABLE_BANKS, key="new_bank_name")
            st.text_input("Account Number", key="new_bank_acc", placeholder="Enter Account Number")
            st.button("Add Bank Account", use_container_width=True, on_click=add_bank_account)

        with st.expander("🔐 Change UPI PIN"):
            st.text_input("Current 4-Digit PIN", type="password", max_chars=4, key="old_pin")
            st.text_input("New 4-Digit PIN", type="password", max_chars=4, key="new_pin")
            st.button("Update PIN", use_container_width=True, on_click=update_upi_pin)

        st.divider()
        st.caption("Switch Accounts to test both sender and receiver perspectives:")
        other_accounts = [m for m in st.session_state.users if m != user["mobile"]]
        if other_accounts:
            st.selectbox(
                "Switch to another test profile:", other_accounts, key="switch_select",
                format_func=lambda m: f"{st.session_state.users[m]['name']} (+91 {m})",
            )
            st.button("Switch Profile", use_container_width=True, on_click=switch_profile)

        st.button("Log Out", use_container_width=True, on_click=logout_user)
