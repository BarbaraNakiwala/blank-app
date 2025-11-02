import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
 
st.set_page_config(page_title="NSSF Smart Contact Center Scheduler", layout="wide")
 
# ------------------------------------------------------
# TITLE
# ------------------------------------------------------
st.title("📞 NSSF Contact Center — Smart Monthly Schedule Generator")
st.write("Generate a fair, rule-based monthly schedule for agents with quotas and restrictions.")
 
# ------------------------------------------------------
# LOAD ROTA
# ------------------------------------------------------
file_path = r"C:\Users\bnakiwala\OneDrive - National Social Security Fund\everyday folder\CALL CENTER ROTA.csv"
 
try:
    agents_df = pd.read_csv(file_path)
    st.success("✅ Rota file loaded successfully!")
except Exception as e:
    st.error(f"❌ Failed to load rota file.\nError: {e}")
    st.stop()
 
agents_df.columns = agents_df.columns.str.strip().str.title()
 
st.subheader("📋 Current Rota Preview")
st.dataframe(agents_df.head())
 
 
# ------------------------------------------------------
# SUPERVISOR INPUT — MONTH
# ------------------------------------------------------
st.write("### 📅 Select Month")
month = st.text_input("Enter the Month (e.g., Nov-2025):",
                      value=datetime.now().strftime("%b-%Y"))
 
 
# ------------------------------------------------------
# SUPERVISOR INPUT — ROLE RESTRICTIONS
# ------------------------------------------------------
st.write("### 🚫 Role Restrictions")
role_list = agents_df["Channel"].unique().tolist()
 
restricted_roles = {}
for role in role_list:
    restricted_roles[role] = st.multiselect(
        f"Agents NOT allowed to work **{role}**:",
        options=agents_df["Name"].unique().tolist(),
        key=f"restrict_role_{role}"
    )
 
 
# ------------------------------------------------------
# SUPERVISOR INPUT — SHIFT RESTRICTIONS
# ------------------------------------------------------
st.write("### ⛔ Shift Restrictions")
shift_list = agents_df["Time"].unique().tolist()
 
restricted_shifts = {}
for shift in shift_list:
    restricted_shifts[shift] = st.multiselect(
        f"Agents NOT allowed on shift **{shift}**:",
        options=agents_df["Name"].unique().tolist(),
        key=f"restrict_shift_{shift}"
    )
 
 
# ------------------------------------------------------
# SUPERVISOR INPUT — MONTHLY ROLE QUOTAS
# ------------------------------------------------------
st.write("### 📦 Monthly Role Quotas (Supervisor Adjustable)")
 
default_monthly_quota = {
    "Calls": 9,
    "Calls/SMS": 4,
    "Emails": 4,
    "Social/SMS": 2,
    "WhatsApp": 5,
}
 
monthly_quota = {}
 
for role, default_val in default_monthly_quota.items():
    monthly_quota[role] = st.number_input(
        f"{role} monthly quota:",
        min_value=0,
        value=default_val,
        key=f"quota_{role}"
    )
 
 
# ------------------------------------------------------
# SUPERVISOR INPUT — SHIFT QUOTAS
# ------------------------------------------------------
st.write("### 🧩 Role–Shift Quotas (Supervisor Adjustable)")
 
default_role_shift_quota = {
    "Calls": {"8am to 5pm": 5, "10am to 7pm": 2, "12pm to 9pm": 1},
    "Calls/SMS": {"8am to 5pm": 2, "12pm to 9pm": 2},
    "Email": {"8am to 5pm": 3, "12pm to 9pm": 1},
    "Social/SMS": {"8am to 5pm": 1, "10am to 7pm": 1},
    "WhatsApp": {"8am to 5pm": 3, "10am to 7pm": 1, "12pm to 9pm": 1},
}
 
role_shift_quota = {}
 
for role, shifts in default_role_shift_quota.items():
    st.write(f"#### {role}")
    role_shift_quota[role] = {}
    for shift, default_val in shifts.items():
        role_shift_quota[role][shift] = st.number_input(
            f"{role} — {shift}",
            min_value=0,
            value=default_val,
            key=f"{role}_{shift}"
        )
 
 
# ------------------------------------------------------
# SMART SCHEDULER FUNCTION
# ------------------------------------------------------
def generate_schedule(df, role_shift_quota, restricted_roles, restricted_shifts):
    df = df.copy()
    np.random.seed()
 
    assignment = []
    available_agents = df["Name"].tolist()
    np.random.shuffle(available_agents)
 
    # Create (role, shift) slots based on supervisor quotas
    slots = []
    for role, shifts in role_shift_quota.items():
        for shift, count in shifts.items():
            for _ in range(count):
                slots.append((role, shift))
 
    np.random.shuffle(slots)
 
    if len(slots) > len(available_agents):
        st.error("❌ Not enough agents to fill all role–shift quotas!")
        return None
 
    final_assignments = []
 
    for role, shift in slots:
        for agent in available_agents:
            # Skip if agent is restricted from this role
            if agent in restricted_roles.get(role, []):
                continue
 
            # Skip if agent is restricted from this shift
            if agent in restricted_shifts.get(shift, []):
                continue
 
            # Assign agent to slot
            final_assignments.append((agent, role, shift))
            available_agents.remove(agent)
            break
 
    schedule_df = pd.DataFrame(final_assignments,
                               columns=["Name", "Assigned Role", "Assigned Shift"])
 
    schedule_df["Month"] = month
    return schedule_df
 
 
# ------------------------------------------------------
# GENERATE BUTTON
# ------------------------------------------------------
if st.button("🎲 Generate Schedule"):
    result = generate_schedule(
        agents_df,
        role_shift_quota,
        restricted_roles,
        restricted_shifts
    )
    if result is not None:
        st.success("✅ Schedule generated successfully!")
        st.dataframe(result)
 
        csv = result.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download Schedule CSV",
            data=csv,
            file_name=f"NSSF_Schedule_{month}.csv",
            mime="text/csv"
        )
 
# ------------------------------------------------------
# SHUFFLE BUTTON
# ------------------------------------------------------
if st.button("🔀 Shuffle Again"):
    result = generate_schedule(
        agents_df,
        role_shift_quota,
        restricted_roles,
        restricted_shifts
    )
    if result is not None:
        st.success("🔀 Schedule reshuffled!")
        st.dataframe(result)
 
        csv = result.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download Shuffled Schedule CSV",
            data=csv,
            file_name=f"NSSF_Schedule_Shuffled_{month}.csv",
            mime="text/csv"
        )
