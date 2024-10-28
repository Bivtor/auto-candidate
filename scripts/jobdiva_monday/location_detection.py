from fuzzywuzzy import fuzz
from shapely import Polygon
from shapely import Point
import pandas as pd
import re
import os
import googlemaps
from dotenv import load_dotenv
from base import CandidateData, ENV_PATH, CM_PATH, logger

# Global
DEFAULT_NOT_FOUND = "Not SoCal"


def create_polygons():
    """
    Reads in a csv file representing polygons made of lat/long representing zones in LA
    """

    # Read the CSV file into a DataFrame
    df = pd.read_csv(CM_PATH)

    # Create list of polygons
    polygons = []  # : list[tuple(Polygon, str)]

    # Create polygons from map
    for index, row in df.iterrows():
        # Target polygon & name
        polygon_str = str(row.iloc[0])
        name = str(row.iloc[1])

        # Format
        formatted_polygon = convert_polygon(polygon_str)

        # Append with name
        polygons.append((Polygon(formatted_polygon), name))

    return polygons


def convert_polygon(polygon_str):
    """
    Helper Function to convert the polygon string
    """
    # Use regular expressions to extract the coordinates
    coordinates = re.findall(r'(-?\d+\.\d+) (-?\d+\.\d+)', polygon_str)

    # Convert the coordinates to the desired format
    formatted_coordinates = [(float(x), float(y)) for x, y in coordinates]

    return formatted_coordinates


def compute_location_area(data: CandidateData):
    """
    Performs all operations needed to return the Stratified LA Location based on the general location provided
    """

    # Create polygons based on csv file
    # Ask googlemaps geocoding API to get lat/long of candidate location
    # Stratify candidate location based on labeled polygons

    # Check for 'OC' and return 'Orange County General'
    if is_approximately_oc(data.location):
        return "General Orange County"

    # Check for 'None' and return 'Central LA/ SoCal'
    if data.location.lower() == 'none':
        return 'Central LA/SoCal'

    # Create Polygon array and fill it
    polygons = create_polygons()

    # Get location from Google Geocoding location_coords[1], locarion_coords[0] (lat, long)
    location_coords = get_location(data.location)

    # Set coordinate field
    data.GPS_COORD = {
        "lat": location_coords[0],
        "long": location_coords[1]
    }
    # Log
    logger.info(
        f'{data.name} - -> Set location coordinates to: {location_coords[0]}, {location_coords[1]}')

    # Assign area location based on polygon fit
    candidate_area: str = check_map_location(location_coords, polygons)

    return candidate_area


def get_location(loc: str) -> list:
    """
    Get lat/long from api
    """
    # Load env
    load_dotenv(dotenv_path=ENV_PATH)

    # Create gmaps client
    gmaps = googlemaps.Client(key=os.getenv('MAPS_API_KEY'))

    # Geocode address
    geocode_result = gmaps.geocode(loc)

    # Check that results were found
    if (len(geocode_result)) == 0:
        return [0, 0]

    # Extract Lat/Long
    latitude = geocode_result[0]['geometry']['location']['lat']
    longitude = geocode_result[0]['geometry']['location']['lng']

    return [latitude, longitude]


def check_map_location(location, polygons):
    """
    Checks if the location fits one of the polygons
    Returns the location
    """

    # Assign default
    default = DEFAULT_NOT_FOUND

    # Create Point
    point = Point(location[1], location[0])

    # Check polygons
    for p in polygons:
        if (p[0].contains(point)):
            return p[1]

    # Default return value
    return default


# Special case for OC lol
def is_approximately_oc(input_string):
    # Calculate the similarity score between the input string and 'OC'
    similarity_score = fuzz.partial_ratio(input_string.upper(), 'OC')

    # You can adjust the threshold as needed
    threshold = 80  # Adjust this value based on your requirements

    # Check if the similarity score is above the threshold
    return similarity_score >= threshold
