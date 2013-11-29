#! /usr/bin/env python

import json
import urllib

def read_data(config, device):
    def add_result(results, sensor, type, value):
        if value == "--":
            return

        results.append({
            "device": "wunderground-%s" % device,
            "sensor": sensor,
            "type": type,
            "time": int(data["observation_epoch"]),
            "value": float(value)
        })

    url = "http://api.wunderground.com/api/%s/conditions/q/%s.json" % (config.get("wunderground", "apikey"), device)
    data = json.load(urllib.urlopen(url))["current_observation"]

    results = []
    add_result(results, "temperature", "temperature", data["temp_c"]),
    add_result(results, "humidity", "humidity", data["relative_humidity"][0:-1]),
    add_result(results, "wind_degrees", "wind_degrees", data["wind_degrees"]),
    add_result(results, "wind_speed", "wind_speed", data["wind_kph"]),
    add_result(results, "wind_gust", "wind_gust", data["wind_gust_kph"]),
    add_result(results, "pressure", "pressure", data["pressure_mb"]),
    add_result(results, "visibility", "visibility", data["visibility_km"]),
    add_result(results, "precipitation-hr", "precipitation_hour", data["precip_1hr_metric"]),
    add_result(results, "precipitation-day", "precipitation_day", data["precip_today_metric"])
    return results

def devices(config):
    return config.get("wunderground", "stations").split(",")
