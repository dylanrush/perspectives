# Dylan Rush 2019
# Provided only for personal or educational use
# Commercial use prohibited

from perspectives import *
import time
from picamera import PiCamera
from PIL import Image
import io
import sys

hosts = {
    '192.168.0.17': {
            'updateFunction': Perspectives.kindle_touch_show_corner_fn,
            'resolution': (600, 800)
        },
    '192.168.0.18': {
        'updateFunction': Perspectives.kindle_touch_show_corner_fn,
        'resolution': (600, 800)
    },
    '192.168.0.19': {
        'updateFunction': Perspectives.kindle_touch_show_corner_fn,
        'resolution': (600, 800)
    }
}

stream = io.BytesIO()

corner_threshold = 85
diff_threshold = 100000

with PiCamera(resolution=(1296, 972), framerate=30) as camera:
    camera.start_preview()
    # Set ISO to the desired value
    #camera.iso = 300
    # Wait for the automatic gain control to settle
    time.sleep(2)
    # Now fix the values
    camera.shutter_speed = camera.exposure_speed
    camera.exposure_mode = 'off'
    g = camera.awb_gains
    camera.awb_mode = 'off'
    camera.awb_gains = g

    def cam_fn():
        stream.seek(0)
        camera.capture(stream, format='jpeg')
        stream.seek(0)
        return Image.open(stream).rotate(180)

    image_fn = "images/A_Sunday_on_La_Grande_Jatte.png"
    if len(sys.argv) > 1:
        image_fn = sys.argv[1]
    with open(image_fn, "rb") as fp:
        template = Image.open(fp).convert("L")
        perspectives = Perspectives(template, camera.resolution, hosts, cam_fn,
                                    corner_threshold, diff_threshold,
                                    Perspectives.find_corner_centroid,
                                    "debug" in sys.argv,
                                    )
        perspectives.refresh_all_hosts()
        while "loop" in sys.argv:
            time.sleep(10)
            perspectives.refresh_all_hosts()