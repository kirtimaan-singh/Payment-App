import streamlit as st
import datetime
import random
import qrcode
from io import BytesIO

# --- Page Setup ---
st.set_page_config(
    page_title="GPay Simulator",
    page_icon="🔵",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# --- Google Pay Style CSS ---
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

    .gpay-top-bar {
        display: flex; align-items: center; justify-content: space-between;
        background: #ffffff; border: 1px solid #e1e7ee; border-radius: 28px;
        padding: 8px 16px; margin-bottom: 1.2rem; box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    .gpay-logo { font-weight: 700; font-size: 17px; letter-spacing: -0.5px; color: #1f1f1f;
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
            "transactions": [],
        },
        "9998887772": {
            "name": "Priya Patel", "mobile": "9998887772", "vpa": "priya@okicici",
            "pin": "0000", "balance": 2100.0, "rewards_won": 0.0, "scratch_cards_available": 0,
            "transactions": [],
        },
        "9998887773": {
            "name": "Blinkit Store", "mobile": "9998887773", "vpa": "blinkit@okaxis",
            "pin": "0000", "balance": 45000.0, "rewards_won": 0.0, "scratch_cards_available": 0,
            "transactions": [],
        },
    }

# --- Session defaults (all widget values live in session_state so they survive reruns) ---
DEFAULTS = {
    "logged_in_mobile": "9876543210",
    "recipient_input": "9998887771",
    "amount_input": 150.0,
    "pin_input": "",
    "pay_flash": None,      # (kind, message) shown in the Send Money tab
    "top_flash": None,      # (kind, message) shown at the top of the page
    "last_receipt": None,   # details of the most recent successful payment
    "show_balloons": False,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

MAX_TXN_AMOUNT = 25000.0
AVATAR_COLORS = ["#1a73e8", "#e91e63", "#00897b", "#f4511e", "#8e24aa", "#3949ab"]


# --- Helpers ---
def get_user():
    return st.session_state.users[st.session_state.logged_in_mobile]


def new_txn_id(prefix="UPI"):
    # Seconds + random suffix so two payments in the same second never collide
    return f"{prefix}{datetime.datetime.now().strftime('%y%m%d%H%M%S')}{random.randint(100, 999)}"


def show_flash(slot):
    flash = st.session_state.get(slot)
    if flash:
        kind, msg = flash
        getattr(st, kind)(msg)
        st.session_state[slot] = None  # show once


# --- Callbacks (run BEFORE the script reruns, so state & messages are never lost) ---
def select_recipient(mobile):
    st.session_state.recipient_input = mobile
    st.session_state.last_receipt = None
    st.session_state.pay_flash = None


def set_amount(amount):
    st.session_state.amount_input = float(amount)


def process_payment():
    user = get_user()
    users = st.session_state.users
    target = str(st.session_state.recipient_input).strip()
    amount = round(float(st.session_state.amount_input or 0), 2)
    pin = st.session_state.pin_input

    # PIN is always cleared after an attempt, like a real UPI app
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

    # Debit sender & credit recipient (rounded to avoid float drift)
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
    if user.get("scratch_cards_available", 0) <= 0:
        return
    win_amt = float(random.choice([5, 10, 25, 50, 100]))
    user["balance"] = round(user["balance"] + win_amt, 2)
    user["rewards_won"] = round(user.get("rewards_won", 0) + win_amt, 2)
    user["scratch_cards_available"] -= 1
    user["transactions"].insert(0, {
        "id": new_txn_id("RW"), "type": "CREDIT", "title": "Google Pay Cashback",
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
    # Options change after switching, so reset the selectbox
    del st.session_state["switch_select"]


# ================= UI =================
user = get_user()

# --- Top Navigation Bar ---
st.markdown(f"""
    <div class="gpay-top-bar">
        <div class="gpay-logo">
            <span class="g-blue">G</span><span class="g-red">o</span><span class="g-yellow">o</span><span class="g-blue">g</span><span class="g-green">l</span><span class="g-red">e</span>&nbsp;Pay
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

# --- People & Businesses (everyone except the logged-in user) ---
st.markdown('<div class="sec-title">People & Businesses</div>', unsafe_allow_html=True)
contacts = [u for m, u in st.session_state.users.items() if m != user["mobile"]]
contact_cols = st.columns(len(contacts))
for idx, c in enumerate(contacts):
    with contact_cols[idx]:
        st.markdown(f"""
            <div class="contact-circle" style="background-color: {AVATAR_COLORS[idx % len(AVATAR_COLORS)]};">
                {c['name'][0]}
            </div>
            <div style="font-size: 11px; font-weight: 600; text-align: center; margin-bottom: 4px;">{c['name'].split()[0]}</div>
        """, unsafe_allow_html=True)
        st.button("Pay", key=f"btn_{c['mobile']}", use_container_width=True,
                  on_click=select_recipient, args=(c["mobile"],))

# --- Tabs ---
tab_pay, tab_scan, tab_activity, tab_profile = st.tabs(["💸 Send Money", "📲 QR Code", "📜 History", "⚙️ Account"])

# 1. Send Money
with tab_pay:
    st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
    receipt = st.session_state.last_receipt

    if receipt and receipt["sender"] == user["mobile"]:
        # --- Success receipt screen ---
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
        # --- Payment form ---
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

# 2. My QR Code
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

# 3. Transaction History
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

# 4. Account & Switch User
with tab_profile:
    st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
    st.write(f"*Logged in as:* {user['name']}")
    st.write(f"*Mobile:* +91 {user['mobile']}")
    st.write(f"*Total Cashback Won:* ₹{user.get('rewards_won', 0):,.2f}")

    st.divider()
    st.caption("Switch Accounts to test both sender and receiver perspectives:")
    other_accounts = [m for m in st.session_state.users if m != user["mobile"]]
    st.selectbox(
        "Switch to another test profile:", other_accounts, key="switch_select",
        format_func=lambda m: f"{st.session_state.users[m]['name']} (+91 {m})",
    )
    st.button("Switch Profile", use_container_width=True, on_click=switch_profile)
