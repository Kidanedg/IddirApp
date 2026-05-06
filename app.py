############################################################
# IDDIR APP SYSTEMS (ADVANCED DEMO VERSION)
# Includes: Login + Loans + Assets + Simulation
############################################################

import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime

# =========================================================
# INITIALIZE DATABASE (SESSION)
# =========================================================
if "users" not in st.session_state:
    st.session_state.users = {
        "admin": {"password": "admin123", "role": "admin"}
    }

if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "members" not in st.session_state:
    st.session_state.members = {}

if "fund" not in st.session_state:
    st.session_state.fund = 1000.0

if "asset" not in st.session_state:
    st.session_state.asset = 100000.0

if "loans" not in st.session_state:
    st.session_state.loans = []

# =========================================================
# LOGIN SYSTEM
# =========================================================
def login():
    st.title("🔐 Iddir Login System")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in st.session_state.users:
            if st.session_state.users[username]["password"] == password:
                st.session_state.current_user = username
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Wrong password")
        else:
            st.error("User not found")

def logout():
    st.session_state.current_user = None
    st.rerun()

# =========================================================
# MEMBER MANAGEMENT
# =========================================================
def add_member():
    st.subheader("👥 Add Member")

    name = st.text_input("Member Name")
    capacity = st.number_input("Contribution Capacity", value=100.0)

    if st.button("Add Member"):
        st.session_state.members[name] = {
            "capacity": capacity,
            "balance": 0
        }
        st.success("Member added")

def show_members():
    if st.session_state.members:
        st.dataframe(pd.DataFrame(st.session_state.members).T)

# =========================================================
# LOAN SYSTEM
# =========================================================
def loan_system():
    st.subheader("💳 Loan System")

    members = list(st.session_state.members.keys())

    if not members:
        st.warning("Add members first")
        return

    borrower = st.selectbox("Select Member", members)
    amount = st.number_input("Loan Amount", value=100.0)
    interest = st.slider("Interest Rate", 0.0, 0.5, 0.1)

    if st.button("Give Loan"):
        if amount <= st.session_state.fund:
            loan = {
                "member": borrower,
                "amount": amount,
                "interest": interest,
                "total_due": amount * (1 + interest),
                "status": "active",
                "time": datetime.now()
            }
            st.session_state.loans.append(loan)
            st.session_state.fund -= amount

            st.success("Loan issued")
        else:
            st.error("Not enough fund")

    # Show loans
    if st.session_state.loans:
        st.subheader("📋 Active Loans")
        st.dataframe(pd.DataFrame(st.session_state.loans))

# =========================================================
# LOAN REPAYMENT
# =========================================================
def repay_loan():
    st.subheader("💰 Loan Repayment")

    if not st.session_state.loans:
        st.info("No loans available")
        return

    loan_ids = list(range(len(st.session_state.loans)))
    idx = st.selectbox("Select Loan", loan_ids)

    if st.button("Repay Loan"):
        loan = st.session_state.loans[idx]

        if loan["status"] == "active":
            st.session_state.fund += loan["total_due"]
            loan["status"] = "repaid"
            st.success("Loan repaid")
        else:
            st.warning("Already repaid")

# =========================================================
# SIMULATION MODEL
# =========================================================
def run_simulation(F0, S0, T, r, p, A_max):
    F = F0
    S = S0

    history = []

    for t in range(T):

        C_t = sum([m["capacity"] for m in st.session_state.members.values()])
        I_t = 0.05 * S

        F_temp = F + C_t + r * F + I_t

        E = np.random.rand() < p

        if E:
            A = min(F_temp, A_max)
            F = F_temp - A
        else:
            A = 0
            F = F_temp

        S += 0.1 * I_t

        history.append({
            "t": t,
            "Fund": F,
            "Asset": S,
            "Aid": A
        })

    return pd.DataFrame(history)

# =========================================================
# MAIN APP
# =========================================================
if st.session_state.current_user is None:
    login()
else:
    st.title("🇪🇹 Iddir App Systems")

    st.sidebar.write(f"Logged in as: {st.session_state.current_user}")
    if st.sidebar.button("Logout"):
        logout()

    menu = st.sidebar.radio("Menu", [
        "Dashboard",
        "Members",
        "Loans",
        "Simulation"
    ])

    # ---------------- DASHBOARD ----------------
    if menu == "Dashboard":
        st.subheader("📊 Overview")

        col1, col2 = st.columns(2)
        col1.metric("Fund", f"{st.session_state.fund:.2f}")
        col2.metric("Asset", f"{st.session_state.asset:.2f}")

    # ---------------- MEMBERS ----------------
    elif menu == "Members":
        add_member()
        show_members()

    # ---------------- LOANS ----------------
    elif menu == "Loans":
        loan_system()
        repay_loan()

    # ---------------- SIMULATION ----------------
    elif menu == "Simulation":
        st.subheader("📈 Simulation")

        T = st.slider("Periods", 5, 50, 20)
        r = st.slider("Interest Rate", 0.0, 0.2, 0.02)
        p = st.slider("Emergency Probability", 0.0, 1.0, 0.3)
        A_max = st.number_input("Max Aid", value=2000.0)

        if st.button("Run Simulation"):
            df = run_simulation(
                st.session_state.fund,
                st.session_state.asset,
                T, r, p, A_max
            )

            st.line_chart(df.set_index("t")[["Fund", "Asset"]])
            st.dataframe(df)

# =========================================================
# FOOTER
# =========================================================
st.markdown("---")
st.markdown("Iddir App Systems | Advanced Demo Version 🇪🇹")
