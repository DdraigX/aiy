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
        detector = snowboydecoder.HotwordDetector(model, sensitivity=0.5)
        #with aiy.voice.audio.get_recorder():
        while True:
                if self._can_start_conversation:
                   #self._board.led.state = Led.ON
                   detector.start(detected_callback=self._on_button_pressed,
                                  interrupt_check=lambda: not(self._can_start_conversation),
                                  sleep_time=0.03)
                   detector.terminate()
    #/added


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

#added-google
        elif event.type == EventType.ON_RECOGNIZING_SPEECH_FINISHED and event.args:
            print('You said:', event.args['text'])
            text = event.args['text'].lower()
            if text == 'power off':
                self._assistant.stop_conversation()
                power_off_pi()
            elif text == 'reboot':
                self._assistant.stop_conversation()
                reboot_pi()
            elif text == 'random':
                self._assistant.stop_conversation()
                for x in range(10):
                    randnum = random.randint(1, 101)
                aiy.voice.tts.say(randnum)
                reboot_pi()
            elif text == 'litany of ignition':
                self._assistant.stop_conversation()
                say_words()
            elif text == 'local ip':
                self._assistant.stop_conversation()
                print("localip")
                #ip_address = os.system('hostname -I')
                #print(ip_address + "derp")
                ip_address = subprocess.check_output("hostname -I | cut -d' ' -f1", shell=True)
                aiy.voice.tts.say('My IP address is %s' % ip_address.decode('utf-8'), lang="en-GB", pitch=10, speed=80)

                print("worked")
                #aiy.voice.tts.say('My IP address is %s' % ip_address.decode('utf-8'))
                #say_ip()
            elif text == 'something':
                self._assistant.stop_conversation()
                print("helloworld")
                aiy.voice.tts.say('hello', lang="en-GB", pitch=10, speed=80)
                #os.system("aplay red1.wav")
                #say_omni()
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


def say_ip():
    ip_address = subprocess.check_output("hostname -I | cut -d' ' -f1", shell=True)
    aiy.voice.tts.say('My IP address is %s' % ip_address.decode('utf-8'))

#added
    def say_omni():
        aiy.voice.tts.say('All praise the Omnissiah', lang="en-GB", pitch=10, speed=80)
        # os.system("mpg321 ignition1.mp3")
#/added


def main():
    logging.basicConfig(level=logging.INFO)
    MyAssistant().start()


if __name__ == '__main__':
    main()

