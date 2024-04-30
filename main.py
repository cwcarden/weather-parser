import requests
import sqlite3
import os 
from dotenv import load_dotenv

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
                    weeklyrainin REAL,
                    monthlyrainin REAL
                )''')

try:
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes

    data = response.json()
    
    # Assumes only one record; modify if multiple
    record = data[0]
    cursor.execute('''INSERT INTO weather (
                        dateutc, tempf, humidity, windspeedmph, windgustmph, eventrainin, weeklyrainin, monthlyrainin
                      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (
                        record['dateutc'],
                        record['tempf'],
                        record['humidity'],
                        record['windspeedmph'],
                        record['windgustmph'],
                        record['eventrainin'],
                        record['weeklyrainin'],
                        record['monthlyrainin']
                      ))

    conn.commit()

except requests.exceptions.RequestException as e:
    print("Error:", e)

finally:
    conn.close()
