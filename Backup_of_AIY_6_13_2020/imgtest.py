#!/usr/bin/env python3
from time import sleep
from PIL import Image
import os.path


# Import Luma.OLED libraries
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1327
# Configure the serial port
serial = i2c(port=1, address=0x3C)
device = ssd1327(serial, width=128, height=128, rotate=0)
# SSD1331 display size
#frameSize = (128, 128)

img_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                              'images', 'decal5.png'))

print(img_path)
filename = img_path
        # Open image file
print(filename)
image = Image.open(filename)
print("displayimage")
        # Output to OLED/LCD display
device.display(image)

        # Output to PC image viewer
image.show()

sleep(10)
