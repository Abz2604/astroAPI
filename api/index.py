from fastapi import FastAPI
from pydantic import BaseModel
import kerykeion as kr
from kerykeion import AstrologicalSubject  # Make sure to import AstrologicalSubject
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

### Create FastAPI instance with custom docs and openapi url
app = FastAPI(docs_url="/api/py/docs", openapi_url="/api/py/openapi.json")

@app.get("/api/py/helloFastApi")
def hello_fast_api():
    return {"message": "Hello from FastAPI"}

class BirthData(BaseModel):
    name: str
    date_of_birth: str  # Format: "YYYY-MM-DD"
    time_of_birth: str  # Format: "HH:MM"
    place_of_birth: str

@app.post("/api/py/generate_chart_data")
async def generate_chart_data(birth_data: BirthData):
    try:
        logging.info(f"Received request for: {birth_data}")

        # Split date and time into components
        year, month, day = map(int, birth_data.date_of_birth.split('-'))
        hour, minute = map(int, birth_data.time_of_birth.split(':'))
        logging.info("Split date and time into components successfully.")

        # Create an AstrologicalSubject instance
        logging.info("Creating AstrologicalSubject instance...")
        subject = AstrologicalSubject(
            name=birth_data.name,
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            city=birth_data.place_of_birth
        )
        logging.info("AstrologicalSubject instance created successfully.")

        # Extract all possible data points
        data = {
            "name": subject.name,
            "date_of_birth": birth_data.date_of_birth,
            "time_of_birth": birth_data.time_of_birth,
            "place_of_birth": birth_data.place_of_birth,
            "sun": subject.sun,
            "moon": subject.moon,
            "mercury": subject.mercury,
            "venus": subject.venus,
            "mars": subject.mars,
            "jupiter": subject.jupiter,
            "saturn": subject.saturn,
            "uranus": subject.uranus,
            "neptune": subject.neptune,
            "pluto": subject.pluto,
            "north_node": subject.true_node,
            "south_node": subject.true_south_node,
            "chiron": subject.chiron,
            "lilith": subject.mean_lilith,
            "ascendant": subject.ascendant,
            "midheaven": subject.midheaven,
            "houses": subject.houses,
            "aspects": subject.aspects,
            "dominant_element": subject.dominant_element,
            "dominant_modality": subject.dominant_modality,
            "retrograde_planets": subject.retrograde_planets,
            "chart_summary": subject.chart_summary()
        }

        logging.info(f"Sending response: {data}")
        return json.dumps(data, default=str)
    
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        return {"error": f"An unexpected error occurred: {str(e)}"}
