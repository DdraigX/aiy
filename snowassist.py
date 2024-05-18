#!/usr/bin/env python3
# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Run a recognizer using the Google Assistant Library with button support.

The Google Assistant Library has direct access to the audio API, so this Python
code doesn't need to record audio. Hot word detection "OK, Google" is supported.

It is available for Raspberry Pi 2/3 only; Pi Zero is not supported.
"""

import logging
import platform
import sys
import threading
import os
import random
import subprocess
import signal
import time
import re
#import os.path
#from demo_opts import get_device
#from PIL import Image, ImageSequence
#from luma.core.sprite_system import framerate_regulator
from rpi_ws281x import PixelStrip, Color
from google.assistant.library.event import EventType
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306, ssd1327, ssd1331, sh1106
from PIL import Image, ImageSequence
from luma.core.sprite_system import framerate_regulator
#from demo_opts import get_device


# Box and text rendered in portrait mode




#import os.path
#from demo_opts import get_device
#from PIL import Image, ImageSequence
#from luma.core.sprite_system import framerate_regulator

#Import animated_gif as display
#then call display.main

from aiy.assistant import auth_helpers
from aiy.assistant.library import Assistant
from aiy.board import Board, Led
#from aiy.voice import tts  #added-google
import aiy.voice.tts

import mod.snowboydecoder as snowboydecoder #added

#subprocess.init()

LED_COUNT = 12
LED_PIN = 10
LED_FREQ_HZ = 800000
LED_DMA = 10
LED_BRIGHTNESS = 10
LED_INVERT = False
LED_CHANNEL = 0

#added
if len(sys.argv) == 1:
    print("Error: need to specify model name")
    print("Usage: python demo.py your.model")
    sys.exit(-1)

model = sys.argv[1]
#/added


#global variables
strradiopart1 = "rtl_fm -f "
strradiopart2 = " -s 200000 -r 48000 -l 70 | aplay -r 48000 -f S16_LE"
strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
serial = i2c(port=1, address=0x3C)
device = ssd1327(serial, width=128, height=128, rotate=0)

class MyAssistant:
    """An assistant that runs in the background.

    The Google Assistant Library event loop blocks the running thread entirely.
    To support the button trigger, we need to run the event loop in a separate
    thread. Otherwise, the on_button_pressed() method will never get a chance to
    be invoked.
    """

    def __init__(self):
        self._task = threading.Thread(target=self._run_task)
        self._hotword = threading.Thread(target=self._run_hotword)  #added
        self._can_start_conversation = False
        self._assistant = None
        self._board = Board()
        self._board.button.when_pressed = self._on_button_pressed
        #self._say_omni = threading.Thread(target=self._say_omni)


    def start(self):
        """Starts the assistant.

        Starts the assistant event loop and begin processing events.
        """
        self._task.start()
        self._hotword.start()

    def _run_task(self):
        credentials = auth_helpers.get_assistant_credentials()
        with Assistant(credentials) as assistant:
            self._assistant = assistant
            for event in assistant.start():
                self._process_event(event)

   #added
    def _run_hotword(self):
        detector = snowboydecoder.HotwordDetector(model, sensitivity=0.4)
        #with aiy.voice.audio.get_recorder():
        while True:
                if self._can_start_conversation:
                   #self._board.led.state = Led.ON
                   detector.start(detected_callback=self._on_button_pressed,
                                  interrupt_check=lambda: not(self._can_start_conversation),
                                  sleep_time=0.03)
                   detector.terminate()
    #/added

    def say_omni(self):
        aiy.voice.tts.say('words are hard', lang="en-GB", pitch=10, speed=80)
        # os.system("mpg321 ignition1.mp3")

    # /added

    def say_ip(self):
        ip_address = subprocess.check_output("hostname -I | cut -d' ' -f1", shell=True)
        aiy.voice.tts.say('My IP address is %s' % ip_address.decode('utf-8'), lang="en-GB", pitch=10, speed=80)

    # added

    def get_temp(self):
        cputemp = subprocess.check_output("vcgencmd measure_temp", shell=True)
        #Try adding universal_newlines=False to above, to change to string
        cputemp2 = os.popen('vcgencmd measure_temp').readline()
        print(os.system('vcgencmd measure_temp'))
        cputemp2.replace("temp=","")
        #cputemp = cputemp.replace("temp=","")
        print(cputemp2)
        aiy.voice.tts.say('I am burning up, my %s' % cputemp.decode('utf-8'), lang="en-GB", pitch=10, speed=80)

##Radio Commands

    def stop_radio(self):
        try:
            process = int(subprocess.check_output(["pidof", "rtl_fm"]))
            print("Process pid = ", process)
            # os.system('kill -9 ' + process)
            os.kill(process, signal.SIGINT)
            time.sleep(1)
            os.system('amixer set Master 85%')
        except:
            aiy.voice.tts.say('Nothing is playing at the moment', lang="en-GB", pitch=10, speed=80)

    def radio_volume(self):
        audiolevel = re.sub("\D", "", text)
        print('amixer set Master ' + audiolevel + '%')
        #aiy.voice.tts.say('setting volume')
        os.system('amixer set Master ' + audiolevel + '%')

   # def start_radio(self):



##Test Area

    def _process_event(self, event):
        logging.info(event)
        if event.type == EventType.ON_START_FINISHED:
            self._board.led.status = Led.BEACON_DARK  # Ready.
            self._can_start_conversation = True
            # Start the voicehat button trigger.
            logging.info('Say "OK, Google" or press the button, then speak. '
                         'Press Ctrl+C to quit...')

        elif event.type == EventType.ON_CONVERSATION_TURN_STARTED:
            lightcircle.loadColor(strip, Color(255, 0, 0))
            os.system("aplay sfx/red1.wav")

            #self.loadColor(strip, Color(0, 0, 255))
            #strip.setPixelColor(0, 0, 255, 0)
            #strip.show()
            self._can_start_conversation = False
            self._board.led.state = Led.ON  # Listening.


        elif event.type == EventType.ON_RECOGNIZING_SPEECH_FINISHED and event.args:

            print('You said:', event.args['text'])
            lightcircle.loadColor(strip, Color(0, 255, 0))
            text = event.args['text'].lower()
            if text == 'power off':
                self._assistant.stop_conversation()
                power_off_pi()
            elif text == 'reboot':
                self._assistant.stop_conversation()
                reboot_pi()

            elif text == 'local ip':
                self._assistant.stop_conversation()
                print('localip')
                # ip_address = os.system('hostname -I')
                # print(ip_address + "derp")
                # ip_address = subprocess.check_output("hostname -I | cut -d' ' -f1", shell=True)
                # aiy.voice.tts.say('My IP address is %s' % ip_address.decode('utf-8'), lang="en-GB", pitch=10, speed=80)

                # print("worked")
                # aiy.voice.tts.say('My IP address is %s' % ip_address.decode('utf-8'))
                self.say_ip()

            elif text == 'get temp':
                self._assistant.stop_conversation()
                self.get_temp()


#Mechanicus Quotes

            elif text == 'tell me a quote':
                self._assistant.stop_conversation()
                #for x in range(10):
                randnum = random.randint(1, 10)
                print(randnum)
                if randnum == 1:
                    print('Playing Omni2')
                    os.system("mpg321 ./quotes/quote_servo_allpraiseomni.mp3")

                elif randnum  == 2:
                    print('Playing igintion')
                    os.system("mpg321 ./quotes/quote_ignition1.mp3")

                elif randnum  == 3:
                    print('Playing greatbell_de')
                    os.system("mpg321 ./quotes/quote_greatbell_de.mp3")

                elif randnum  == 4:
                    print('Playing greaterwork aus')
                    os.system("mpg321 ./quotes/quote_greater_work_aus.mp3")

                elif randnum  == 5:
                    print('Playing korielzeth')
                    os.system("mpg321 ./quotes/quote_koriel_zeth.mp3")

                elif randnum  == 6:
                    print('Playing lordofengines')
                    os.system("mpg321 ./quotes/quote_lordoftheengines.mp3")

                elif randnum  == 7:
                    print('Playing stealandwire')
                    os.system("mpg321 ./quotes/quote_steelandwire.mp3")

                elif randnum  == 8:
                    print('Playing warnings')
                    os.system("mpg321 ./quotes/quote_warnings_adeptusmechanicus.mp3")
                else:
                    #os.system("mpg321 ./quotes/quote_servo_allpraiseomni.mp3")
                    aiy.voice.tts.say('I have nothing to say at the moment',lang="en-GB", pitch=10, speed=80 )


# RTL-SDR Control

            elif 'turn on radio' in text:
                self._assistant.stop_conversation()
                #Splits up sentance
                #textlist = text.split()
                #print("last word" + textlist[0] + textlist[-1] + textlist[3])

                #freq = input('Enter freq ') + "M"
                #Gets Numbers for frequency
                freq = re.sub("\D", "", text)

                print(freq)
                numcount = len(freq)
                print(numcount)
                if numcount == 3:
                    freq = freq + "000K"
                elif numcount == 4:
                    freq = freq + "00K"
                elif numcount == 5:
                    freq = freq + "0K"
                else:
                    freq = freq + "K"

                #freq = textlist[-1] + "M"
                print("it worked " + freq)
                part1 = "rtl_fm -f "
                part2 = " -M wbfm -p 59 -r 48k -s 210K -r 48000 - | aplay -r 48000 -f S16_LE"
                cmd = part1 + freq + part2
                print(cmd)
                thevolume = 30
                print('amixer set Master ' + str(thevolume) + '%')
                os.system('amixer set Master ' + str(thevolume) + '%')
                subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)

                #self._assistant.start_conversation()
                #if text == "list frequency":
                #    text = event.args['text'].lower()
                #    print(text + " is it working? " + freq)
                #Figure out how to do nested commands
                #self._assistant.stop_conversation()
                #print()

            elif text == 'air band':
                self._assistant.stop_conversation()
                #print(part1)
                abscan = "rtl_fm -M am -f 118M:137M:25k -s 12k -g 50 -l 100 | aplay -r 12000 -f S16_LE"
                os.system('amixer set Master 50%')
                subprocess.Popen(abscan, stdout=subprocess.PIPE, shell=True)

            elif "ham radio" in text :
                self._assistant.stop_conversation()
                os.system('amixer set Master 30%')
                freq = re.sub("\D", "", text)

                print(freq)
                numcount = len(freq)
                print(numcount)
                if numcount == 3:
                    freq = freq + "000K"
                elif numcount == 4:
                    freq = freq + "00K"
                elif numcount == 5:
                    freq = freq + "0K"
                else:
                    freq = freq + "K"

                print("Selected Frequency: " + freq)
                part1 = "rtl_fm -f "
                part2 = " -M wbfm -p 59 -r 48k -s 210K -r 48000 -l 150 | aplay -r 48000 -f S16_LE"
                cmd = part1 + freq + part2
                print(cmd)
                #thevolume = 30
                #print('amixer set Master ' + str(thevolume) + '%')
                #os.system('amixer set Master ' + str(thevolume) + '%')
                subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)

            elif text == 'scan ham band':
                self._assistant.stop_conversation()
                #print(part1)
                hamscan = "rtl_fm -f 145M:148M:5k -M wbfm -p 59 -r 48k -s 210K -r 48000 -l 150 | aplay -r 48000 -f S16_LE"
                os.system('amixer set Master 50%')
                subprocess.Popen(hamscan, stdout=subprocess.PIPE, shell=True)

            elif text == 'terminate radio':
                self._assistant.stop_conversation()
                self.stop_radio()
                #process = int(subprocess.check_output(["pidof", "rtl_fm"]))
                #print("Process pid = ", process)
                ##os.system('kill -9 ' + process)
                #os.kill(process,signal.SIGINT)
                #subprocess.Popen.terminate()

            elif text == "reset audio":
                self._assistant.stop_conversation()
                os.system('amixer set Master 85%')


#Playing Mechanicus Music

            elif "play music" in text:
                self._assistant.stop_conversation()
                os.system("amixer set Master 30%")
                #subprocess.Popen('mpg321 /mnt/nas_store/Music/Mechanicus/*', stdout=subprocess.PIPE, shell=True)
                #Music needs to terminate before switching types

                #last word, playlist outrun, warhammer, all
                textlist = text.split()
                print(textlist[-1])
                lastword = textlist[-1]
                if "warhammer" in lastword:
                    subprocess.Popen('mpg321 /mnt/nas_store/Music/Mechanicus/*', stdout=subprocess.PIPE, shell=True)
                elif "outrun" in lastword:
                    subprocess.Popen('mpg321 -B /mnt/nas_store/Music/Outrun/*', stdout=subprocess.PIPE, shell=True)
                elif "folder" in lastword:
                    #Insert Test MP3 and test MP3 in sub folder
                    subprocess.Popen('mpg321 -B /mnt/nas_store/Music/Outrun/*', stdout=subprocess.PIPE, shell=True)

            elif "terminate music" in text:
                self._assistant.stop_conversation()
                try:
                    self._assistant.stop_conversation()
                    process = int(subprocess.check_output(["pidof", "mpg321"]))
                    print("Process pid = ", process)
                    #os.system('kill ' + process)
                    os.kill(process,signal.SIGQUIT)
                    #os.kill(process, signal.SIGINT)
                    time.sleep(1)
                    os.system('amixer set Master 85%')
                except:
                    self._assistant.stop_conversation()
                    aiy.voice.tts.say('nothing is playing at the moment',lang="en-GB", pitch=10, speed=80 )



            #Test Area

            elif 'set audio level' in text:
                self._assistant.stop_conversation()
                #self.radio_volume()
                audiolevel = re.sub("\D", "", text)
                os.system('amixer set Master ' + audiolevel + '%')
                print(text+" workies?")
            elif 'lights' in text:
                self._assistant.stop_conversation()
                #display_oled.cleardisplay()
                #time.sleep(10)
                #display_oled.aquila('decal5.png')
                display_oled.display_decal()

                #strip.setPixelColor(1, Color(255, 0, 0))
                #strip.show()
                #loadColor(strip, Color(255,0,0))
                print("startlights")
                lightcircle.loadColor(strip, Color(0, 255, 0))
                time.sleep(1)
                #lightcircle.pulse(self)
            elif "terminate display" in text:
                self._assistant.stop_conversation()
                print("terminating display")
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)


            elif "testing" in text:
                self._assistant.stop_conversation()
                print(text+" workies?")
            elif text.startswith("world"):
                self._assistant.stop_conversation()
                print("hello you're an idiot" + text)
                textlist = text.split()
                print("last word" + textlist[0] + textlist[-1] + textlist[3])
            elif "get numbers" in text:
                self._assistant.stop_conversation()
                print(text)
                numbs = re.sub("\D", "", text)
                print("numbers are " + numbs)
                numcount = len(numbs)
                print(numcount)
                if numcount == 4:
                    numbs = numbs + "00K"
                else:
                    numbs = numbs + "0K"

                #numbs = filter(lambda x: x.isdigit(), text)
                #numbs = int(filter(text.isdigit(), str1))
                print(numbs)



            elif text == 'litany of ignition':
                self._assistant.stop_conversation()
                say_words()

            elif text == 'something':
                self._assistant.stop_conversation()
                print("helloworld")
                aiy.voice.tts.say('hello', lang="en-GB", pitch=10, speed=80)
                # os.system("aplay red1.wav")
                self.say_omni()

#/added

        elif event.type == EventType.ON_END_OF_UTTERANCE:
            self._board.led.state = Led.PULSE_QUICK  # Thinking.

        elif (event.type == EventType.ON_CONVERSATION_TURN_FINISHED
              or event.type == EventType.ON_CONVERSATION_TURN_TIMEOUT
              or event.type == EventType.ON_NO_RESPONSE):
            self._board.led.state = Led.BEACON_DARK  # Ready.
            self._can_start_conversation = True

        elif event.type == EventType.ON_ASSISTANT_ERROR and event.args and event.args['is_fatal']:
            sys.exit(1)

    def _on_button_pressed(self):
        # Check if we can start a conversation. 'self._can_start_conversation'
        # is False when either:
        # 1. The assistant library is not yet ready; OR
        # 2. The assistant library is already in a conversation.
        if self._can_start_conversation:
            self._assistant.start_conversation()


class lightcircle:

    def loadColor(strip, color, wait_ms=5000):
        # for i in range(strip.numPixels()):
        strip.setPixelColor(0, color)
        strip.setPixelColor(1, color)
        strip.setPixelColor(2, color)
        strip.setPixelColor(3, color)
        strip.setPixelColor(4, color)
        strip.setPixelColor(5, color)
        strip.setPixelColor(6, color)
        strip.setPixelColor(7, color)
        strip.setPixelColor(8, color)
        strip.setPixelColor(9, color)
        strip.setPixelColor(10, color)
        strip.setPixelColor(11, color)
        strip.show()
        #time.sleep(wait_ms / 1000.0)

    def pulse(self):
        for i in range(10):
            for i in range(5, 20, 2):
                time.sleep(.2)
                strip.setBrightness(i)
                #print(i)
                strip.show()
        # fade out
            for i in range(20, 5, -2):
                time.sleep(.2)
                strip.setBrightness(i)
                #print(i)
                strip.show()

class display_oled:

    def aquila(img):
        device.show()
        # img_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
        #                                      'images', img))
        # Image.open(img_path)
        # background = Image.new("RGBA", device.size, "black")
        # device.display(background.convert(device.mode))

        regulator = framerate_regulator(fps=0)
        img_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                            'images', img))
        banana = Image.open(img_path)
        size = [min(*device.size)] * 2
        posn = ((device.width - size[0]) // 2, device.height - size[1])

        while True:
            for frame in ImageSequence.Iterator(banana):
               with regulator:
                  background = Image.new("RGB", device.size, "white")
                  background.paste(frame.resize(size, resample=Image.LANCZOS), posn)
                  device.display(background.convert(device.mode))


    def cleardisplay():
        #device.display.clear(self)
        background = Image.new("RGBA", device.size, "black")
        device.display(background.convert(device.mode))
        print("clearing oled")
        device.clear()
        print("hide oled")
        device.hide()


    def showpic():
        img_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                'images', 'pi_logo.png'))
        logo = Image.open(img_path).convert("RGBA")
        fff = Image.new(logo.mode, logo.size, (255,) * 4)

        background = Image.new("RGBA", device.size, "white")
        posn = ((device.width - logo.width) // 2, 0)

        while True:
            for angle in range(0, 360, 2):
                rot = logo.rotate(angle, resample=Image.BILINEAR)
                img = Image.composite(rot, fff, rot)
                background.paste(img, posn)
                device.display(background.convert(device.mode))


    def display_decal():
        os.killpg(os.getpgid(display_oled.display_aquila().proc.pid), signal.SIGTERM)
        time.sleep(1)
        display_oled.cleardisplay()
        proc = subprocess.Popen('./disp_decal.py --display ssd1327 --width 128 --height 128', stdout=subprocess.PIPE, shell=True,
                            preexec_fn=os.setsid)

        # try:
        #     print("killing process2")
        #     os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        #
        #     print("displaying decal")
        #     proc = subprocess.Popen('./disp_decal.py --display ssd1327 --width 128 --height 128',
        #                             stdout=subprocess.PIPE, shell=True,
        #                             preexec_fn=os.setsid)
        # except:
        #     proc = subprocess.Popen('./disp_decal.py --display ssd1327 --width 128 --height 128', stdout=subprocess.PIPE, shell=True,
        #                      preexec_fn=os.setsid)

    def display_aquila():
        proc = subprocess.Popen('./aquila.py --display ssd1327 --width 128 --height 128', stdout=subprocess.PIPE,
                                       shell=True, preexec_fn=os.setsid)
        # proc = subprocess.Popen('./disp_decal.py --display ssd1327 --width 128 --height 128', stdout=subprocess.PIPE, shell=True,
        #                    preexec_fn=os.setsid)
        #fgprocid = os.getpgid(aqproc.pid)
        #print("aquila", proc.pid)
        #print("decal", proc.pid)
        #time.sleep(10)
        #print("killing process")
        #os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        #device.hide()
        #device.show()
        # display_oled.cleardisplay()
        #time.sleep(10)
        #display_oled.display_decal()
        # proc = subprocess.Popen('./disp_decal.py --display ssd1327 --width 128 --height 128', stdout=subprocess.PIPE, shell=True,
        #                     preexec_fn=os.setsid)
        # try:
        #     print("displaying aquila")
        #     aqproc = subprocess.Popen('./aquila.py --display ssd1327 --width 128 --height 128', stdout=subprocess.PIPE,
        #                               shell=True, preexec_fn=os.setsid)
        #     #print(os.getpgid(aqproc.pid))
        #     #os.killpg(os.getpgid(aqproc.pid), signal.SIGTERM)
        #
        #     print("displaying decal")
        #     # proc = subprocess.Popen('./disp_decal.py --display ssd1327 --width 128 --height 128',
        #     #                         stdout=subprocess.PIPE, shell=True,
        #     #                         preexec_fn=os.setsid)
        # except:
        #     print("error")
        #     # proc = subprocess.Popen('./disp_decal.py --display ssd1327 --width 128 --height 128', stdout=subprocess.PIPE, shell=True,
        #     #                  preexec_fn=os.setsid)


def main():

    logging.basicConfig(level=logging.INFO)
    #Add random quotes here, and movements
    #strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    strip.begin()
    #loadColor(strip, Color(255, 0, 255))
    #strip.setPixelColor(11, Color(255, 0, 255))
    #strip.show()
    MyAssistant().start()
    # strip.setPixelColor(1, Color(255, 0, 0))
    # strip.show()
    # loadColor(strip, Color(255,0,0))
    #print("starlights")


    #while True:
    #    for frame in ImageSequence.Iterator(banana):
    #        with regulator:
    #            background = Image.new("RGB", device.size, "white")
    #            background.paste(frame.resize(size, resample=Image.LANCZOS), posn)
     #           device.display(background.convert(device.mode))
    #display_oled.aquila(self)
    # aqproc = subprocess.Popen('./aquila.py --display ssd1327 --width 128 --height 128', stdout=subprocess.PIPE,
    #                           shell=True, preexec_fn=os.setsid)


    display_oled.display_aquila()
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0, 255, 0))
        strip.show()
        time.sleep(.05)

    strip.setPixelColor(0, Color(0, 255, 0))
    strip.setPixelColor(1, Color(0, 255, 0))
    strip.setPixelColor(2, Color(0, 255, 0))
    strip.setPixelColor(3, Color(0, 255, 0))
    strip.setPixelColor(4, Color(0, 255, 0))
    strip.setPixelColor(5, Color(0, 255, 0))
    strip.setPixelColor(6, Color(0, 255, 0))
    strip.setPixelColor(7, Color(0, 255, 0))
    strip.setPixelColor(8, Color(0, 255, 0))
    strip.setPixelColor(9, Color(0, 255, 0))
    strip.setPixelColor(10, Color(0, 255, 0))
    strip.setPixelColor(11, Color(0, 255, 0))
    strip.show()
    for x in range(5):
        for i in range(5, 10, 2):
            time.sleep(.1)
            strip.setBrightness(i)
            #print(i)
            strip.show()
        # fade out
        for i in range(10, 5, -2):
            time.sleep(.1)
            strip.setBrightness(i)
            #print(i)
            strip.show()
    #display_oled.aquila()
    #time.sleep(100)
    #print("putting to sleepclear screen")
    #display_oled.cleardisplay()

    #procid = subprocess.Popen.pid

    #print("killing aquila")
    #os.killpg(os.getpgid(aqproc.pid), signal.SIGTERM)
    #display_oled.cleardisplay()
    # process = int(subprocess.check_output(["pidof", "mpg321"]))
    # print("Process pid = ", process)
    # # os.system('kill ' + process)
    # os.kill(process, signal.SIGQUIT)
    #print('displaying mechanicus')
    #proc = subprocess.Popen('./piquila.py --display ssd1327 --width 128 --height 128', stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
    #time.sleep(10)
    #print("killing mech")
    #os.killpg(os.getpgid(mechproc.pid), signal.SIGTERM)

    #display_oled.aquila('mechanicus.png')
    # print("display oled")
    # regulator = framerate_regulator(fps=0)
    # img_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
    #                                         'images', 'aquila_mono_fix.gif'))
    # banana = Image.open(img_path)
    # size = [min(*device.size)] * 2
    # posn = ((device.width - size[0]) // 2, device.height - size[1])
    # index = 1
    # while True:
    #     for frame in ImageSequence.Iterator(banana):
    #         with regulator:
    #             background = Image.new("RGB", device.size, "white")
    #             background.paste(frame.resize(size, resample=Image.LANCZOS), posn)
    #             device.display(background.convert(device.mode))
    #             print(index)
    #             index = index + 1

    #with canvas(device) as draw:
    #    draw.rectangle(device.bounding_box, outline="white", fill="black")
    #    draw.text((10, 40), "Hello World", fill="white")
    #lightcircle.loadColor(strip, Color(0, 255, 255))
    #loadColor(strip, Color(0, 0, 255))

if __name__ == '__main__':
    main()

