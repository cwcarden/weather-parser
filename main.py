import requests
import sqlite3
import os 
from dotenv import load_dotenv
from datetime import datetime, timezone
from dateutil import parser

load_dotenv()

api_key = os.getenv('API_KEY')
application_key = os.getenv('APPLICATION_KEY')
mac_address = os.getenv('MAC_ADDRESS')

url = f"https://rt.ambientweather.net/v1/devices/{mac_address}"
params = {
    "apiKey": api_key,
    "applicationKey": application_key,
    "endDate": "",
    "limit": 288
}

# Connect to SQLite database
conn = sqlite3.connect('weather_data.db')
cursor = conn.cursor()

# Ensure that you have already created a table with the correct structure:
cursor.execute('''CREATE TABLE IF NOT EXISTS weather (
                    dateutc INTEGER,
                    tempf REAL,
                    humidity INTEGER,
                    windspeedmph REAL,
                    windgustmph REAL,
                    eventrainin REAL,
                    lastRain INTEGER
                )''')

try:
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes

    data = response.json()
    
    # Assumes only one record; modify if multiple
    record = data[0]
    cursor.execute('''INSERT INTO weather (
                        dateutc, tempf, humidity, windspeedmph, windgustmph, eventrainin, lastRain
                      ) VALUES (?, ?, ?, ?, ?, ?, ?)''', (
                        record['dateutc'],
                        record['tempf'],
                        record['humidity'],
                        record['windspeedmph'],
                        record['windgustmph'],
                        record['eventrainin'],
                        record['lastRain'],
                      ))

    conn.commit()

except requests.exceptions.RequestException as e:
    print("Error:", e)

finally:
    conn.close()
    #last_rain = (data[0]['lastRain'])

    # Returns true if has been 48 hours since last rain
    def rain_last48():
        last_rain = (data[0]['lastRain'])
        date = parser.parse(last_rain)
        current_date = datetime.now(timezone.utc)
        time_difference = current_date - date
        return (time_difference.total_seconds() >= 48 * 3600) 

    # Returns True if is currently raining
    def is_raining():
        if (data[0]['eventrainin']) == 0:
            return False

    # Returns True if below freezing. Set to 33 as precaution
    def is_freezing():
        if (data[0]['tempf'] < 33):
            return True

    # Returns True if too windy 
    def is_windy():
        if (data[0]['windspeedmph'] > 15):
            return True
