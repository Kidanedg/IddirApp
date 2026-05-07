############################################################
# IDDIR APP SYSTEMS (FULL DEMO VERSION)
# Login + Registration + Loans + Assets + Simulation
############################################################

import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime

# =========================================================
# PAGE CONFIG (MUST COME FIRST)
# =========================================================
st.set_page_config(page_title="Iddir App Systems", layout="wide")

# =========================================================
# WELCOME & PROJECT CONTEXT
# =========================================================
st.title("Iddir App Systems")

st.markdown("""
### Welcome to Our Demo

Welcome to the **Iddir App Systems**, a digital platform developed to transform 
traditional Ethiopian mutual aid associations into a modern, data-driven system.

This application demonstrates how **mathematical modeling, stochastic processes, 
and community finance principles** can be translated into a practical, interactive tool 
for managing Iddir operations — including contributions, loans, shared assets, and 
emergency support mechanisms.

---

### Project Objective

- Digitize Iddir operations  
- Improve transparency and sustainability  
- Support decision-making through simulation and analytics  
- Enable future expansion to mobile and enterprise systems  

---

### Acknowledgment

This project is developed as part of a **Technology Transfer Initiative**.  
We gratefully acknowledge the support of the **Technology Transfer Office, Aksum University**,  
for funding and facilitating this project.
""")

# =========================================================
# INITIALIZE SESSION STORAGE (IN-MEMORY DATABASE)
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
# AUTH SYSTEM (LOGIN + REGISTER)
# =========================================================
def auth_system():
    st.subheader("🔐 Authentication")

    tab1, tab2 = st.tabs(["Login", "Register"])

    # LOGIN
    with tab1:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login"):
            if username in st.session_state.users:
                if st.session_state.users[username]["password"] == password:
                    st.session_state.current_user = username
                    st.success("Login successful")
                    st.rerun()
                else:
                    st.error("Incorrect password")
            else:
                st.error("User not found")

    # REGISTER
    with tab2:
        new_user = st.text_input("New Username", key="reg_user")
        new_pass = st.text_input("Password", type="password", key="reg_pass")
        confirm_pass = st.text_input("Confirm Password")

        if st.button("Register"):
            if not new_user or not new_pass:
                st.warning("Fill all fields")
            elif new_user in st.session_state.users:
                st.error("Username already exists")
            elif new_pass != confirm_pass:
                st.error("Passwords do not match")
            else:
                st.session_state.users[new_user] = {
                    "password": new_pass,
                    "role": "member"
                }
                st.success("Registration successful")

# =========================================================
# LOGOUT
# =========================================================
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
        if name:
            st.session_state.members[name] = {
                "capacity": capacity,
                "balance": 0
            }
            st.success("Member added")

def show_members():
    if st.session_state.members:
        st.subheader("📋 Members")
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
            st.error("Insufficient fund")

    if st.session_state.loans:
        st.subheader("📋 Loans")
        st.dataframe(pd.DataFrame(st.session_state.loans))

# =========================================================
# LOAN REPAYMENT
# =========================================================
def repay_loan():
    st.subheader("💰 Repay Loan")

    if not st.session_state.loans:
        st.info("No loans")
        return

    idx = st.selectbox("Select Loan", range(len(st.session_state.loans)))

    if st.button("Repay"):
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
    auth_system()

else:
    st.sidebar.write(f"User: {st.session_state.current_user}")

    if st.sidebar.button("Logout"):
        logout()

    menu = st.sidebar.radio("Navigation", [
        "Dashboard", "Members", "Loans", "Simulation"
    ])

    if menu == "Dashboard":
        st.subheader("📊 Overview")
        col1, col2 = st.columns(2)
        col1.metric("Fund", f"{st.session_state.fund:.2f}")
        col2.metric("Asset", f"{st.session_state.asset:.2f}")

    elif menu == "Members":
        add_member()
        show_members()

    elif menu == "Loans":
        loan_system()
        repay_loan()

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
st.markdown("Iddir App Systems | Technology Transfer Project @ Aksum University ")
