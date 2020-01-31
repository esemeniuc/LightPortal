# pip install geoip2 pysolar pytz timezonefinder numpy
import datetime
import urllib.request
from typing import Tuple

import geoip2.database
import pytz
import timezonefinder
from pysolar import radiation
from pysolar.solar import get_altitude
from pysolar.util import get_sunrise_sunset

import kelvin_rgb_conversion
import util


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


# outputs the raw lux brightness of a given lat lon, and a normalized 0-255 value
def get_lux(latitude_deg: float, longitude_deg: float, date: datetime) -> Tuple[float, int]:
    raw_lux = radiation.get_radiation_direct(date, get_altitude(latitude_deg, longitude_deg, date))
    sr, ss = get_sunrise_sunset(latitude_deg, longitude_deg, date)
    print('sunrise: ', sr)
    print('sunset: ', ss)
    daylight_span = ss - sr
    midday = sr + daylight_span / 2
    print('midday: ', midday)
    max_lux = radiation.get_radiation_direct(date, get_altitude(latitude_deg, longitude_deg, midday))
    print('max_lux: ', max_lux)
    normalized = (raw_lux / max_lux) * 255  # put in 0 - 255 range
    return raw_lux, util.clamp(normalized, 0, 255)


# x: sun altitude, from 0 deg to 180 deg
# returns sunlight color temp in kelvin (k)
# assumes the following:
# SUNRISE_TEMP = 3000
# MIDDAY_TEMP = 5500
# SUNSET_TEMP = 3000
# see https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html
def colour_temp(alt_deg: float) -> int:
    if not 0 < alt_deg < 180:
        return 0

    if alt_deg > 90:
        alt_deg -= 90  # sunrise and sunset are mirrors of each other

    if alt_deg < 30:
        # linear function based on
        # https://micro.magnet.fsu.edu/primer/lightandcolor/colortemperatureintro.html
        return int(50 * alt_deg + 3000)

    if alt_deg < 90:
        return int(5 / 18 * (alt_deg - 90) ** 2 + 5500)


def demo():
    # daly city
    latitude_deg = 37.70577
    longitude_deg = -122.46192
    date = datetime.datetime(2020, 1, 27, 7, 58, 1, 0, tzinfo=datetime.timezone.utc)
    return get_lux(latitude_deg, longitude_deg, date)


# k: color temp (3000 to 5500k)
# brightness: 0-255
def update(brightness: int, k: int) -> None:
    # philips hue stuff
    # group = Bridge().groups[1]
    # def from_k(k):
    #     return (1, 1)
    #
    # h, s = from_k(k)
    # group.hue = h
    # group.saturation = s
    # group.brightness = brightness

    # grid stuff
    from rgbmatrix import RGBMatrix, RGBMatrixOptions

    options = RGBMatrixOptions()
    options.rows = 32
    options.chain_length = 1
    options.parallel = 1
    options.hardware_mapping = 'adafruit-hat'
    matrix = RGBMatrix(options=options)
    r, g, b = kelvin_rgb_conversion.color_temp_to_rgb(k)
    print('rgb: ', r, g, b)
    matrix.Fill(r, g, b)
    matrix.brightness = brightness


def main():
    latitude_deg, longitude_deg = get_location_from_ip()
    # date = get_time_with_timezone(latitude_deg, longitude_deg)
    date = datetime.datetime(2020, 1, 29, 12, 30, 1, 0, tzinfo=pytz.timezone('America/Los_Angeles'))
    brightness, normalized_brightness = get_lux(latitude_deg, longitude_deg, date)
    print('brightness: ', brightness, normalized_brightness)
    alt = get_altitude(latitude_deg, longitude_deg, date)
    print('alt :', alt)
    k = colour_temp(alt)
    update(normalized_brightness, k)


main()
