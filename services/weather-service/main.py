from fastapi import FastAPI

app = FastAPI(title="Weather Service", description="Weather information service", version="1.0.0")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "weather-service"}

@app.get("/weather/{location}")
async def get_weather(location: str):
    return {
        "location": location,
        "temperature": "22°C",
        "condition": "Sunny",
        "humidity": "65%"
    } 