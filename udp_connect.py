import socket
from struct import unpack_from

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

for data, addr in listen_sensor_data():
     print(data, addr)