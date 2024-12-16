import time
from datetime import datetime
import schedule
import adafruit_dht
import board
import thingspeak
import requests


WRITE_API = '24V45T2VJ24JLZTE' # put your write API key here, or you´ll push your data to my channel
BASE_URL = 'https://api.thingspeak.com/update'

data = {
    'api_key' : WRITE_API,
    'field1' : 1,
    'field2' : 2
}


print("Starting system..")
dht_device = adafruit_dht.DHT22(board.D24) # GPIO24=pin18 - nr 9 outside from status light on PI 2B
time.sleep(2.0)
print("System initialized..")


def readSensor():
    attempts = 0
    success = False

    while attempts < 5: # try 5 times
        try:
            temperature_c = dht_device.temperature
            humidity = dht_device.humidity
            time.sleep(0.5)
            print(f"[{datetime.now()}] Temp: {temperature_c:.1f} C    Humidity: {humidity}%")
            data['field1'] = temperature_c
            data['field2'] = humidity
            response = requests.post(BASE_URL,data=data)                # post data to ThingSpeak 
            response.raise_for_status()                                 # throws exception on bad reply
            success = True
            break      

        except requests.exceptions.HTTPError as http_err:
            # Handle HTTP error codes
            print(f"HTTP error occurred: {http_err}")
            raise RuntimeError(f"HTTP request failed with status code {response.status_code}") from http_err

        except requests.exceptions.RequestException as req_err:
            # Handle other possible request errors (e.g., network issues)
            print(f"Request error occurred: {req_err}")
            raise RuntimeError("Request failed") from req_err
        
        except RuntimeError:
            attempts += 1
            success = False
            print("Error - retrying with attempt nr.", str(attempts+1))
            time.sleep(0.5)  # Short delay before retrying

    if success == False:
        raise RuntimeError("Failed to read sensor data after 5 attempts")
        time.sleep(4.0)  # Wait before the next read



def schedule_reading():
    # Schedule to run at 00, 15, 30, 45 minutes past every hour
    schedule.every().hour.at(":00").do(readSensor)
    schedule.every().hour.at(":15").do(readSensor)
    schedule.every().hour.at(":30").do(readSensor)
    schedule.every().hour.at(":45").do(readSensor)
    print("Scheduled jobs..")
    # Print the next scheduled job time
    next_run_time = schedule.next_run()
    print(f"First job will run at {next_run_time}")


    while True:
        # Run the scheduled jobs
        schedule.run_pending()
        time.sleep(15)  # Sleep briefly to prevent excessive CPU usage

# Start the scheduling
schedule_reading()

