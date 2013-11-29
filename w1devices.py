#! /usr/bin/env python

import os, re
from socket import getfqdn
from time import time

BUS = "/sys/bus/w1/devices"
SLAVE = "w1_slave"
DEVICE = getfqdn()

VALID = re.compile("^([0-9a-fA-F]{2})-[0-9a-fA-F]{12}$")

def read_data(config, device):
    results = []

    if device != DEVICE:
        return results

    names = os.listdir(BUS)
    for sensor in names:
        if not os.path.isdir(os.path.join(BUS, sensor)):
            continue
        match = VALID.match(sensor)
        if not match:
            continue
        if match.group(1) == "28":
            read_temperature(results, sensor)

    return results


def devices(config):
    return [DEVICE]

def read_temperature(results, sensor):
    tfile = open(os.path.join(BUS, sensor, "w1_slave"))
    text = tfile.read()
    tfile.close()

    temperature_data = text.split()[-1]
    temperature = float(temperature_data[2:])
    temperature = temperature / 1000

    results.append({
        "device": DEVICE,
        "sensor": "w1-%s" % sensor,
        "type": "temperature",
        "time": int(time()),
        "value": temperature
    })
