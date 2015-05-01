import os
import stomp
import socket
import json
import logging
from evdev import InputDevice, list_devices, categorize, ecodes

logging.basicConfig(level=logging.DEBUG)

host = os.environ.get('STOMP_HOST', "localhost")
port = os.environ.get('STOMP_PORT', 61613)
client = os.environ.get('SUBSTATION_ID', "demo")
destination = os.environ.get('STOMP_TOPIC', '/topic/substations')
scanner = os.environ.get('SCANNER', '/dev/input/event0')


def find_input():
    devices = [InputDevice(fn) for fn in list_devices()]
    for dev in devices:
        print(dev.fn, dev.name, dev.phys)


def attach_scanner():
    return InputDevice(scanner)


def read_input(dev):
    print("Reading from %s" % dev.name)
    scancodes = {
        # Scancode: ASCIICode
        0: None, 1: u'ESC', 2: u'1', 3: u'2', 4: u'3', 5: u'4', 6: u'5', 7: u'6', 8: u'7', 9: u'8',
        10: u'9', 11: u'0', 12: u'-', 13: u'=', 14: u'BKSP', 15: u'TAB', 16: u'q', 17: u'w', 18: u'e', 19: u'r',
        20: u't', 21: u'y', 22: u'u', 23: u'i', 24: u'o', 25: u'p', 26: u'[', 27: u']', 28: u'CRLF', 29: u'LCTRL',
        30: u'a', 31: u's', 32: u'd', 33: u'f', 34: u'g', 35: u'h', 36: u'j', 37: u'k', 38: u'l', 39: u';',
        40: u'"', 41: u'`', 42: u'LSHFT', 43: u'\\', 44: u'z', 45: u'x', 46: u'c', 47: u'v', 48: u'b', 49: u'n',
        50: u'm', 51: u',', 52: u'.', 53: u'/', 54: u'RSHFT', 56: u'LALT', 100: u'RALT'
    }

    capscodes = {
        0: None, 1: u'ESC', 2: u'!', 3: u'@', 4: u'#', 5: u'$', 6: u'%', 7: u'^', 8: u'&', 9: u'*',
        10: u'(', 11: u')', 12: u'_', 13: u'+', 14: u'BKSP', 15: u'TAB', 16: u'Q', 17: u'W', 18: u'E', 19: u'R',
        20: u'T', 21: u'Y', 22: u'U', 23: u'I', 24: u'O', 25: u'P', 26: u'{', 27: u'}', 28: u'CRLF', 29: u'LCTRL',
        30: u'A', 31: u'S', 32: u'D', 33: u'F', 34: u'G', 35: u'H', 36: u'J', 37: u'K', 38: u'L', 39: u':',
        40: u'\'', 41: u'~', 42: u'LSHFT', 43: u'|', 44: u'Z', 45: u'X', 46: u'C', 47: u'V', 48: u'B', 49: u'N',
        50: u'M', 51: u'<', 52: u'>', 53: u'?', 54: u'RSHFT', 56: u'LALT', 100: u'RALT'
    }
    # setup vars
    x = ''
    caps = False

    # grab that shit
    dev.grab()

    # loop
    for event in dev.read_loop():
        if event.type == ecodes.EV_KEY:
            # Save the event temporarily to introspect it
            data = categorize(event)
            if data.scancode == 42:
                if data.keystate == 1:
                    caps = True
                if data.keystate == 0:
                    caps = False
            if data.keystate == 1:  # Down events only
                if caps:
                    key_lookup = u'{}'.format(capscodes.get(data.scancode)) or u'UNKNOWN:[{}]'.format(
                        data.scancode)  # Lookup or return UNKNOWN:XX
                else:
                    key_lookup = u'{}'.format(scancodes.get(data.scancode)) or u'UNKNOWN:[{}]'.format(
                        data.scancode)  # Lookup or return UNKNOWN:XX
                if (data.scancode != 42) and (data.scancode != 28):
                    x += key_lookup  # Print it all out!
                if(data.scancode == 28):
                    print x
                    x = ''


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
    scanner = attach_scanner()
    read_input(scanner)
    # conn = connect()
    # main(conn)
except KeyboardInterrupt:
    # message = json.dumps({"client": client,
    #                       "command": "connection",
    #                       "value": "%s: Disconnected gracefully" % client})
    # conn.send(body=message, destination=destination)
    # conn.disconnect()
    print('\n\nKeyboard exception received. Exiting.')
    exit()
