#! /usr/bin/env python

import sys
import os
import re
import json
from time import time
from pytz import timezone, utc
from datetime import datetime

def to_epoch(time):
    epoch = datetime.fromtimestamp(0, utc)
    delta = time - epoch
    return delta.seconds + delta.days * 24 * 3600

def read_xml(fname, device):
    from xml.etree import ElementTree

    results = []

    tree = ElementTree.parse(fname)

    for interval in tree.getroot().findall(".//{http://www.w3.org/2005/Atom}IntervalReading"):
        period = interval.find("{http://www.w3.org/2005/Atom}timePeriod")
        time = datetime.utcfromtimestamp(int(period.find("{http://www.w3.org/2005/Atom}start").text))
        time = time.replace(tzinfo = timezone("America/Los_Angeles"))
        results.append({
            "device": "sce-" + device,
            "sensor": "meter",
            "type": "mains",
            "time": to_epoch(time),
            "duration": int(period.find("{http://www.w3.org/2005/Atom}duration").text),
            "value": float(interval.find("{http://www.w3.org/2005/Atom}value").text)
        })

    return results

def read_csv(fname):
    from csv import DictReader, excel

    results = []

    dialect = excel()
    dialect.skipinitialspace = True

    lines = open(fname).readlines()
    header = DictReader(lines[0:2], dialect = dialect).next()
    device = header["Service Account"]

    data = DictReader(lines[3:], dialect = dialect)

    for datum in data:
        time = datetime.strptime(datum["Interval Date & Time"], "%m/%d/%Y %I:%M %p ")
        time = time.replace(tzinfo = timezone("America/Los_Angeles"))
        results.append({
            "device": "sce-" + device,
            "sensor": "meter",
            "type": "mains",
            "time": to_epoch(time),
            "duration": 3600,
            "value": float(datum["kWh Delivered"])
        })

    return results

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Syntax: sce.py <datafile>")
        sys.exit(1)

    fname = sys.argv[1]
    if not os.path.isfile(fname):
        print("File not found.")
        sys.exit(1)

    result = re.match(r"SCE_Usage_([\d-]+)_[\d-]+_to_[\d-]+\.xml", os.path.basename(fname))
    if result is not None:
        results = read_xml(fname, result.group(1))
        print("\n".join([json.dumps(r) for r in results]))
    elif fname[-4:] == ".csv":
        results = read_csv(fname)
        print("\n".join([json.dumps(r) for r in results]))
    else:
        print("Unknown file format.")
        sys.exit(1)
