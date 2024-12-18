import time
from datetime import datetime
import schedule
import adafruit_dht
import board
import thingspeak
import requests
import RPi.GPIO  as GPIO
import csv


class GrowController:
    def __init__(self,minHumidity,maxHumidity,solenoidPin):
        self.minHumidity = minHumidity
        self.maxHumidity = maxHumidity
        self.dehumidifyerIsOn = False
        self.solenoidPin = solenoidPin
        self.WRITE_API = '24V45T2VJ24JLZTE'                                 # put your write API key here, or you´ll push your data to my channel
        self.BASE_URL = 'https://api.thingspeak.com/update'  
        self.data = {
                        'api_key' : self.WRITE_API,
                        'field1' : 1,
                        'field2' : 2,
                        'field3' : 0
                    }
        self.logPath = '/home/lukas/Programming/GrowController/SensorValues.csv'
        
        # setup of GPIO
        GPIO.setmode(GPIO.BCM)                                              # use board specific pin numbering
        GPIO.setwarnings(False)                                             # ignore warnings
        GPIO.setup(self.solenoidPin,GPIO.OUT, initial=GPIO.LOW)             # set initial output value low

        # setup DHT
        print("Starting system..")
        self.dht_device = adafruit_dht.DHT22(board.D24)                     # GPIO24=pin18 - nr 9 outside from status light on PI 2B
        time.sleep(2.0)
        print("System initialized..")

    # set the GPIO pin that enables/disables the dehumidifyer depending on the humidity
    def setDehumidifyer(self,humidity):
        if humidity > self.maxHumidity and self.dehumidifyerIsOn == False:
            GPIO.output(self.solenoidPin, GPIO.HIGH)                        # activate dehumidifyer
            self.data['field3'] = 1
            self.dehumidifyerIsOn = True
        elif humidity < self.minHumidity and self.dehumidifyerIsOn == True:
            GPIO.output(self.solenoidPin, GPIO.LOW)                         # deactivate dehumidifyer
            self.data['field3'] = 0
            self.dehumidifyerIsOn = False 

    # store the data to a .csv file for later use
    def updateDataLog(self,timeNow,temp,relh):
        formatted_now = timeNow.strftime("%Y-%m-%d %H:%M")
        with open(self.logPath,'a') as dataLog:
            writer = csv.writer(dataLog)
            writer.writerow([formatted_now,temp,relh])

    def readSensor(self):
        attempts = 0
        success = False

        while attempts < 5: # try 5 times
            try:
                temperature_c = self.dht_device.temperature
                humidity = self.dht_device.humidity
                timeNow = datetime.now()
                time.sleep(0.5)

                self.setDehumidifyer(humidity)
                self.data['field1'] = temperature_c
                self.data['field2'] = humidity
                self.updateDataLog(timeNow, temperature_c, humidity)

                response = requests.post(self.BASE_URL,data=self.data)      # post data to ThingSpeak 
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
            GPIO.cleanup()
            raise RuntimeError("Failed to read sensor data after 5 attempts")
        

    def schedule_reading(self):
        # Schedule to run at 00, 15, 30, 45 minutes past every hour
        schedule.every().hour.at(":00").do(self.readSensor)
        schedule.every().hour.at(":10").do(self.readSensor)
        schedule.every().hour.at(":20").do(self.readSensor)
        schedule.every().hour.at(":30").do(self.readSensor)
        schedule.every().hour.at(":40").do(self.readSensor)
        schedule.every().hour.at(":50").do(self.readSensor)
        print("Scheduled jobs..")
        # Print the next scheduled job time
        next_run_time = schedule.next_run()
        print(f"First job will run at {next_run_time}")


        while True:
            # Run the scheduled jobs
            schedule.run_pending()
            time.sleep(15)  # Sleep briefly to prevent excessive CPU usage

        

if __name__ == "__main__":
    try:
        GrowController = GrowController(minHumidity=40.0,maxHumidity=55,solenoidPin=18)
        GrowController.schedule_reading()   # schedule reading
    except KeyboardInterrupt:
        print("Shutting down..")
        GPIO.cleanup()





        





