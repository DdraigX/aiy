#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-18 Richard Hull and contributors
# See LICENSE.rst for details.
# PYTHON_ARGCOMPLETE_OK

"""
Display the Raspberry Pi logo (loads image as .png).
"""

import time
import datetime
import os.path
import threading
from demo_opts import get_device
from luma.core.render import canvas
from PIL import Image, ImageSequence
from luma.core.sprite_system import framerate_regulator


blurb = """


   Episode IV:
   A NEW HOPE

It is a period of
civil war. Rebel
spaceships, striking
from a hidden base,
have won their first
victory against the
evil Galactic Empire.

"""
now = datetime.datetime.now()


def draw_login_screen():
    with canvas(device) as draw:
        # draw.rectangle(device.bounding_box, outline="white", fill="black")
        draw.text((1, 1), "+++Servo Skull+++", fill="white")
        # time.sleep(2)
        draw.text((1, 10), "/", fill="white")
        # time.sleep(2)
        draw.text((1, 20), "/", fill="white")
        # time.sleep(2)
        draw.text((1, 30), "Loading...", fill="white")
        # time.sleep(2)
        draw.text((1, 40), "/", fill="white")
        # time.sleep(2)
        draw.text((1, 50), "/", fill="white")
        # time.sleep(2)
        draw.text((1, 60), "Servo Alpha Online", fill="white")

        print(now.date())
        draw.multiline_text((20, 70), str(now.date()), fill="white", align="center")
        device.show()
        #time.sleep(10)

    for _ in range(5):
        for level in range(255, -1, -10):
            device.contrast(level)
            time.sleep(0.05)
        time.sleep(0.1)

        for level in range(0, 255, 10):
            device.contrast(level)
            time.sleep(0.05)


        # draw.text((1, 40), "Hello World", fill="white")

        # print("clearing screen")
        # device.clear()
        # draw.multiline_text((1,1), "+++Servo Skull Loading...+++", align="center")
        # for i, line in enumerate(blurb.split("\n")):
        #     draw.text((0, 40 + (i * 12)), text=line, fill="white")
        # for y in range(450):
        #     device.set_position((0, y))
        #     time.sleep(0.01)

def draw_mechanicus():
    img_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
        'images', 'mechanicus.png'))
    img = Image.open(img_path).convert("RGBA")
    basewidth = 128
    wpercent = (basewidth / float(img.size[0]))
    hsize = int((float(img.size[1]) * float(wpercent)))
    img = img.resize((basewidth, hsize), Image.ANTIALIAS)
    #fff = Image.new(logo.mode, logo.size, (255,) * 4)
    size = [min(*device.size)] * 2
    background = Image.new("RGBA", device.size, "white")
    posn = ((device.width - size[0]) // 2, device.height - size[1])
    #posn = ((device.width - device.height) // 2, 0)
    background.paste(img, posn)
    device.display(background.convert(device.mode))

def clearscreen():
    device.clear()
    #device.hide()


def loadaquila(loop):
    regulator = framerate_regulator(fps=10)
    img_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                            'images', 'aquila_mono_fix.gif'))
    banana = Image.open(img_path)
    size = [min(*device.size)] * 2
    posn = ((device.width - size[0]) // 2, device.height - size[1])

    while True:
        if loop == 'start':
            while loop:
                for frame in ImageSequence.Iterator(banana):
                    with regulator:
                        background = Image.new("RGB", device.size, "white")
                        background.paste(frame.resize(size, resample=Image.LANCZOS), posn)
                        device.display(background.convert(device.mode))
        elif loop == 'stop':
            break

    #time.sleep(10)

def main():

    while True:
        loadimage = raw_input("Display images select 1,2, or 0 to clear")
        if loadimage == '1':
            print("loading login screen")
            device.clear()
            draw_login_screen()

        elif loadimage == '2':
            print("loading mechanicus")
            device.clear()
            draw_mechanicus()
        elif loadimage == '3':
            device.clear()
            loadaquila('start')
        elif loadimage == '0':
            print("clearing screen")
            clearscreen()
        elif loadimage == 'q':
            loadaquila('stop')
        elif loadimage == 'n':
            print("exiting")
            break


    # with canvas(device) as draw:
    #     # draw.rectangle(device.bounding_box, outline="white", fill="black")
    #     draw.text((1, 1), "+++Servo Skull+++", fill="white")
    #     #time.sleep(2)
    #     draw.text((1, 10), "/", fill="white")
    #     #time.sleep(2)
    #     draw.text((1, 20), "/", fill="white")
    #     #time.sleep(2)
    #     draw.text((1, 30), "Loading...", fill="white")
    #     #time.sleep(2)
    #     draw.text((1, 40), "/", fill="white")
    #     #time.sleep(2)
    #     draw.text((1, 50), "/", fill="white")
    #     #time.sleep(2)
    #     draw.text((1, 60), "Servo Alpha Online", fill="white")
    #     print(now.date())
    #     draw.multiline_text((20, 70), str(now.date()), fill="white", align="center")
    #     #time.sleep(2)
    #     #draw.text((1, 40), "Hello World", fill="white")
    #
    #     #print("clearing screen")
    #     #device.clear()
    #     #draw.multiline_text((1,1), "+++Servo Skull Loading...+++", align="center")
    #     # for i, line in enumerate(blurb.split("\n")):
    #     #     draw.text((0, 40 + (i * 12)), text=line, fill="white")
    #     # for y in range(450):
    #     #     device.set_position((0, y))
    #     #     time.sleep(0.01)
    #
    #
    # for _ in range(5):
    #     for level in range(255, -1, -10):
    #         device.contrast(level)
    #         time.sleep(0.05)
    #     time.sleep(0.1)
    #
    #     for level in range(0, 255, 10):
    #         device.contrast(level)
    #         time.sleep(0.05)


    # img_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
    #     'images', 'mechanicus.png'))
    # img = Image.open(img_path).convert("RGBA")
    # basewidth = 128
    # wpercent = (basewidth / float(img.size[0]))
    # hsize = int((float(img.size[1]) * float(wpercent)))
    # img = img.resize((basewidth, hsize), Image.ANTIALIAS)
    # #fff = Image.new(logo.mode, logo.size, (255,) * 4)
    # size = [min(*device.size)] * 2
    # background = Image.new("RGBA", device.size, "white")
    # posn = ((device.width - size[0]) // 2, device.height - size[1])
    # #posn = ((device.width - device.height) // 2, 0)


    # loopbol = True
    # while loopbol:
    #    for angle in range(0, 360, 2):
    #         #rot = logo.rotate(angle, resample=Image.BILINEAR)
    #         #img = Image.composite(rot, fff, rot)
    #         background.paste(img, posn)
    # #background.paste(frame.resize(size, resample=Image.LANCZOS), posn)
    #         device.display(background.convert(device.mode))
    #    # time.sleep(10)
    #    # print("breaking out")
    #    # break
    #
    #    keeploop = raw_input("Keep looping  y/n")
    #    if keeploop != 'y':
    #         print(keeploop)
    #         print("Closing Program")
    #         break
    #             #loopbol = False
    #
    # img_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
    #                                         'images', 'decal5.png'))
    # img = Image.open(img_path).convert("RGBA")
    # basewidth = 128
    # wpercent = (basewidth / float(img.size[0]))
    # hsize = int((float(img.size[1]) * float(wpercent)))
    # img = img.resize((basewidth, hsize), Image.ANTIALIAS)
    # # fff = Image.new(logo.mode, logo.size, (255,) * 4)
    # size = [min(*device.size)] * 2
    # background = Image.new("RGBA", device.size, "white")
    # posn = ((device.width - size[0]) // 2, device.height - size[1])
    # # posn = ((device.width - device.height) // 2, 0)
    #
    # loopbol = True
    # while loopbol:
    #     for angle in range(0, 360, 2):
    #         # rot = logo.rotate(angle, resample=Image.BILINEAR)
    #         # img = Image.composite(rot, fff, rot)
    #         background.paste(img, posn)
    #         # background.paste(frame.resize(size, resample=Image.LANCZOS), posn)
    #         device.display(background.convert(device.mode))
    #     # time.sleep(10)
    #     # print("breaking out")
    #     # break
    #
    #     keeploop = raw_input("Keep looping  y/n")
    #     if keeploop != 'y':
    #         print(keeploop)
    #         print("Closing Program")
    #         break
    #         # loopbol = False
    #
    #
    # print("The Loop has ended")
    # time.sleep(5)
    # print("Closing Program")

if __name__ == "__main__":
    try:
        device = get_device()
        main()
    except KeyboardInterrupt:
        pass
