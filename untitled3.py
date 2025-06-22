import streamlit as st
from datetime import datetime, time
import pytz
import pandas as pd

# --- FOREX SESSIONS in UTC ---
sessions_utc = {
    "Sydney": (22, 0),
    "Tokyo": (0, 0),
    "London": (7, 0),
    "New York": (12, 0),
}

display_to_timezone = {
    "London": "Europe/London",
    "New York": "America/New_York",
    "Tokyo": "Asia/Tokyo",
    "Sydney": "Australia/Sydney",
    "India (IST)": "Asia/Kolkata",
    "UTC": "UTC"
}

timezones = list(display_to_timezone.keys())

# --- PAGE SETUP ---
st.set_page_config("Forex Time Converter", layout="centered")

# --- CUSTOM DARK THEME STYLING ---
st.markdown("""
    <style>
    html, body, [data-testid="stApp"] {
        background-color: #121212;
        color: #E0E0E0;
        font-size: 14px;
    }
    h1, h2, h3, h4 {
        font-size: 24px;
        margin-bottom: 10px;
    }
    table, th, td {
        color: #f0f0f0 !important;
        font-size: 14px;
    }
    input, select, textarea {
        background-color: #1f1f1f !important;
        color: #e0e0e0 !important;
        font-size: 14px;
    }
    </style>
""", unsafe_allow_html=True)

# --- APP HEADER ---
st.markdown("## Forex Sessions & Time Zone Converter By OP")

# --- DATE INPUT ---
selected_date = st.date_input("Select Date", value=datetime.now().date())

# --- FOREX SESSION TABLE ---
st.markdown("#### 📈 Forex Opening Times (IST & Local)")

table_data = []
for session, (h, m) in sessions_utc.items():
    dt_utc = datetime.combine(selected_date, time(hour=h, minute=m))
    utc = pytz.utc.localize(dt_utc)

    ist_time = utc.astimezone(pytz.timezone("Asia/Kolkata")).strftime("%I:%M %p")
    local_zone = pytz.timezone(display_to_timezone[session])
    local_time = utc.astimezone(local_zone).strftime("%I:%M %p")

    table_data.append({
        "Session": session,
        "IST Time": ist_time,
        "Local Time": local_time
    })

df = pd.DataFrame(table_data)
st.table(df.set_index("Session"))

# --- TIME CONVERTER ---
st.markdown("#### 🔁 Time Converter")

col1, col2 = st.columns(2)
with col1:
    hour = st.number_input("Hour (1–12)", min_value=1, max_value=12, value=12)
    minute = st.number_input("Minute (0–59)", min_value=0, max_value=59, value=0)
with col2:
    ampm = st.selectbox("AM / PM", ["AM", "PM"])
    from_zone_display = st.selectbox("From Timezone", timezones)

# --- TIME CONVERSION ---
if st.button("Convert"):
    if ampm == "PM" and hour != 12:
        hour += 12
    elif ampm == "AM" and hour == 12:
        hour = 0

    base_dt = datetime.combine(selected_date, time(hour, minute))
    from_zone = pytz.timezone(display_to_timezone[from_zone_display])
    aware_dt = from_zone.localize(base_dt)

    st.markdown("**🧭 Converted Time in All Zones:**")
    for name, zone in display_to_timezone.items():
        target_zone = pytz.timezone(zone)
        converted = aware_dt.astimezone(target_zone)
        st.write(f"{name}: {converted.strftime('%I:%M %p')}")
