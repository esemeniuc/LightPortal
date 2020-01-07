# pip install geoip2 pysolar
import datetime
import urllib.request

import geoip2.database
from pysolar import radiation
from pysolar.solar import get_altitude


# from phue import Bridge

def get_lux():
    reader = geoip2.database.Reader('GeoLite2-City.mmdb')
    ips = urllib.request.urlopen('https://checkip.amazonaws.com').read().decode('ascii').split(', ')
    main_ip = ips[0].strip()
    response = reader.city(main_ip)
    latitude_deg = response.location.latitude
    longitude_deg = response.location.longitude
    date = datetime.datetime.now(tz=datetime.timezone.utc)
    return get_brightness(latitude_deg, longitude_deg, date)


def get_brightness(latitude_deg=37.70577,  # daly city
                   longitude_deg=-122.46192,
                   date=datetime.datetime(2020, 1, 6, 2, 13, 1, 0, tzinfo=datetime.timezone.utc)):
    return radiation.get_radiation_direct(date, get_altitude(latitude_deg, longitude_deg, date))


brightness = get_lux()
# group = Bridge().groups[1]
# group.brightness = brightness
