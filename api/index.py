from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import Response
from kerykeion import AstrologicalSubject, NatalAspects, KerykeionChartSVG, AspectModel, LunarPhaseModel
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
from typing import Any, Dict
import os
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)

# Create FastAPI instance with custom docs and OpenAPI URL
app = FastAPI(docs_url="/api/py/docs", openapi_url="/api/py/openapi.json")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your frontend URL here
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

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

# Mapping of sign abbreviations to full names
SIGN_NAME_MAP = {
    "Ari": "Aries",
    "Tau": "Taurus",
    "Gem": "Gemini",
    "Can": "Cancer",
    "Leo": "Leo",
    "Vir": "Virgo",
    "Lib": "Libra",
    "Sco": "Scorpio",
    "Sag": "Sagittarius",
    "Cap": "Capricorn",
    "Aqu": "Aquarius",
    "Pis": "Pisces"
}

def serialize(obj: Any) -> Any:
    """
    Recursively serialize an object into a JSON-compatible format.
    """
    if isinstance(obj, dict):
        return {k: serialize(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize(i) for i in obj]
    elif isinstance(obj, (str, int, float, bool, type(None))):
        # Directly return basic data types
        return obj
    elif isinstance(obj, AspectModel):
        # Convert AspectModel instance to a dictionary
        return {
            "p1_name": obj.p1_name,
            "p1_abs_pos": obj.p1_abs_pos,
            "p2_name": obj.p2_name,
            "p2_abs_pos": obj.p2_abs_pos,
            "aspect": obj.aspect,
            "orbit": obj.orbit,
            "aspect_degrees": obj.aspect_degrees,
            "aid": obj.aid,
            "diff": obj.diff,
            "p1": obj.p1,
            "p2": obj.p2
        }
    elif isinstance(obj, LunarPhaseModel):
        # Convert LunarPhaseModel instance to a dictionary
        return {
            "degrees_between_s_m": obj.degrees_between_s_m,
            "moon_phase": obj.moon_phase,
            "sun_phase": obj.sun_phase,
            "moon_emoji": obj.moon_emoji,
            "moon_phase_name": obj.moon_phase_name
        }
    elif isinstance(obj, BaseModel):
        return serialize(obj.dict())
    elif hasattr(obj, '__dict__'):
        return serialize(vars(obj))
    else:
        return obj  # Return the object as is if it's a basic data type

def optimize_json_structure(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Optimize the JSON structure by extracting common keys, removing specified attributes,
    and replacing abbreviated sign names with full names.
    """
    optimized_data = {}
    general_exclude_keys = {"emoji", "sign_num", "house", "point_type"}
    aspects_exclude_keys = {"p1_abs_pos", "p2_abs_pos", "aid", "diff", "p1", "p2"}

    for category, items in data.items():
        if category == "aspects":
            # Filter aspects specifically
            optimized_aspects = []
            for aspect in items:
                if isinstance(aspect, dict):
                    filtered_aspect = {
                        k: v for k, v in aspect.items() if k not in aspects_exclude_keys
                    }
                    optimized_aspects.append(filtered_aspect)
            optimized_data[category] = optimized_aspects
        elif isinstance(items, dict):
            # Extract the first item's keys as the common keys
            first_item = next(iter(items.values()), None)
            if first_item and isinstance(first_item, dict):
                # Filter out the general excluded keys
                common_keys = [
                    key for key in first_item.keys() if key not in general_exclude_keys
                ]
                optimized_data["keys"] = common_keys

                # Extract values corresponding to the common keys
                optimized_values = []
                for item in items.values():
                    if isinstance(item, dict):
                        values = []
                        for key in common_keys:
                            value = item.get(key)
                            # Replace abbreviated sign names with full names
                            if key == "sign" and value in SIGN_NAME_MAP:
                                value = SIGN_NAME_MAP[value]
                            values.append(value)
                        optimized_values.append(values)
                optimized_data[category] = optimized_values
            else:
                optimized_data[category] = items
        else:
            optimized_data[category] = items

    return optimized_data


def generate_astrology_details(name: str, birth_date: str, birth_time: str, latitude: float, longitude: float, timezone: str) -> Dict[str, Any]:
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
        online=False,
        city="New Delhi",  # Default value
        nation="IN"        # Default value
    )

    # Extract planetary data
    planets = {
        "sun": serialize(subject.sun),
        "moon": serialize(subject.moon),
        "mercury": serialize(subject.mercury),
        "venus": serialize(subject.venus),
        "mars": serialize(subject.mars),
        "jupiter": serialize(subject.jupiter),
        "saturn": serialize(subject.saturn),
        "uranus": serialize(subject.uranus),
        "neptune": serialize(subject.neptune),
        "pluto": serialize(subject.pluto),
        "true_node": serialize(subject.true_node),
        "mean_node": serialize(subject.mean_node),
        "chiron": serialize(subject.chiron),
        "mean_lilith": serialize(subject.mean_lilith),
        "mean_south_node": serialize(subject.mean_south_node),
        "true_south_node": serialize(subject.true_south_node),
        "sidereal_mode": serialize(subject.sidereal_mode)
    }

    # Extract house data
    houses = {
        "first_house": serialize(subject.first_house),
        "second_house": serialize(subject.second_house),
        "third_house": serialize(subject.third_house),
        "fourth_house": serialize(subject.fourth_house),
        "fifth_house": serialize(subject.fifth_house),
        "sixth_house": serialize(subject.sixth_house),
        "seventh_house": serialize(subject.seventh_house),
        "eighth_house": serialize(subject.eighth_house),
        "ninth_house": serialize(subject.ninth_house),
        "tenth_house": serialize(subject.tenth_house),
        "eleventh_house": serialize(subject.eleventh_house),
        "twelfth_house": serialize(subject.twelfth_house)
    }

    # Initialize the NatalAspects class with the subject
    natal_aspects = NatalAspects(user=subject)

    # Retrieve all aspects
    aspects = serialize(natal_aspects.all_aspects)

    # Extract lunar phase
    lunar_phase = serialize(subject.lunar_phase)

    # Compile the astrology data
    astrology_data = {
        "planets": planets,
        "houses": houses,
        "aspects": aspects,
        "lunar_phase": lunar_phase
    }

    # Optimize the JSON structure
    optimized_astrology_data = optimize_json_structure(astrology_data)

    return optimized_astrology_data

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

        # Return the optimized astrology data as JSON
        return JSONResponse(content={"astrology_data": astrology_data})

    except ValueError as ve:
        logging.error(f"Validation error occurred: {str(ve)}")
        raise HTTPException(status_code=400, detail=f"Validation error: {str(ve)}")
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
    
@app.post("/api/py/generate_chart_svg")
async def generate_chart_svg(birth_data: BirthData):
    try:
        logging.info(f"Received request for SVG generation: {birth_data}")

        # Validate date and time format
        try:
            birth_year, birth_month, birth_day = map(int, birth_data.date_of_birth.split('-'))
            birth_hour, birth_minute = map(int, birth_data.time_of_birth.split(':'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date or time format.")

        # Create an AstrologicalSubject instance
        subject = AstrologicalSubject(
            name=birth_data.name,
            year=birth_year,
            month=birth_month,
            day=birth_day,
            hour=birth_hour,
            minute=birth_minute,
            lat=birth_data.latitude,
            lng=birth_data.longitude,
            tz_str=birth_data.timezone,
            online=False,
            city='New Delhi',  # Replace with actual city if available
            nation='IN'        # Replace with actual nation code if available
        )

        # Define the output directory
        output_directory = '/tmp'

        # Ensure the output directory exists
        os.makedirs(output_directory, exist_ok=True)

        # Generate the SVG chart
        chart_svg = KerykeionChartSVG(subject, new_output_directory=output_directory)
        try:
            chart_svg.makeSVG()
        except Exception as e:
            logging.error(f"Error generating SVG with KerykeionChartSVG: {e}")
            raise HTTPException(status_code=500, detail="Failed to generate the SVG chart.")

        # Dynamically locate the generated SVG file
        # generated_files = os.listdir(output_directory)
        # svg_files = [f for f in generated_files if f.endswith('.svg')]

        # if not svg_files:
        #     logging.error("No SVG file was created or found in the output directory.")
        #     raise HTTPException(status_code=500, detail="Failed to generate the SVG chart.")

        # Assuming the latest SVG file is the one just created
        # svg_files.sort(key=lambda f: os.path.getmtime(os.path.join(output_directory, f)), reverse=True)
        # actual_output_path = os.path.join(output_directory, svg_files[0])
        actual_output_path = output_directory + "/" + birth_data.name + ' - Natal Chart.svg'
        logging.info(f"Actual SVG path: {actual_output_path}")

        # Read and return the SVG content
        with open(actual_output_path, 'r', encoding='utf-8') as svg_file:
            svg_content = svg_file.read()

        if not svg_content.strip():
            logging.error("Generated SVG content is empty.")
            raise HTTPException(status_code=500, detail="Generated SVG content is empty.")

        logging.info("SVG chart generated successfully.")
        return Response(content=svg_content, media_type='image/svg+xml')

    except HTTPException as http_exc:
        logging.error(f"HTTP error occurred: {http_exc.detail}")
        raise http_exc
    except Exception as e:
        logging.error(f"Unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")