#! /usr/bin/env python

import os
import sys
import json
import importlib

from fcntl import lockf, LOCK_UN, LOCK_EX
from traceback import print_exc
from ConfigParser import ConfigParser

def write_file(file, text):
    fd = open(file, "a")
    lockf(fd, LOCK_EX)
    try:
        fd.write(text)
    finally:
        lockf(fd, LOCK_UN)
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

    config = ConfigParser()
    config.read(os.path.join(state, "config"))

    modules = config.get("daq", "modules").split(",")

    sensors = []
    for module in modules:
        sensors.extend(read_devices(config, module))

    text = "\n".join([json.dumps(s) for s in sensors])
    write_file(os.path.join(state, "pending"), text + "\n")
