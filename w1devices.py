import os, re
from time import time

BUS = "/sys/bus/w1/devices"
SLAVE = "w1_slave"

VALID = re.compile("^([0-9a-fA-F]{2})-[0-9a-fA-F]{12}$")

def read_data(device):
    match = VALID.match(device)
    if match.group(1) == "28":
        return read_temperature(device)
    raise Error("Unknown device type")

def devices():
    names = os.listdir(BUS)
    for name in names:
        if not os.path.isdir(os.path.join(BUS, name)):
            continue
        if not VALID.match(name):
            continue
        yield name

def read_temperature(device):
    tfile = open(os.path.join(BUS, device, "w1_slave"))
    text = tfile.read()
    tfile.close()
    temperature_data = text.split()[-1]
    temperature = float(temperature_data[2:])
    temperature = temperature / 1000
    return [{
        "device": "w1-%s" % device,
        "sensor": "0",
        "type": "temperature",
        "time": int(time()),
        "value": temperature
    }]

if __name__ == "__main__":
    import json
    for device in devices():
        print("%s" % json.dumps(read_data(device)))
