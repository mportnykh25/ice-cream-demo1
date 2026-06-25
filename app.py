import streamlit as st
import requests
import pickle
import numpy as np
from datetime import datetime

st.set_page_config(page_title="Ice Cream Sales Predictor", page_icon="🍦", layout="centered")

# load model
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

# header
st.title("🍦 Ice Cream Sales Predictor")
st.caption("Enter your location and date details to predict today's sales.")
st.divider()

# inputs
city = st.text_input("Your city", "New York")

day = st.selectbox("Day of week", 
    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
day_num = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"].index(day)

is_holiday = st.toggle("Public holiday today?")

st.divider()

# predict button
if st.button("Predict Sales", type="primary"):
    
    # fetch temperature from weather API
    with st.spinner("Fetching weather..."):
        geo = requests.get(
            f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
        ).json()
        
        if not geo.get("results"):
            st.error("City not found. Please try another city.")
        else:
            lat = geo["results"][0]["latitude"]
            lon = geo["results"][0]["longitude"]
            
            weather = requests.get(
                f"https://api.open-meteo.com/v1/forecast"
                f"?latitude={lat}&longitude={lon}&current_weather=true"
            ).json()
            
            temperature = weather["current_weather"]["temperature"]
            
            # run model
            X = np.array([[temperature, day_num, int(is_holiday)]])
            prediction = model.predict(X)[0]
            prediction = max(0, prediction)
            
            # display results
            st.success("Prediction ready!")
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Temperature", f"{temperature}°C")
            col2.metric("Day", day)
            col3.metric("Holiday", "Yes" if is_holiday else "No")
            
            st.markdown("###")
            st.metric("Predicted Sales", f"{prediction:.0f} units")
            
            # simple interpretation
            if prediction > 400:
                st.info("🔥 High demand day — make sure you're fully stocked!")
            elif prediction > 200:
                st.info("📈 Moderate demand expected.")
            else:
                st.info("📉 Slow day expected — consider a promotion.")
