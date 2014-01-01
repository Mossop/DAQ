#! /usr/bin/env python

import sys
import os
import re
import json
from time import time
from xml.etree import ElementTree
from pytz import timezone, utc
from datetime import datetime

def to_epoch(time):
    epoch = datetime.fromtimestamp(0, utc)
    delta = time - epoch
    return delta.seconds + delta.days * 24 * 3600

def read_xml(fname, device):
    results = []

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
    else:
        print("Unknown file format.")
        sys.exit(1)
