from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from kerykeion import AstrologicalSubject, KerykeionChartSVG
from fastapi.responses import JSONResponse
import logging
import json

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

def generate_astrology_details(name, birth_date, birth_time, latitude, longitude, timezone):
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

    # Determine the output directory
    output_directory = "/tmp"  # Ensure this directory is writable in your environment

    # Generate the SVG chart with dark theme
    chart = KerykeionChartSVG(subject, theme="dark", new_output_directory=output_directory)
    chart.makeSVG()

    # Construct the file path
    svg_filename = f"{name} - Natal Chart.svg"
    svg_filepath = os.path.join(output_directory, svg_filename)

    # Read the SVG content
    with open(svg_filepath, "r", encoding="utf-8") as svg_file:
        svg_content = svg_file.read()

    # Optionally, delete the SVG file after reading its content
    # os.remove(svg_filepath)

    # Serialize the subject to a JSON-compatible dictionary
    astrology_data = subject.__dict__

    return astrology_data, svg_content

@app.post("/api/py/generate_chart_data")
async def generate_chart_data(birth_data: BirthData):
    try:
        logging.info(f"Received request for: {birth_data}")

        # Generate astrology details and SVG chart
        astrology_data, svg_content = generate_astrology_details(
            name=birth_data.name,
            birth_date=birth_data.date_of_birth,
            birth_time=birth_data.time_of_birth,
            latitude=birth_data.latitude,
            longitude=birth_data.longitude,
            timezone=birth_data.timezone
        )

        logging.info("Astrology details and SVG chart generated successfully.")

        # Return JSON data and SVG content
        return JSONResponse(content={
            "astrology_data": astrology_data,
            "svg_chart": svg_content
        })

    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
