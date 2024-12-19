from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from kerykeion import AstrologicalSubject, NatalAspects
from fastapi.responses import JSONResponse
import logging
from typing import Any

# Setup logging
logging.basicConfig(level=logging.INFO)

# Create FastAPI instance with custom docs and OpenAPI URL
app = FastAPI(docs_url="/api/py/docs", openapi_url="/api/py/openapi.json")

@app.get("/api/py/helloFastApi")
def hello_fast_api():
    return {"message": "Hello from FastAPI"}

class BirthData(BaseModel):
    name: str
    date_of_birth: str  # Format: "YYYY-MM-DD"
    time_of_birth: str  # Format: "HH:MM"
    latitude: float
    longitude: float
    timezone: str

def serialize(obj: Any) -> Any:
    """
    Recursively serialize an object into a JSON-compatible format.
    """
    if isinstance(obj, dict):
        return {k: serialize(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize(i) for i in obj]
    elif hasattr(obj, '__dict__'):
        return serialize(vars(obj))
    else:
        return str(obj)  # Convert non-serializable objects to strings

def generate_astrology_details(name: str, birth_date: str, birth_time: str, latitude: float, longitude: float, timezone: str) -> dict:
    # Parse birth date and time
    birth_year, birth_month, birth_day = map(int, birth_date.split('-'))
    birth_hour, birth_minute = map(int, birth_time.split(':'))

    # Create an AstrologicalSubject instance
    subject = AstrologicalSubject(
        name=name,
        year=birth_year,
        month=birth_month,
        day=birth_day,
        hour=birth_hour,
        minute=birth_minute,
        lat=latitude,
        lng=longitude,
        tz_str=timezone,
        online=False
    )

    # Calculate natal aspects
    natal_aspects = NatalAspects(subject)
    aspects = natal_aspects.all_aspects

    # Serialize the subject to a JSON-compatible dictionary
    astrology_data = serialize(subject)

    # Add aspects to the astrology data
    #astrology_data['aspects'] = [serialize(aspect) for aspect in aspects]

    return astrology_data

@app.post("/api/py/generate_chart_data")
async def generate_chart_data(birth_data: BirthData):
    try:
        logging.info(f"Received request for: {birth_data}")

        # Generate astrology details
        astrology_data = generate_astrology_details(
            name=birth_data.name,
            birth_date=birth_data.date_of_birth,
            birth_time=birth_data.time_of_birth,
            latitude=birth_data.latitude,
            longitude=birth_data.longitude,
            timezone=birth_data.timezone
        )

        logging.info("Astrology details generated successfully.")

        # Return the astrology data as JSON
        return JSONResponse(content={"astrology_data": astrology_data})

    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
