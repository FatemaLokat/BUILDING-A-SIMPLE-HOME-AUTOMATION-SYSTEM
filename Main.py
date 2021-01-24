from datetime import timedelta
import time
from timeloop import Timeloop


client = get_gateway_cilent('gateway_config.yml')
client.connect()
time.sleep(2)
tl = Timeloop()

devices_data = {}


# Job that runs every 5 seconds
@tl.job(interval=timedelta(seconds=5))
def send_gateway_status():
    send_status_event(client)


# Job that runs every 200 milliseconds
@tl.job(interval=timedelta(milliseconds=200))
def send_device_readings():
    for device_addr, data in devices_data.items():
        send_android_device_event(client, device_addr, "status", data)
    devices_data.clear()

tl.start()

for data, device_addr in listen_sensor_data():
    devices_data[device_addr[0]] = data