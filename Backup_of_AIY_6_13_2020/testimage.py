#serial = i2c(port=1, address=0x3C)
#device = ssd1327(serial, width=128, height=128, rotate=0)

#jpeg-image-load-test.py
from time import sleep

from PIL import Image
'''
# Import Luma.OLED libraries
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1327
# Configure the serial port
serial = i2c(port=1, address=0x3C)
device = ssd1327(serial)
'''
# SSD1331 display size
frameSize = (128, 128)

def main():
    filename = "decal5.jpg"
    # Open image file
    image = Image.open(filename)
    '''
    # Output to OLED/LCD display
    device.display(image)
    '''
    # Output to PC image viewer
    image.show()
    
    sleep(10)
    
if __name__ == "__main__":
    main()
