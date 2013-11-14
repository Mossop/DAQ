import w1devices
import sys
import json
from fcntl import lockf, LOCK_UN, LOCK_EX

def write_file(file, text):
    fd = open(file, "a")
    lockf(fd, LOCK_EX)
    try:
        fd.write(text)
    finally:
        lockf(fd, LOCK_UN)
        fd.close()

def read_devices(module):
    list = []
    for device in module.devices():
        list.extend(module.read_data(device))
    return list

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Syntax: daq.py <outputfile>")
        sys.exit(1)
    sensors = []
    sensors.extend(read_devices(w1devices))

    text = "\n".join([json.dumps(s) for s in sensors])
    write_file(sys.argv[1], text + "\n")
