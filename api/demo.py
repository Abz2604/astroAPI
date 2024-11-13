from kerykeion import AstrologicalSubject

# Function to generate astrology details
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

    # Serialize the subject to a JSON string
    astrology_json = subject.json(indent=4)

    return astrology_json

def main():
    # Sample input
    latitude = 28.6139
    longitude = 77.2090
    timezone = "Asia/Kolkata"
    birth_date = "1993-04-26"  # Format: YYYY-MM-DD
    birth_time = "05:30"       # Format: HH:MM (24-hour format)
    name = "Sample Name"

    # Generate astrology details
    astrology_json = generate_astrology_details(
        name=name,
        birth_date=birth_date,
        birth_time=birth_time,
        latitude=latitude,
        longitude=longitude,
        timezone=timezone
    )

    # Print the JSON string
    print(astrology_json)

if __name__ == "__main__":
    main()
