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
from google.assistant.library.event import EventType

from aiy.assistant import auth_helpers
from aiy.assistant.library import Assistant
from aiy.board import Board, Led
#from aiy.voice import tts  #added-google
import aiy.voice.tts

import mod.snowboydecoder as snowboydecoder #added

#subprocess.init()

#added
if len(sys.argv) == 1:
    print("Error: need to specify model name")
    print("Usage: python demo.py your.model")
    sys.exit(-1)

model = sys.argv[1]
#/added

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

    def _say_omni(self):
        aiy.voice.tts.say('words are hard', lang="en-GB", pitch=10, speed=80)
        # os.system("mpg321 ignition1.mp3")

    # /added

    def say_ip(self):
        ip_address = subprocess.check_output("hostname -I | cut -d' ' -f1", shell=True)
        aiy.voice.tts.say('My IP address is %s' % ip_address.decode('utf-8'))

    # added

    def stop_radio(self):
        process = int(subprocess.check_output(["pidof", "rtl_fm"]))
        print("Process pid = ", process)
        # os.system('kill -9 ' + process)
        os.kill(process, signal.SIGINT)
        os.system('amixer set Master 94%')

    def radio_volume(self):
        print('amixer set Master ' + str(thevolume) + '%')
        #aiy.voice.tts.say('setting volume')
        os.system('amixer set Master ' + str(thevolume) + '%')


    def get_temp(self):
        cputemp = subprocess.check_output("vcgencmd measure_temp", shell=True)
        #Try adding universal_newlines=False to above, to change to string
        cputemp2 = os.popen('vcgencmd measure_temp').readline()
        print(os.system('vcgencmd measure_temp'))
        cputemp2.replace("temp=","")
        #cputemp = cputemp.replace("temp=","")
        print(cputemp2)
        aiy.voice.tts.say('I am burning up, my %s' % cputemp.decode('utf-8'), lang="en-GB", pitch=10, speed=80)

    def _process_event(self, event):
        logging.info(event)
        if event.type == EventType.ON_START_FINISHED:
            self._board.led.status = Led.BEACON_DARK  # Ready.
            self._can_start_conversation = True
            # Start the voicehat button trigger.
            logging.info('Say "OK, Google" or press the button, then speak. '
                         'Press Ctrl+C to quit...')

        elif event.type == EventType.ON_CONVERSATION_TURN_STARTED:
            #os.system("aplay red1.wav")
            self._can_start_conversation = False
            self._board.led.state = Led.ON  # Listening.


        elif event.type == EventType.ON_RECOGNIZING_SPEECH_FINISHED and event.args:
            print('You said:', event.args['text'])
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
                say_ip()

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

            elif text == 'turn on radio':
                self._assistant.stop_conversation()
                freq = input('Enter freq ') + "M"
                print("it worked " + freq)
                part1 = "rtl_fm -f "
                part2 = " -s 200000 -r 48000 | aplay -r 48000 -f S16_LE"
                cmd = part1 + freq + part2
                print(cmd)
                thevolume = 50
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


            elif text == 'stop radio':
                self._assistant.stop_conversation()
                stop_radio()
                #process = int(subprocess.check_output(["pidof", "rtl_fm"]))
                #print("Process pid = ", process)
                ##os.system('kill -9 ' + process)
                #os.kill(process,signal.SIGINT)
                #subprocess.Popen.terminate()



            #Test Area

            elif text == 'set audio level':
                self._assistant.stop_conversation()
                print(text+" workies?")
            elif "testing" in text:
                self._assistant.stop_conversation()
                print(text+" workies?")
            elif text.startswith("world"):
                self._assistant.stop_conversation()
                print("hello you're an idiot" + text)
                textlist = text.split()
                print("last word" + textlist[0] + textlist[-1] + textlist[3])



            elif text == 'litany of ignition':
                self._assistant.stop_conversation()
                say_words()

            elif text == 'something':
                self._assistant.stop_conversation()
                print("helloworld")
                aiy.voice.tts.say('hello', lang="en-GB", pitch=10, speed=80)
                # os.system("aplay red1.wav")
                self._say_omni()

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






def main():
    logging.basicConfig(level=logging.INFO)
    MyAssistant().start()


if __name__ == '__main__':
    main()

