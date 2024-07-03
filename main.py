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

def get_city_from_ip(ip_address: str) -> str:
    geolocation_api_key = os.getenv("IPGEOLOCATION_API_KEY")
    if not geolocation_api_key:
        raise HTTPException(status_code=500, detail="Geolocation API key not found")
    
    try:
        geolocation_url = f"https://api.ipgeolocation.io/ipgeo?apiKey={geolocation_api_key}&ip={ip_address}"
        geolocation_response = requests.get(geolocation_url)
        geolocation_response.raise_for_status()
        geolocation_data = geolocation_response.json()
        
        if 'city' not in geolocation_data:
            raise ValueError("Unexpected geolocation data format")
        
        city = geolocation_data["city"]
        return city
    except requests.RequestException as e:
        print(f"Error fetching geolocation data: {e}")
        raise HTTPException(status_code=500, detail="Error fetching geolocation data")
    except ValueError as e:
        print(f"Error parsing geolocation data: {e}")
        raise HTTPException(status_code=500, detail="Error parsing geolocation data")

@app.get("/api/hello", response_model=HelloResponse)
async def hello(request: Request, visitor_name: str = Query(...)):
    client_ip = request.client.host
    
    try:
        city = get_city_from_ip(client_ip)
    except HTTPException as e:
        city = "unknown"
    
    # Get weather data for the city
    weather_api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    if not weather_api_key:
        raise HTTPException(status_code=500, detail="Weather API key not found")
    
    try:
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api_key}&units=metric"
        weather_response = requests.get(weather_url)
        weather_response.raise_for_status()
        weather_data = weather_response.json()
        
        if 'main' not in weather_data or 'temp' not in weather_data['main']:
            raise ValueError("Unexpected weather data format")
        
        temperature = weather_data["main"]["temp"]
    except requests.RequestException as e:
        print(f"Error fetching weather data: {e}")
        temperature = "unknown"
    except ValueError as e:
        print(f"Error parsing weather data: {e}")
        temperature = "unknown"
    
    greeting = f"Hello, {visitor_name}! The temperature is {temperature} degrees Celsius in {city}"
    
    return HelloResponse(client_ip=client_ip, location=city, greeting=greeting)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
