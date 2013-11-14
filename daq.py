#! /usr/bin/env python

import os
import sys
import json
import importlib

from urllib2 import urlopen
from traceback import print_exc
from ConfigParser import ConfigParser
from datetime import datetime

API_URL = "/api/v1/submit"

def read_file(file):
    if not os.path.isfile(file):
        return []

    fd = open(file, "r")
    try:
        return [l.strip() for l in fd]
    finally:
        fd.close()

def append_file(file, lines):
    if len(lines) == 0:
        return

    fd = open(file, "a")
    try:
        fd.write("\n".join(lines))
        fd.write("\n")
    finally:
        fd.close()

def read_devices(config, modulename):
    list = []
    try:
        module = importlib.import_module(modulename)
        for device in module.devices(config):
            try:
                list.extend(module.read_data(config, device))
            except:
                print_exc()
    except:
        print_exc()
    return list

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Syntax: daq.py <statedir>")
        sys.exit(1)

    state = sys.argv[1]
    pendingfile = os.path.join(state, "pending")

    config = ConfigParser()
    config.read(os.path.join(state, "config"))

    modules = config.get("daq", "modules").split(",")

    sensors = []
    for module in modules:
        sensors.extend(read_devices(config, module))

    newresults = [json.dump(s) for s in sensors]

    try:
        allresults = read_file(pendingfile)
        allresults.extend(newresults)

        if len(allresults) == 0:
            sys.exit(0)

        url = config.get("daq", "server")
        if url[-1:] == "/":
            url = url[:-1]
        url = url + API_URL

        result = urlopen(url, "\n".join(allresults))

        if result.getcode() != 200:
            raise Exception("Unexcepted HTTP response %d" % result.getcode())

        processed = int(result.readline().strip())
        if processed != len(allresults):
            raise Exception("Didn't process all data packets, saw %d expected %d" % (processed, len(allresults)))

        if config.has_option("daq", "backup") and (config.get("daq", "backup") == "true"):
            filename = "backup-%s" % datetime.now().strftime("%Y%m%d%H%M%S")
            while os.path.isfile(os.path.join(state, filename)):
                filename = filename + "-1"
            os.rename(pendingfile, os.path.join(state, filename))
        else:
            os.remove(pendingfile)
    except:
        append_file(pendingfile, newresults)
        raise
