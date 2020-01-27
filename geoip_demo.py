# pip install geoip2 pysolar pytz timezonefinder
import datetime
import urllib.request
from typing import Tuple

import geoip2.database
import pytz
import timezonefinder
from pysolar import radiation
from pysolar.solar import get_altitude


# from phue import Bridge

def get_location_from_ip() -> Tuple[float, float]:
    reader = geoip2.database.Reader('GeoLite2-City.mmdb')
    ips = urllib.request.urlopen('https://checkip.amazonaws.com').read().decode('ascii').split(
        ', ')  # can return multiple ips
    main_ip = ips[0].strip()
    response = reader.city(main_ip)
    latitude_deg = response.location.latitude
    longitude_deg = response.location.longitude
    return latitude_deg, longitude_deg


def get_time_with_timezone(latitude_deg: float, longitude_deg: float) -> datetime.datetime:
    tf = timezonefinder.TimezoneFinder()
    tz_str = tf.timezone_at(lat=latitude_deg, lng=longitude_deg)
    tz = pytz.timezone(tz_str)
    date = datetime.datetime.now(tz=tz)
    return date


# outputs the brightness of a given lat lon
def get_lux(latitude_deg: float, longitude_deg: float, date: datetime) -> float:
    return radiation.get_radiation_direct(date, get_altitude(latitude_deg, longitude_deg, date))


def demo():
    # daly city
    latitude_deg = 37.70577
    longitude_deg = -122.46192
    date = datetime.datetime(2020, 1, 27, 7, 13, 1, 0, tzinfo=datetime.timezone.utc)
    return get_lux(latitude_deg, longitude_deg, date)


latitude_deg, longitude_deg = get_location_from_ip()
date = get_time_with_timezone(latitude_deg, longitude_deg)
brightness = get_lux(latitude_deg, longitude_deg, date)
print(brightness)
# group = Bridge().groups[1]
# group.brightness = brightness
