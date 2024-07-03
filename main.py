from fastapi import FastAPI, Query, HTTPException
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
    geolocation_api_key = os.getenv("IPGEOLOCATION_API_KEY", "696940ac2594400c94cb3bffb9f37b8e")
    if not geolocation_api_key:
        raise HTTPException(status_code=500, detail="Geolocation API key not found")
    
    try:
        geolocation_url = f"https://api.ipgeolocation.io/ipgeo?apiKey={geolocation_api_key}&ip={ip_address}"
        print(f"Requesting geolocation for IP: {ip_address}")  # Debug print
        geolocation_response = requests.get(geolocation_url)
        geolocation_response.raise_for_status()
        geolocation_data = geolocation_response.json()
        
        print(f"Geolocation API response: {geolocation_data}")  # Debug print
        
        if 'city' not in geolocation_data or not geolocation_data['city']:
            print(f"City not found in geolocation data for IP {ip_address}")
            return "unknown"
        
        city = geolocation_data["city"]
        return city
    except requests.RequestException as e:
        print(f"Error fetching geolocation data: {e}")
        return "unknown"
    except ValueError as e:
        print(f"Error parsing geolocation data: {e}")
        return "unknown"

@app.get("/api/hello", response_model=HelloResponse)
async def hello(visitor_name: str = Query(...), client_ip: str = Query(...)):
    print(f"Received request for IP: {client_ip}")  # Debug print
    
    try:
        city = get_city_from_ip(client_ip)
    except HTTPException as e:
        city = "unknown"
    
    # Get weather data for the city
    weather_api_key = os.getenv("OPENWEATHERMAP_API_KEY", "a64222d0621682143c070b0824387864")
    if not weather_api_key:
        raise HTTPException(status_code=500, detail="Weather API key not found")
    
    try:
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api_key}&units=metric"
        print(f"Requesting weather for city: {city}")  # Debug print
        weather_response = requests.get(weather_url)
        weather_response.raise_for_status()
        weather_data = weather_response.json()
        
        print(f"Weather API response: {weather_data}")  # Debug print
        
        if 'main' not in weather_data or 'temp' not in weather_data['main']:
            print(f"Unexpected weather data format for city {city}")
            temperature = "unknown"
        else:
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