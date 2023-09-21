import boto3
import json
import requests
from datetime import datetime
import uuid
import os

api_key = os.environ["OPENWEATHER_API_KEY"]
s3_bucket_name = "randy-pitcher-workspace--aws"
s3_folder_location = 'tabular/staged/rpw__aws/default/weather_raw'


def get_weather(city, api_key):
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "imperial",  # use 'metric' for Celsius
    }
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred for city {city}: {http_err}")
        return None
    except Exception as err:
        print(f"Other error occurred for city {city}: {err}")
        return None
    else:
        return response.json()


def lambda_handler(event, context):
    s3 = boto3.client("s3")

    cities = ["Indianapolis", "New York", "London", "Paris", "Tokyo", "Sydney"]

    for city in cities:
        weather_data = get_weather(city, api_key)

        if weather_data:
            file_name = f"{city}--{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}--{uuid.uuid4()}.json"
            s3.put_object(
                Bucket=s3_bucket_name, Key=f"{s3_folder_location}/{file_name}", Body=json.dumps(weather_data)
            )
