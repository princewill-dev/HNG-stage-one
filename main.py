from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import requests

app = FastAPI()

@app.get("/api/hello")
async def hello(request: Request, visitor_name: str = "Guest"):
    # Get client's IP address
    client_ip = get_client_ip(request)

    # Fetch location from IP address
    location_data = get_location(client_ip)

    # Fetch weather data
    temperature = get_temperature(location_data['state'])

    response_data = {
        "client_ip": client_ip,
        "location": location_data['state'],
        "greeting": f"Hello, {visitor_name}!, the temperature is {temperature} degrees Celsius in {location_data['state']}"
    }
    
    return JSONResponse(content=response_data)

def get_client_ip(request: Request):
    x_forwarded_for = request.headers.get('x-forwarded-for')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.client.host
    return ip

def get_location(ip):
    ipgeolocation_api_key = 'YOUR_IPGEOLOCATION_API_KEY'
    response = requests.get(f'https://api.ipgeolocation.io/ipgeo?apiKey={ipgeolocation_api_key}&ip={ip}')
    data = response.json()
    return {
        'state': data.get('state_prov', 'Unknown'),
        'country': data.get('country_name', 'Unknown')
    }

def get_temperature(state):
    openweather_api_key = 'YOUR_OPENWEATHER_API_KEY'
    response = requests.get(f'http://api.openweathermap.org/data/2.5/weather?q={state}&appid={openweather_api_key}&units=metric')
    data = response.json()
    
    if response.status_code != 200 or 'main' not in data:
        raise HTTPException(status_code=404, detail="Could not fetch temperature data")
    
    return data['main']['temp']

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
