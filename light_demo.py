#sudo apt install python3-pip libatlas-base-dev
#enable the camera thru: sudo raspi-config
#deps:
#pip3 install numpy phue picamera webcolors

# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import webcolors

camera = PiCamera()

def capture_image(camera):
    # configure camera
    camera.resolution = (640,480)
    rawCapture = PiRGBArray(camera)
    time.sleep(0.1)
    # capture image
    camera.capture(rawCapture, format="rgb")
    return rawCapture.array

# get average pixel
def rgb_from_image(image):
    (height, width, pixel) = image.shape
    pixelsCount = height * width
    rSum = 0
    gSum = 0
    bSum = 0
    for row in image:
        for elem in row:
            (r, g, b) = elem
            rSum += r
            gSum += g
            bSum += b
    rAverage = rSum // pixelsCount
    gAverage = gSum // pixelsCount
    bAverage = bSum // pixelsCount
    pix = (rAverage, gAverage, bAverage)
    return pix

# get average pixel
def hsv_from_image(image):    
    import colorsys
    (height, width, pixel) = image.shape
    pixelsCount = height * width
    rSum = 0
    gSum = 0
    bSum = 0
    for row in image:
        for elem in row:
            (r, g, b) = elem
            rSum += r
            gSum += g
            bSum += b
    rAverage = rSum // pixelsCount
    gAverage = gSum // pixelsCount
    bAverage = bSum // pixelsCount
    pix = (rAverage / 255.0, gAverage / 255.0, bAverage / 255.0)
    return colorsys.rgb_to_hsv(pix[0], pix[1], pix[2])

def hsv_from_camera(camera):
    image = capture_image(camera)
    return hsv_from_image(image)

def rgb_from_camera(camera):
    image = capture_image(camera)
    return rgb_from_image(image)
    

# https://github.com/studioimaginaire/phue
# https://developers.meethue.com/develop/hue-api/lights-api/
from phue import Bridge
b = Bridge()
group = b.groups[1]

def phue_scaled_hsv(hsv):
    return int(round(65535 * hsv[0])), int(round(254 * hsv[1])), int(round(254 * hsv[2]))


def closest_colour(requested_colour):
    min_colours = {}
    for key, name in webcolors.css3_hex_to_names.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - requested_colour[0]) ** 2
        gd = (g_c - requested_colour[1]) ** 2
        bd = (b_c - requested_colour[2]) ** 2
        min_colours[(rd + gd + bd)] = name
    return min_colours[min(min_colours.keys())]


def set_hsv_from_camera(camera, group):
    image = capture_image(camera)
    rgb = rgb_from_image(image)
    print("setting color to: ", closest_colour(rgb))
    float_hsv = hsv_from_image(image)
    h, s, v = phue_scaled_hsv(float_hsv)
    upscaled_v = v + 30
    print('upscaled_v:', upscaled_v)
    group.hue = h
    group.saturation = s
    group.brightness = upscaled_v

for i in range(9999):
	set_hsv_from_camera(camera, group)
	time.sleep(600)
