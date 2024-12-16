# GrowController
Project building a GrowController that measures temperature and humidity. A dehumidifyer can be managed by an active solenoid (coming soon). The project is based on a RaspberryPI 2B and DHT22 sensor .


## Running script on bootup
We use a systemd service in order to start the script as soon as the PI boots up.

1. Create a unit file to define the custom service

```
sudo nano /lib/systemd/system/GrowController.service
```

2. Add following text, make sure to replace `user` with your local user
```
[Unit]
Description=My GrowController Service
After=multi-user.target

[Service]
Type=idle
WorkingDirectory=/home/user/Programming/GrowController/SensorBox
ExecStart=/home/user/Programming/GrowController/env/bin/python3.11 /home/user/Programming/GrowController/SensorBox/humidity.py > /home/user/Programming/logs/GrowController.log 2>&1
Restart=always

[Install]
WantedBy=multi-user.target
```

3. Add permissions on the unit file
```
sudo chmod 644 /lib/systemd/system/GrowController.service
```

4. Configure systemd and reboot
```
sudo systemctl daemon-reload
sudo systemctl enable GrowController.service
sudo reboot
```

5. To check if the service is running use
```
sudo systemctl status GrowController.service
```
