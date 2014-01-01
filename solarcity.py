#! /usr/bin/env python

import sys
import os
import re
import json
from time import time
from pytz import timezone, utc
from datetime import datetime, timedelta

def to_epoch(time):
    epoch = datetime.fromtimestamp(0, utc)
    delta = time - epoch
    return delta.seconds + delta.days * 24 * 3600

def read_html(fname):
    from xml.etree import ElementTree

    results = []

    tree = ElementTree.parse(fname)
    table = tree.getroot().find(".//{http://www.w3.org/1999/xhtml}table[@id='gvRawDataByDevice']")

    headings = [th.text for th in table.find("{http://www.w3.org/1999/xhtml}tr").findall("{http://www.w3.org/1999/xhtml}th")]

    def make_dict(rows):
        for row in rows:
            cells = [c.text for c in row.findall("{http://www.w3.org/1999/xhtml}td")]
            if len(cells) == 0:
                continue
            yield dict(zip(headings, cells))

    data = make_dict(table.findall("{http://www.w3.org/1999/xhtml}tr"))

    for datum in data:
        time = datetime.strptime(datum["Measured Date (30 min)"], "%m/%d/%Y %I:%M:%S %p")
        time = time - timedelta(seconds = time.second)
        time = time.replace(tzinfo = timezone("America/Los_Angeles"))

        results.append({
            "device": "solarcity-" + datum["InverterID"],
            "sensor": "generated",
            "type": "solar",
            "time": to_epoch(time),
            "duration": 15 * 60,
            "value": float(datum["Energy (kWh AC)"])
        })

    return results

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Syntax: solarcity.py <datafile>")
        sys.exit(1)

    fname = sys.argv[1]
    if not os.path.isfile(fname):
        print("File not found.")
        sys.exit(1)

    results = read_html(fname)
    print("\n".join([json.dumps(r) for r in results]))
