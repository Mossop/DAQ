#! /usr/bin/env python

from urllib2 import urlopen

API_URL = "/api/v1/submit"

def submit(server, measurements):
    if len(measurements) == 0:
        return

    if server[-1:] == "/":
        server = server[:-1]
    url = server + API_URL

    result = urlopen(url, "\n".join(measurements))

    if result.getcode() != 200:
        raise Exception("Unexcepted HTTP response %d" % result.getcode())

    processed = int(result.readline().strip())
    if processed != len(measurements):
        raise Exception("Didn't process all data packets, saw %d expected %d" % (processed, len(measurements)))

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Syntax: submit.py <server>")
        sys.exit(1)

    server = sys.argv[1]

    measurements = [m.strip() for m in sys.stdin.readlines() if len(m.strip()) > 0]
    submit(server, measurements)
