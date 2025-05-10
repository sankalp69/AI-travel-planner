from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
import os
from dotenv import load_dotenv
import datetime
import logging

# --- Configuration ---

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from .env file
load_dotenv()

# Fetch the API key from environment variables
api_key = os.getenv("GOOGLE_API_KEY")

# Flag to track if API key is configured successfully
api_configured = False

# Configure the generative AI client on startup
if not api_key:
    logging.error("Error: GOOGLE_API_KEY not found in environment variables. Please create a `.env` file with your key.")
else:
    try:
        genai.configure(api_key=api_key)
        api_configured = True
        logging.info("Google Generative AI configured successfully.")
    except Exception as e:
        logging.error(f"Error configuring Google Generative AI: {e}")

# --- FastAPI App Instance ---
app = FastAPI(
    title="AI Ultimate Travel Planner API",
    description="API to generate trip plans including flights, itinerary, recommendations, and weather forecasts using Google Gemini."
)

# --- Pydantic Model for Request Body ---
class TripRequest(BaseModel):
    source: str
    destination: str
    start_date: datetime.date
    end_date: datetime.date
    budget_level: int # 1 for Budget-Friendly, 2 for Mid-Range, 3 for Luxury

# --- Helper Functions (Adapted for FastAPI) ---

def get_budget_description(budget_level: int) -> str:
    """Maps budget level integer to a descriptive string."""
    if budget_level == 1:
        return "Budget-Friendly"
    elif budget_level == 2:
        return "Mid-Range"
    elif budget_level == 3:
        return "Luxury"
    else:
        return "Any Budget" # Default or unexpected case

async def generate_flight_suggestions(source: str, destination: str, start_date: datetime.date, end_date: datetime.date, budget_level_desc: str, model_name: str = "gemini-1.5-flash") -> str:
    """
    Generates AI-based flight suggestions.
    """
    if not api_configured:
        return "API not configured. Cannot generate flight suggestions."

    try:
        prompt = f"""
        As a travel planning AI, suggest potential flight options for a trip from {source} to {destination}.
        The desired departure date is {start_date.strftime('%Y-%m-%d')} and the return date is {end_date.strftime('%Y-%m-%d')}.
        Please provide suggestions that align with a **{budget_level_desc} budget**.

        Suggest a few possible airlines, potential layover cities (if applicable), and a general idea of what one might expect regarding flight duration or typical costs for this route and budget.
        Emphasize that these are *suggestions based on general knowledge* and that users should perform a real-time flight search for accurate prices and availability.

        Present the response clearly using Markdown.
        """

        logging.info(f"Generating {budget_level_desc} flight suggestions from {source} to {destination} using {model_name}...")
        model = genai.GenerativeModel(model_name=model_name)
        generation_config = genai.types.GenerationConfig(
            temperature=0.6,
            max_output_tokens=700
        )
        response = await model.generate_content_async( # Use async version
            contents=[prompt],
            generation_config=generation_config
        )

        if response.parts:
            logging.info("Flight suggestions generated successfully.")
            return response.text
        else:
            logging.warning("Received an empty response or content was blocked.")
            return f"Could not generate flight suggestions. The response was empty or blocked. (Feedback: {response.prompt_feedback})"

    except Exception as e:
        logging.error(f"An error occurred during flight suggestion generation: {e}")
        return f"An error occurred during flight suggestion generation: {e}"


async def generate_travel_itinerary(destination: str, start_date: datetime.date, end_date: datetime.date, budget_level_desc: str, model_name: str = "gemini-1.5-flash") -> str:
    """
    Generates a travel itinerary using the Gemini model, considering budget.
    """
    if not api_configured:
        return "API not configured. Cannot generate itinerary."

    try:
        duration = (end_date - start_date).days + 1
        prompt = f"""Create a detailed travel itinerary for a trip to {destination}.
        The trip starts on {start_date.strftime('%Y-%m-%d')} and ends on {end_date.strftime('%Y-%m-%d')}, lasting for {duration} days.
        Please plan the trip with a **{budget_level_desc} budget** in mind.

        Provide a day-by-day plan including:
        - Suggested activities for morning, afternoon, and evening (suitable for a {budget_level_desc} budget).
        - Recommendations for places to visit (landmarks, museums, parks, etc.) - mention cost implications if relevant to the budget.
        - Optional: Suggestions for local food or restaurants to try that fit a {budget_level_desc} budget.
        - Optional: Basic tips for getting around (e.g., public transport, walking) that are budget-conscious.

        Format the output clearly, perhaps using Markdown with headings for each day.
        Be creative and provide practical suggestions for a memorable trip.
        """

        logging.info(f"Generating {budget_level_desc} itinerary for {destination} from {start_date} to {end_date} using {model_name}...")
        model = genai.GenerativeModel(model_name=model_name)
        generation_config = genai.types.GenerationConfig(
            temperature=0.7,
            max_output_tokens=2048
        )
        response = await model.generate_content_async( # Use async version
            contents=[prompt],
            generation_config=generation_config
        )

        if response.parts:
            logging.info("Itinerary generated successfully.")
            return response.text
        else:
            logging.warning("Received an empty response or content was blocked.")
            return f"Could not generate itinerary. The response was empty or blocked. (Feedback: {response.prompt_feedback})"

    except Exception as e:
        logging.error(f"An error occurred during itinerary generation: {e}")
        return f"An error occurred during itinerary generation: {e}"

async def generate_recommendations(location: str, budget_level_desc: str, model_name: str = "gemini-1.5-flash") -> str:
     """
     Generates restaurant and hotel recommendations using the Gemini model, considering budget.
     """
     if not api_configured:
         return "API not configured. Cannot generate recommendations."

     try:
         prompt = f"""
         You are an expert Restaurant & Hotel Planner.
         Your job is to provide Restaurant & Hotel recommendations for {location}.
         Please provide recommendations specifically for a **{budget_level_desc} budget**.

         - For Restaurants: Provide Top 5 restaurants that fit a {budget_level_desc} budget, with address and a general idea of average cost or cuisine type. Include a rating if available or inferable.
         - For Hotels: Provide Top 5 hotels that fit a {budget_level_desc} budget, with address and a general idea of average cost per night or star rating. Include a rating if available or inferable.

         Return the response using Markdown for clear formatting.
         """

         logging.info(f"Generating {budget_level_desc} recommendations for {location} using {model_name}...")
         model = genai.GenerativeModel(model_name=model_name)
         generation_config = genai.types.GenerationConfig(
             temperature=0.7,
             max_output_tokens=2048
         )
         response = await model.generate_content_async( # Use async version
             contents=[prompt],
             generation_config=generation_config
         )

         if response.parts:
             logging.info("Recommendations generated successfully.")
             return response.text
         else:
             logging.warning("Received an empty response or content was blocked.")
             return f"Could not generate recommendations. The response was empty or blocked. (Feedback: {response.prompt_feedback})"

     except Exception as e:
         logging.error(f"An error occurred during recommendation generation: {e}")
         return f"An error occurred during recommendation generation: {e}"

async def get_weather_forecast(location: str, model_name: str = "gemini-1.5-flash") -> str:
     """
     Gets a weather forecast and clothing suggestions using the Gemini model based on a prompt.
     """
     if not api_configured:
         return "API not configured. Cannot get weather forecast or clothing suggestions."

     try:
         prompt = f"""
         You are an expert weather forecaster and travel advisor. Your job is to provide a detailed weather forecast and suggest appropriate clothing to pack for a trip to {location}.
         Provide the forecast for the next 7 days, starting from today's date.
         Include details such as:
         - Daily temperature range (High/Low)
         - Precipitation (chance of rain/snow)
         - Humidity
         - Wind conditions
         - Air Quality (if available or inferable)
         - Cloud Cover

         Based on this 7-day forecast, provide a clear and concise suggestion for the type of clothing and gear someone should pack for their trip to {location} during this period. Consider layering if temperatures vary.

         Present the response clearly using Markdown, with a section for the daily forecast and a separate section for clothing suggestions.
         """

         logging.info(f"Getting weather forecast and clothing suggestions for {location} using {model_name}...")
         model = genai.GenerativeModel(model_name=model_name)
         generation_config = genai.types.GenerationConfig(
             temperature=0.4,
             max_output_tokens=1500
         )
         response = await model.generate_content_async( # Use async version
             contents=[prompt],
             generation_config=generation_config
         )

         if response.parts:
             logging.info("Weather forecast and clothing suggestions generated successfully.")
             return response.text
         else:
             logging.warning("Received an empty response or content was blocked.")
             return f"Could not get weather forecast and clothing suggestions. The response was empty or blocked. (Feedback: {response.prompt_feedback})"

     except Exception as e:
         logging.error(f"An error occurred during weather forecasting and clothing suggestions: {e}")
         return f"An error occurred during weather forecasting and clothing suggestions: {e}"

# --- API Endpoint ---

@app.post("/plan_trip/")
async def plan_trip(request: TripRequest):
    """
    Generates a complete trip plan including flight suggestions, itinerary,
    recommendations, and weather forecast based on user input.
    """
    if not api_configured:
         raise HTTPException(status_code=503, detail="Google Generative AI API is not configured.")

    budget_level_desc = get_budget_description(request.budget_level)

    # Generate results sequentially
    flight_suggestions = await generate_flight_suggestions(
        request.source,
        request.destination,
        request.start_date,
        request.end_date,
        budget_level_desc
    )

    itinerary = await generate_travel_itinerary(
        request.destination,
        request.start_date,
        request.end_date,
        budget_level_desc
    )

    recommendations = await generate_recommendations(
        request.destination,
        budget_level_desc
    )

    weather_forecast = await get_weather_forecast(
        request.destination
    )

    # Return results in the specified order
    return {
        "flight_suggestions": flight_suggestions,
        "itinerary": itinerary,
        "recommendations": recommendations,
        "weather_forecast": weather_forecast
    }

# --- Root endpoint for health checks ---
@app.get("/")
def read_root():
    return {"status": "healthy", "message": "AI Travel Planner API is running"}