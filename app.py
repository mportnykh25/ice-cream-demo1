import streamlit as st
import requests
import pickle
import numpy as np
from datetime import date, timedelta

st.set_page_config(page_title="Ice Cream Sales Predictor", page_icon="🍦", layout="centered")

# load model
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

st.title("🍦 Ice Cream Sales Predictor")
st.caption("Enter your location and a date to predict ice cream sales.")
st.divider()

# inputs
col1, col2 = st.columns(2)
city = col1.text_input("City", "Springfield")
state = col2.text_input("State", "Illinois")

selected_date = st.date_input(
    "Date",
    min_value=date.today(),
    max_value=date.today() + timedelta(days=16),
    value=date.today()
)

is_holiday = st.toggle("Is this a special event or holiday?")
st.divider()

if st.button("Predict Sales", type="primary"):
    with st.spinner("Fetching weather forecast..."):

        # geocode city
        geo = requests.get(
            f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=5"
        ).json()

        if not geo.get("results"):
            st.error("City not found. Please try another city.")
        else:
            # filter by state
            results = geo["results"]
            if state:
                filtered = [r for r in results if state.lower() in r.get("admin1", "").lower()]
                results = filtered if filtered else results

            result = results[0]
            lat = result["latitude"]
            lon = result["longitude"]

            st.caption(f"📍 Found: {result['name']}, {result.get('admin1', '')}, {result.get('country', '')}")

            # fetch forecast for selected date
            weather = requests.get(
                f"https://api.open-meteo.com/v1/forecast"
                f"?latitude={lat}&longitude={lon}"
                f"&daily=temperature_2m_max"
                f"&timezone=auto"
                f"&start_date={selected_date}"
                f"&end_date={selected_date}"
            ).json()

            temperature = weather["daily"]["temperature_2m_max"][0]
            day_name = selected_date.strftime("%A")
            day_num = selected_date.weekday()

            # run model
            X = np.array([[temperature, day_num, int(is_holiday)]])
            prediction = max(0, model.predict(X)[0])

            # display results
            st.success("Prediction ready!")
            st.markdown("###")

            col1, col2, col3 = st.columns(3)
            col1.metric("Day", day_name)
            col2.metric("Temperature", f"{temperature}°C")
            col3.metric("Holiday / Event", "Yes" if is_holiday else "No")

            st.markdown("###")
            st.metric("Predicted Sales", f"{prediction:.0f} units")

            if prediction > 400:
                st.info("🔥 High demand — make sure you're fully stocked!")
            elif prediction > 200:
                st.info("📈 Moderate demand expected.")
            else:
                st.info("📉 Slow day — consider running a promotion.")
