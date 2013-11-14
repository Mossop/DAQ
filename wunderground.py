#! /usr/bin/env python

import json
import urllib

def read_data(config, device):
    def build_result(sensor, type, value):
        return {
            "device": "wunderground-%s" % device,
            "sensor": sensor,
            "type": type,
            "time": data["observation_epoch"],
            "value": float(value)
        }

    url = "http://api.wunderground.com/api/%s/conditions/q/pws:%s.json" % (config.get("wunderground", "apikey"), device)
    data = json.load(urllib.urlopen(url))["current_observation"]

    return [
      build_result("temperature", "temperature", data["temp_c"]),
      build_result("humidity", "humidity", data["relative_humidity"][0:-1]),
      build_result("wind_degrees", "wind_degrees", data["wind_degrees"]),
      build_result("wind_speed", "wind_speed", data["wind_kph"]),
      build_result("wind_gust", "wind_gust", data["wind_gust_kph"]),
      build_result("pressure", "pressure", data["pressure_mb"]),
      build_result("visibility", "visibility", data["visibility_km"]),
      build_result("precipition-hr", "precipitation_hour", data["precip_today_metric"]),
      build_result("precipitation-day", "precipitation_day", data["precip_today_metric"])
    ]

def devices(config):
    return config.get("wunderground", "stations").split(",")
