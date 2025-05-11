# AI Ultimate Travel Planner

Link - https://renderdeploy-i0n9.onrender.com/

A containerized travel planning application with a FastAPI backend and Streamlit frontend. This application uses Google's Gemini AI model to generate personalized travel plans including flight suggestions, itineraries, restaurant and hotel recommendations, and weather forecasts.

## Project Structure

```
.
├── .env                  # Environment variables (create from .env.template)
├── docker-compose.yml    # Docker Compose configuration
├── backend/              # FastAPI backend service
│   ├── Dockerfile        # Docker configuration for backend
│   ├── main.py           # FastAPI application
│   └── requirements.txt  # Python dependencies for backend
└── frontend/             # Streamlit frontend service
    ├── Dockerfile        # Docker configuration for frontend
    ├── app.py            # Streamlit application
    └── requirements.txt  # Python dependencies for frontend
```

## Prerequisites

1. Docker and Docker Compose installed on your system
2. Google API key for Gemini AI

## Setup Instructions

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd ai-ultimate-travel-planner
   ```

2. Create a `.env` file from the template:
   ```bash
   cp .env.template .env
   ```

3. Edit the `.env` file and add your Google API key:
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   ```

4. Build and start the Docker containers:
   ```bash
   docker-compose up --build
   ```

5. Access the application:
   - Frontend (Streamlit): http://localhost:8501
   - Backend API docs: http://localhost:8000/docs

## Usage

1. Enter your departure city and destination
2. Select your preferred budget level
3. Choose your travel dates
4. Click "Plan My Trip!" and wait for the AI to generate your personalized travel plan
5. View the results in the various sections

## Troubleshooting

If you encounter connection issues between the frontend and backend:

1. Make sure both containers are running:
   ```bash
   docker-compose ps
   ```

2. Check the logs for any errors:
   ```bash
   docker-compose logs
   ```

3. Ensure your Google API key is valid and has access to the Gemini AI API

## License

[MIT License](LICENSE)
