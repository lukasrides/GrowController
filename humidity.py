import time
from datetime import datetime
import schedule
import adafruit_dht
import board

print("Starting script..")
dht_device = adafruit_dht.DHT22(board.D24) # GPIO24=pin18 - nr 9 outside from status light
time.sleep(2.0)
print("Sensor initialized..")


def readSensor():
    attempts = 0
    success = False

    while attempts < 5: # try 5 times
        try:
            temperature_c = dht_device.temperature
            humidity = dht_device.humidity
            print(f"[{datetime.now()}] Temp: {temperature_c:.1f} C    Humidity: {humidity}%")
            success = True
            break
        except RuntimeError:
            attempts += 1
            print("Error - retrying...")
            time.sleep(0.5)  # Short delay before retrying

    if not success:
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

