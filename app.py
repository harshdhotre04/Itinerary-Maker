import streamlit as st
import google.generativeai as genai
import json
import re  # For extracting JSON
from datetime import datetime, timedelta

# Set your API key
API_KEY = "AIzaSyBIDCqTiMPg4WvL5k1nXZ1Ee3MeVaLjJN8"
genai.configure(api_key=API_KEY)

# Initialize the Gemini model
model = genai.GenerativeModel("gemini-1.5-pro")

# Streamlit UI
st.title("Travel Itinerary Generator")

city = st.text_input("Enter the city you're visiting:")
start_date = st.date_input("Select the start date for your trip:", value=datetime.today())

# Limit the end date selection
max_end_date = start_date + timedelta(days=30)
end_date = st.date_input("Select the end date for your trip:", 
                         value=start_date + timedelta(days=1),  
                         min_value=start_date, 
                         max_value=max_end_date)

# Calculate trip duration
days = (end_date - start_date).days

# User preferences
preferences = []
if st.checkbox("Art"):
    preferences.append("art")
if st.checkbox("Museums"):
    preferences.append("museums")
if st.checkbox("Outdoor Activities"):
    preferences.append("outdoor activities")
if st.checkbox("Indoor Activities"):
    preferences.append("indoor activities")
if st.checkbox("Good for Kids"):
    preferences.append("kid-friendly places")
if st.checkbox("Good for Young People"):
    preferences.append("places popular among young people")

# Generate itinerary button
if st.button("Generate Itinerary"):
    preference_text = ", ".join(preferences) if preferences else "a general travel experience"
    
    # Ensure the model returns JSON
    prompt = f"""
    You are a travel expert. Generate an itinerary for {city} for {days} days. Each day starts at 10:00 AM and ends at 8:00 PM, with 30-minute breaks between activities. 
    The itinerary should focus on {preference_text}. Return ONLY JSON. Do not include any explanations or extra text.

    Example:
    ```json
    {{
        "days": [
            {{
                "day": 1, 
                "activities": [
                    {{
                        "title": "Activity 1",
                        "description": "Description of Activity 1",
                        "link": "https://example.com/activity1",
                        "start_time": "10:00 AM",
                        "end_time": "12:00 PM",
                        "location": "https://maps.google.com/?q=location1"
                    }}
                ]
            }}
        ]
    }}
    ```
    """

    try:
        response = model.generate_content(prompt)

        # Extract JSON using regex (ensures only valid JSON is taken)
        match = re.search(r"\{.*\}", response.text, re.DOTALL)
        if match:
            itinerary_text = match.group(0)  # Get the JSON part
            itinerary_json = json.loads(itinerary_text)  # Convert text to JSON

            # Display itinerary
            for day in itinerary_json["days"]:
                st.header(f"Day {day['day']}")
                for activity in day["activities"]:
                    st.subheader(activity["title"])
                    st.write(f"**Description:** {activity['description']}")
                    st.write(f"**Location:** {activity['location']}")
                    st.write(f"**Time:** {activity['start_time']} - {activity['end_time']}")
                    st.write(f"[More Info]({activity['link']})")
                    st.write("\n")
        else:
            st.error("Error: AI did not return valid JSON. Please try again.")

    except json.JSONDecodeError:
        st.error("Error: AI response was not valid JSON. Try again.")
    except Exception as e:
        st.error(f"Error generating itinerary: {e}")
