#! /usr/bin/env python

import os, re
from socket import getfqdn
from time import time
from xml.etree import ElementTree
from pytz import timezone, utc
from datetime import datetime

def to_epoch(time):
    epoch = datetime.fromtimestamp(0, utc)
    delta = time - epoch
    return delta.seconds + delta.days * 24 * 3600

def read_data(config, device):
    results = []

    device = device[4:]

    state = config.get("daq", "state")
    fname = os.path.join(state, device) + ".xml"
    if not os.path.isfile(fname):
        return results

    tree = ElementTree.parse(fname)

    for interval in tree.getroot().findall(".//{http://www.w3.org/2005/Atom}IntervalReading"):
        period = interval.find("{http://www.w3.org/2005/Atom}timePeriod")
        time = datetime.fromtimestamp(int(period.find("{http://www.w3.org/2005/Atom}start").text))
        time = time.replace(tzinfo = timezone("America/Los_Angeles"))
        results.append({
            "device": "sce-" + device,
            "sensor": "electricity",
            "type": "energy",
            "time": to_epoch(time),
            "duration": int(period.find("{http://www.w3.org/2005/Atom}duration").text),
            "value": float(interval.find("{http://www.w3.org/2005/Atom}value").text)
        })

    return results


def devices(config):
    devices = []

    state = config.get("daq", "state")

    names = os.listdir(state)
    for name in names:
        if not os.path.isfile(os.path.join(state, name)):
            continue
        if name[-4:] != ".xml":
            continue
        devices.append("sce-" + name[0:-4])

    return devices
