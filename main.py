from fastapi import FastAPI, Request
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
    temperature = get_temperature(location_data['city'])

    response_data = {
        "client_ip": client_ip,
        "location": location_data['city'],
        "greeting": f"Hello, {visitor_name}!, the temperature is {temperature} degrees Celsius in {location_data['city']}"
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
    ipstack_access_key = 'https://princewilldev.com/'
    response = requests.get(f'http://api.ipstack.com/{ip}?access_key={ipstack_access_key}')
    data = response.json()
    return {
        'city': data.get('city', 'Unknown'),
        'country': data.get('country_name', 'Unknown')
    }

def get_temperature(city):
    openweather_api_key = 'a64222d0621682143c070b0824387864'
    response = requests.get(f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={openweather_api_key}&units=metric')
    data = response.json()
    return data['main']['temp']

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
