import os
import stomp
import socket
import json
import logging
from evdev import InputDevice, list_devices

logging.basicConfig(level=logging.DEBUG)

host = os.environ.get('STOMP_HOST', "localhost")
port = os.environ.get('STOMP_PORT', 61613)
client = os.environ.get('SUBSTATION_ID', "demo")
destination = os.environ.get('STOMP_TOPIC', '/topic/substations')


def find_input():
    devices = [InputDevice(fn) for fn in list_devices()]
    for dev in devices:
        print(dev.fn, dev.name, dev.phys)


def connect():
    conn = stomp.Connection(host_and_ports=[(host, int(port))])
    try:
        print('Connecting as <%s> to <%s:%s>' % (client, host, port))
        conn.start()
        conn.connect()
        message = json.dumps({"client": client,
                              "command": "connection",
                              "value": "%s: Reporting for duty" % client})
        conn.send(body=message, destination=destination)
        return conn

    except stomp.exception.ConnectFailedException:
        print('Unable to connect to Stomp server')
    except socket.error:
        print('Stomp unable to get a socket')


def main(conn):
    while True:
        # Get user input
        command = raw_input('Enter command: ')

        # Ask for value
        value = raw_input('Enter value: ')
        if value != "restart":
            print('Sending command <%s> value <%s> to server.\n' %
                  (command, value, ))
            message = json.dumps({"client": client,
                                  "command": command,
                                  "value": value})
            conn.send(body=message, destination=destination)
        continue

try:
    find_input()
    conn = connect()
    main(conn)
except KeyboardInterrupt:
    message = json.dumps({"client": client,
                          "command": "connection",
                          "value": "%s: Disconnected gracefully" % client})
    conn.send(body=message, destination=destination)
    conn.disconnect()
    print('\n\nKeyboard exception received. Exiting.')
    exit()
