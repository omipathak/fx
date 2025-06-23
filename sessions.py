import streamlit as st
from datetime import datetime, time
import pytz
import pandas as pd

# --- Forex Sessions in UTC ---
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

# --- Page Setup ---
st.set_page_config("Forex Time Converter", layout="centered")

# --- Dark Theme Styling ---
st.markdown("""
    <style>
    html, body, [data-testid="stApp"] {
        background-color: #121212;
        color: #E0E0E0;
        font-size: 14px;
    }
    h1, h2, h3, h4 {
        font-size: 18px;
        margin-bottom: 10px;
    }
    input, select, textarea {
        background-color: #1f1f1f !important;
        color: #e0e0e0 !important;
        font-size: 14px;
    }
    th, td {
        color: #f0f0f0 !important;
        font-size: 13px;
    }
    div.stButton > button {
        width: 100% !important;
    }
    div[data-baseweb="select"] input {
        caret-color: transparent !important;
    }
    div[data-baseweb="select"] input:focus {
        border: none !important;
        box-shadow: none !important;
    }
    input[type="text"][data-testid="stDateInput"] {
        pointer-events: none;
        caret-color: transparent;
        color: #e0e0e0;
    }
    .convert-label {
        background-color: #1f1f1f;
        padding: 8px 16px;
        border-radius: 8px;
        margin-top: 20px;
        font-weight: bold;
        font-size: 14px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Title ---
st.markdown("## Forex Sessions & Timezone Converter")

# --- Date Picker ---
selected_date = st.date_input("Select Date", value=datetime.now().date())
formatted_date = selected_date.strftime("%d %B %Y – %A")
st.markdown(f"📅 **Selected Date:** {formatted_date}")

# --- Split Layout for Session & Time Converter ---
left_col, right_col = st.columns(2)

# --- LEFT: Forex Session Table ---
with left_col:
    st.markdown("#### 📈 Forex Session Times")
    table_data = []

    for session, (h, m) in sessions_utc.items():
        dt_utc = datetime.combine(selected_date, time(hour=h, minute=m))
        utc = pytz.utc.localize(dt_utc)

        ist_time = utc.astimezone(pytz.timezone("Asia/Kolkata")).strftime("%I:%M %p")
        local_time = utc.astimezone(pytz.timezone(display_to_timezone[session])).strftime("%I:%M %p")

        table_data.append({
            "Session": session,
            "IST Time": ist_time,
            "Local Time": local_time
        })

    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

# --- RIGHT: Time Converter ---
converted_times = {}

with right_col:
    st.markdown("#### 🔁 Time Converter")

    col1, col2 = st.columns(2)
    with col1:
        hour_input = st.text_input("Hour (1–12)", value="12")
        minute_input = st.text_input("Minute (0–59)", value="00")
    with col2:
        ampm = st.selectbox("AM / PM", ["AM", "PM"], index=0)
        from_zone_display = st.selectbox("From Timezone", timezones, index=0)

    convert_col = st.columns([1, 2, 1])[1]
    with convert_col:
        convert_clicked = st.button("🔁 Convert", use_container_width=True)

    if convert_clicked:
        try:
            hour = int(hour_input)
            minute = int(minute_input)
            if not (1 <= hour <= 12):
                st.error("Hour must be between 1 and 12.")
            elif not (0 <= minute <= 59):
                st.error("Minute must be between 0 and 59.")
            else:
                if ampm == "PM" and hour != 12:
                    hour += 12
                elif ampm == "AM" and hour == 12:
                    hour = 0

                input_dt = datetime.combine(selected_date, time(hour, minute))
                from_zone = pytz.timezone(display_to_timezone[from_zone_display])
                aware_dt = from_zone.localize(input_dt)

                for name, zone in display_to_timezone.items():
                    converted = aware_dt.astimezone(pytz.timezone(zone))
                    converted_times[name] = converted.strftime('%I:%M %p')
        except ValueError:
            st.error("Please enter valid numeric values for hour and minute.")

# --- Output label across full width ---
if converted_times:
    st.markdown('<div class="convert-label">🧭 Converted Times:</div>', unsafe_allow_html=True)

    keys = list(converted_times.keys())
    half = len(keys) // 2

    left_out, right_out = st.columns(2)
    with left_out:
        for name in keys[:half]:
            st.write(f"{name}: {converted_times[name]}")

    with right_out:
        for name in keys[half:]:
            st.write(f"{name}: {converted_times[name]}")
