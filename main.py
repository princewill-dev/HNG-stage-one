from fastapi import FastAPI, Request, Query, HTTPException
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

class HelloResponse(BaseModel):
    client_ip: str
    location: str
    greeting: str

@app.get("/api/hello", response_model=HelloResponse)
async def hello(request: Request, visitor_name: str = Query(...)):
    client_ip = request.client.host
    
    # Get location data
    try:
        location_response = requests.get(f"https://ipapi.co/{client_ip}/json/")
        location_response.raise_for_status()
        location_data = location_response.json()
        city = location_data.get("city", "Unknown")
    except requests.RequestException as e:
        print(f"Error fetching location data: {e}")
        city = "Unknown"
    
    # Get weather data
    weather_api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    if not weather_api_key:
        raise HTTPException(status_code=500, detail="Weather API key not found")
    
    try:
        weather_response = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api_key}&units=metric")
        weather_response.raise_for_status()
        weather_data = weather_response.json()
        print(f"Weather API response: {weather_data}")  # Debug print
        
        if 'main' not in weather_data or 'temp' not in weather_data['main']:
            raise ValueError("Unexpected weather data format")
        
        temperature = weather_data["main"]["temp"]
    except (requests.RequestException, ValueError) as e:
        print(f"Error fetching weather data: {e}")
        temperature = "unknown"
    
    greeting = f"Hello, {visitor_name}! The temperature is {temperature} degrees Celsius in {city}"
    
    return HelloResponse(client_ip=client_ip, location=city, greeting=greeting)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)