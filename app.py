import streamlit as st
import numpy as np
import pandas as pd

# -----------------------------
# PAGE SETUP
# -----------------------------
st.set_page_config(layout="wide")
st.title("🏥 Iddir Smart System (Mathematical + Simulation Engine)")

# -----------------------------
# INTRODUCTION (YOUR TEXT)
# -----------------------------
with st.expander("📘 About Iddir System"):
    st.write("""
Iddir is a community-based mutual aid system where members contribute to a shared fund,
which is used to support emergencies such as funerals or health crises.

This system models:
- Member contributions (strategic + social norms)
- Fund dynamics with interest
- Random emergency events (Bernoulli process)
- Aid disbursement policies
- Sustainability over time
""")

# -----------------------------
# SIDEBAR PARAMETERS
# -----------------------------
st.sidebar.header("⚙️ Model Parameters")

N = st.sidebar.slider("Number of Members (N)", 2, 50, 5)
T = st.sidebar.slider("Time Periods (T)", 5, 100, 20)

F0 = st.sidebar.number_input("Initial Fund F₀", value=1000.0)
r = st.sidebar.slider("Interest Rate r", 0.0, 0.2, 0.02)
p = st.sidebar.slider("Emergency Probability p", 0.0, 1.0, 0.3)
A_max = st.sidebar.number_input("Max Aid A_max", value=2000.0)

social_norm = st.sidebar.number_input("Social Norm Contribution", value=50.0)

# -----------------------------
# MEMBER CAPACITY INPUT
# -----------------------------
st.sidebar.subheader("👥 Member Capacities")

capacities = []
for i in range(N):
    cap = st.sidebar.number_input(f"Capacity Member {i+1}", value=100.0, key=i)
    capacities.append(cap)

capacities = np.array(capacities)

# -----------------------------
# CONTRIBUTION STRATEGY
# -----------------------------
def contribution_strategy(F_t, prev_c, capacities):
    contributions = []

    for i in range(len(capacities)):
        max_possible = capacities[i]

        # Strategic behavior (simple form)
        strategic = 0.05 * F_t  # depends on fund size

        c = min(max_possible, max(social_norm, strategic))
        c = max(c, 0)

        contributions.append(c)

    return np.array(contributions)

# -----------------------------
# FUND UPDATE + EMERGENCY
# -----------------------------
def fund_update(F_t, contributions):
    C_t = np.sum(contributions)

    F_temp = F_t + C_t + r * F_t

    # Bernoulli(p)
    E_t = np.random.rand() < p

    if E_t:
        A_t = min(F_temp, A_max)
        D_t = A_t
        F_next = F_temp - D_t
    else:
        A_t = 0
        D_t = 0
        F_next = F_temp

    return F_next, E_t, D_t, A_t, C_t

# -----------------------------
# SIMULATION ENGINE
# -----------------------------
def run_simulation():
    F = F0
    history = []

    prev_c = np.zeros(N)

    for t in range(T):
        c = contribution_strategy(F, prev_c, capacities)

        F, E, D, A, C = fund_update(F, c)

        history.append({
            "t": t,
            "Fund": F,
            "Total Contribution": C,
            "Emergency": int(E),
            "Aid Paid": D,
            "Aid Amount": A
        })

        prev_c = c

    return pd.DataFrame(history)

# -----------------------------
# RUN BUTTON
# -----------------------------
if st.button("🚀 Run Simulation"):

    df = run_simulation()

    st.subheader("📊 Simulation Results")
    st.dataframe(df)

    # -------------------------
    # VISUALIZATION
    # -------------------------
    col1, col2 = st.columns(2)

    with col1:
        st.line_chart(df.set_index("t")["Fund"])

    with col2:
        st.bar_chart(df.set_index("t")["Total Contribution"])

    # -------------------------
    # EMERGENCY EVENTS
    # -------------------------
    st.subheader("🚨 Emergency Events")
    st.bar_chart(df.set_index("t")["Emergency"])

    # -------------------------
    # SUSTAINABILITY METRICS
    # -------------------------
    st.subheader("📈 Sustainability Analysis")

    final_fund = df["Fund"].iloc[-1]
    total_aid = df["Aid Paid"].sum()
    total_contrib = df["Total Contribution"].sum()

    st.write(f"Final Fund: {final_fund:.2f}")
    st.write(f"Total Aid Paid: {total_aid:.2f}")
    st.write(f"Total Contributions: {total_contrib:.2f}")

    # -------------------------
    # RISK ANALYSIS
    # -------------------------
    st.subheader("⚠️ Risk & Stability")

    if final_fund <= 0:
        st.error("⚠️ System is NOT sustainable")
    elif final_fund < F0:
        st.warning("⚠️ Fund is declining")
    else:
        st.success("✅ System is sustainable")

# -----------------------------
# POLICY OPTIMIZATION (BASIC)
# -----------------------------
st.subheader("🧠 Policy Experimentation")

test_norm = st.slider("Test Social Norm", 0.0, 200.0, 50.0)

if st.button("Test Policy"):

    social_norm = test_norm
    df = run_simulation()

    st.line_chart(df.set_index("t")["Fund"])
    st.write("Final Fund:", df["Fund"].iloc[-1])
