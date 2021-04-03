'''LED visual effects'''

# to use this handler, run:
#    sudo apt-get install libjpeg-dev
#    sudo pip install pillow

import Config
from eventmanager import Evt
from led_event_manager import LEDEffect, Color
import gevent
import os
from PIL import Image, ImageDraw

def userBitmap(args):
    if args['RACE'].results and 'by_race_time' in args['RACE'].results:
        leaderboard = args['RACE'].results['by_race_time']
    else:
        return False

    for line in leaderboard:
        if args['node_index'] == line['node']:
            callsign = line['callsign']
            break

    if callsign:
        args['bitmaps'] = [
            {"image": "static/user/" + callsign + ".png", "delay": 0}
        ]
        showBitmap(args)
    else:
        return False

def showBitmap(args):
    if 'strip' in args:
        strip = args['strip']
    else:
        return False

    def setPixels(img):
        pos = 0
        for row in range(0, img.height):
            for col in range(0, img.width):
                if pos >= strip.numPixels():
                    return

                c = col
                if Config.LED['INVERTED_PANEL_ROWS']:
                    if row % 2 == 0:
                        c = 15 - col

                px = img.getpixel((c, row))
                strip.setPixelColor(pos, Color(px[0], px[1], px[2]))
                pos += 1

    bitmaps = args['bitmaps']
    if bitmaps and bitmaps is not None:
        for bitmap in bitmaps:
            if os.path.exists(bitmap['image']):
                img = Image.open(bitmap['image'])
            else:
                img = Image.new('RGB', (1, 1))
                draw = ImageDraw.Draw(img)
                if 'color' in args:
                    draw.rectangle((0, 0, 1, 1), fill=convertColor(args['color']))
                else:
                    draw.rectangle((0, 0, 1, 1), fill=(127, 127, 127))

            img = img.rotate(90 * Config.LED['PANEL_ROTATE'])
            img = img.resize((Config.LED['LED_COUNT'] // Config.LED['LED_ROWS'], Config.LED['LED_ROWS']))

            setPixels(img)
            strip.show()

            delay = bitmap['delay']
            gevent.sleep(delay/1000.0)

def convertColor(color):
    return color >> 16, (color >> 8) % 256, color % 256

def discover(*args, **kwargs):
    # state bitmaps
    return [
    LEDEffect("bitmapCallsign", "Image: user/[callsign].png", userBitmap, {
            'manual': False,
            'include': [Evt.CROSSING_ENTER, Evt.CROSSING_EXIT, Evt.RACE_LAP_RECORDED, Evt.RACE_WIN],
            'exclude': [Evt.ALL],
            'recommended': [Evt.CROSSING_ENTER, Evt.CROSSING_EXIT, Evt.RACE_LAP_RECORDED, Evt.RACE_WIN],
        }, {
            'time': 5
        }),

    LEDEffect("bitmapRHLogo", "Image: RotorHazard", showBitmap, {
            'include': [Evt.SHUTDOWN],
            'recommended': [Evt.STARTUP]
        }, {
            'bitmaps': [
                {"image": "static/image/LEDpanel-16x16-RotorHazard.png", "delay": 0}
                ],
            'time': 60
            },
        ),
    LEDEffect("bitmapOrangeEllipsis", "Image: Orange Ellipsis", showBitmap, {
            'include': [Evt.SHUTDOWN],
            'recommended': [Evt.RACE_STAGE]
        }, {
            'bitmaps': [
                {"image": "static/image/LEDpanel-16x16-ellipsis.png", "delay": 0}
                ],
            'time': 8
        }),
    LEDEffect("bitmapGreenArrow", "Image: Green Upward Arrow", showBitmap, {
            'include': [Evt.SHUTDOWN],
            'recommended': [Evt.RACE_START]
        }, {
            'bitmaps': [
                {"image": "static/image/LEDpanel-16x16-arrow.png", "delay": 0}
                ],
            'time': 8
        }),
    LEDEffect("bitmapRedX", "Image: Red X", showBitmap, {
            'include': [Evt.SHUTDOWN],
            'recommended': [Evt.RACE_STOP]
        }, {
            'bitmaps': [
                {"image": "static/image/LEDpanel-16x16-X.png", "delay": 0}
                ],
            'time': 8
        }),
    LEDEffect("bitmapCheckerboard", "Image: Checkerboard", showBitmap, {
            'include': [Evt.SHUTDOWN],
            'recommended': [Evt.RACE_FINISH, Evt.RACE_STOP]
        }, {
            'bitmaps': [
                {"image": "static/image/LEDpanel-16x16-checkerboard.png", "delay": 0}
                ],
        'time': 20
        })
    ]
