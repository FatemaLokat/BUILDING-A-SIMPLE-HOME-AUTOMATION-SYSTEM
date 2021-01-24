import wiotp.sdk.gateway
import yaml
import psutil
import time
import socket
from datetime import timedelta
from timeloop import Timeloop
from struct import unpack_from

ANDROID_DEVICE_TYPE = "ANDROID"

def get_gateway_cilent(config_file_path):
    config = wiotp.sdk.gateway.parseConfigFile(config_file_path)
    client = wiotp.sdk.gateway.GatewayClient(config=config, logHandlers=None)
    return client

def send_status_event(client):
    payload={
        "cpu": psutil.cpu_percent(),
        "memory": psutil.virtual_memory().percent,
        "cpu count": psutil.cpu_count()
    }
    return client.publishEvent(eventId="status", msgFormat="json", data= payload, qos=1)

client = get_gateway_cilent('./gateway_config.yml')
print("Got the client.....")
client.connect()
print("Connection established")


devices_data = {}
def send_regular_status(client, interval):
    while True:
        send_status_event(client)
        time.sleep(interval)

UDP_IP = "192.168.1.3"
UDP_PORT = 60123 # The port where you want to receive the packets

# https://play.google.com/store/apps/details?id=com.ubccapstone.sensorUDP&hl=en_IN
properties = ['x_acc', 'y_acc', 'z_acc', 'x_gravity', 'y_gravity', 'z_gravity',  'x_rotation', 'y_rotation', 'z_rotation',
              'x_orientation', 'y_orientation', 'z_orientation', 'deprecated_1', 'deprecated_2', 'ambient_light', 'proximity',
              'keyboard_button_pressed']


def unpack_and_return(data, offset):
    return unpack_from("!f", data, offset)[0]


def process_data(data):
    offset = 0
    result = {}
    for property in properties:
        result[property] = unpack_and_return(data, offset)
        offset += 4
    return result


def listen_sensor_data():
    sock = socket.socket(socket.AF_INET,
                         socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT))
    # Keep listening for data indefinitely
    while True:
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        data = process_data(data)
        yield data, addr

def send_android_device_event(client, device_id, eventId, data):
    client.publishDeviceEvent(
      ANDROID_DEVICE_TYPE, device_id, eventId, msgFormat="json", data=data, qos=0)

for data, device_addr in listen_sensor_data():
     send_android_device_event(client, device_addr[0], "status", data)

def gateway_command_callback(cmd):
    print("Command received for {}:{}: {}".format(cmd.typeId, cmd.deviceId, cmd.data))
    if cmd.typeId == 'reset':
        reset_data(devices_data)
    else:
        print("Unknown command type received")


def reset_data():
    devices_data.clear()
    # Add more custom logic here.
    pass