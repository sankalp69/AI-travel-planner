import streamlit as st
import requests
import json
import datetime
from dateutil.parser import parse
import pandas as pd
import time
import os

# Set page configuration
st.set_page_config(
    page_title="AI Ultimate Travel Planner",
    page_icon="✈️",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stButton button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .plan-section {
        background-color: #f9f9f9;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    h1, h2, h3 {
        color: #2E86C1;
    }
    .section-divider {
        margin-top: 30px;
        margin-bottom: 30px;
        border-bottom: 1px solid #eaeaea;
    }
    .loader {
        display: flex;
        justify-content: center;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# API endpoint URL - use environment variable with fallback
API_ENDPOINT = os.environ.get("API_URL", "http://127.0.0.1:8000")

# Add a trailing slash to the endpoint if it doesn't exist
if not API_ENDPOINT.endswith('/'):
    API_ENDPOINT += '/'

# Create the full endpoint URL
API_ENDPOINT += "plan_trip/"

# Debug information
st.sidebar.markdown("### Debug Info")
st.sidebar.write(f"API Endpoint: {API_ENDPOINT}")

# Title and intro
st.title("✈️ AI Ultimate Travel Planner")
st.markdown("""
Welcome to your AI-powered travel companion! Enter your trip details below to get personalized flight suggestions, 
a detailed itinerary, restaurant & hotel recommendations, and weather forecast for your destination.
""")

# Create a form for user input
with st.form(key="trip_form"):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        source = st.text_input("Departure City", placeholder="e.g., New York")
        
    with col2:
        destination = st.text_input("Destination", placeholder="e.g., Paris")
    
    with col3:
        budget_level = st.selectbox(
            "Budget Level",
            options=[(1, "Budget-Friendly"), (2, "Mid-Range"), (3, "Luxury")],
            format_func=lambda x: x[1]
        )
    
    col4, col5 = st.columns(2)
    
    with col4:
        start_date = st.date_input("Start Date", min_value=datetime.date.today())
    
    with col5:
        # Calculate a default end date (start date + 7 days)
        default_end_date = start_date + datetime.timedelta(days=7) if start_date else datetime.date.today() + datetime.timedelta(days=7)
        end_date = st.date_input("End Date", value=default_end_date, min_value=start_date if start_date else datetime.date.today())
    
    submit_button = st.form_submit_button(label="Plan My Trip!")

# Create variable for displaying results
if 'show_results' not in st.session_state:
    st.session_state.show_results = False

# Function to process and display results
def display_results(response_data):
    # Flight Suggestions Section
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='plan-section'>", unsafe_allow_html=True)
    st.markdown("## ✈️ Flight Suggestions")
    st.markdown(response_data["flight_suggestions"])
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Itinerary Section
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='plan-section'>", unsafe_allow_html=True)
    st.markdown("## 🗓️ Trip Itinerary")
    st.markdown(response_data["itinerary"])
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Recommendations Section
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='plan-section'>", unsafe_allow_html=True)
    st.markdown("## 🍽️ Recommendations")
    
    # Try to extract JSON from the recommendations text
    try:
        # Look for JSON content in the markdown
        text = response_data["recommendations"]
        
        # Display the markdown content
        st.markdown(text)
        
        # Try to find and parse any JSON content
        import re
        json_matches = re.findall(r'```json\n(.*?)\n```', text, re.DOTALL)
        
        if json_matches:
            for json_str in json_matches:
                try:
                    data = json.loads(json_str)
                    
                    # Check if the data contains restaurants
                    if isinstance(data, dict) and "restaurants" in data:
                        st.subheader("Top Restaurants")
                        restaurants_df = pd.DataFrame(data["restaurants"])
                        st.dataframe(restaurants_df, use_container_width=True)
                    
                    # Check if the data contains hotels
                    if isinstance(data, dict) and "hotels" in data:
                        st.subheader("Top Hotels")
                        hotels_df = pd.DataFrame(data["hotels"])
                        st.dataframe(hotels_df, use_container_width=True)
                except:
                    pass
    except:
        # If JSON extraction fails, just display the markdown
        pass
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Weather Forecast Section
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='plan-section'>", unsafe_allow_html=True)
    st.markdown("## 🌤️ Weather Forecast")
    
    # Try to extract JSON from the weather forecast text
    try:
        # Look for JSON content in the markdown
        text = response_data["weather_forecast"]
        
        # Display the markdown content
        st.markdown(text)
        
        # Try to find and parse any JSON content
        import re
        json_matches = re.findall(r'```json\n(.*?)\n```', text, re.DOTALL)
        
        if json_matches:
            for json_str in json_matches:
                try:
                    data = json.loads(json_str)
                    
                    # Check if the data contains forecast
                    if isinstance(data, dict) and "forecast" in data:
                        st.subheader("7-Day Forecast")
                        forecast_df = pd.DataFrame(data["forecast"])
                        st.dataframe(forecast_df, use_container_width=True)
                except:
                    pass
    except:
        # If JSON extraction fails, just display the markdown
        pass
    
    st.markdown("</div>", unsafe_allow_html=True)

# Process form submission
if submit_button:
    if not source or not destination:
        st.error("Please provide both departure city and destination!")
    else:
        with st.spinner("🌍 Planning your dream trip... Please wait!"):
            # Prepare payload
            payload = {
                "source": source,
                "destination": destination,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "budget_level": budget_level[0]  # Extract the numeric value from the tuple
            }
            
            try:
                # Call the API
                response = requests.post(API_ENDPOINT, json=payload, timeout=180)
                
                if response.status_code == 200:
                    # Store the results in session state
                    st.session_state.response_data = response.json()
                    st.session_state.show_results = True
                    st.success("Your travel plan is ready! 🎉")
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"Error connecting to the API. Make sure your FastAPI server is running. Error: {e}")
                st.error(f"API URL being used: {API_ENDPOINT}")

# Display results if available
if st.session_state.show_results and hasattr(st.session_state, 'response_data'):
    display_results(st.session_state.response_data)

# Add a footer
st.markdown("---")
st.markdown("### How to use this app")
st.markdown("""
1. Enter your departure city and destination
2. Select your preferred budget level
3. Choose your travel dates
4. Click 'Plan My Trip!' and wait for the AI to generate your personalized travel plan
5. View the results in the tabs above
""")

st.markdown("---")
st.caption("Powered by AI Ultimate Travel Planner API & Google Gemini")