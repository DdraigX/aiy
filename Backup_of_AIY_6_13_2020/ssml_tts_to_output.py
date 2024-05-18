#!/usr/bin/env python

# Copyright 2018 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Google Cloud Text-To-Speech API sample application .
Example usage:
    python synthesize_file.py --text resources/hello.txt
    python synthesize_file.py --ssml resources/hello.ssml
"""

import argparse
import os
import pygame
import time

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/pi/cloud_tts.json"
from pygame import mixer
pygame.init()
pygame.mixer.init()


#ssml_file = 'speech.ssml'

# [START tts_synthesize_ssml_file]
def synthesize_ssml_file(ssml_file):
    """Synthesizes speech from the input file of ssml.
    Note: ssml must be well-formed according to:
        https://www.w3.org/TR/speech-synthesis/
    """
    from google.cloud import texttospeech
    client = texttospeech.TextToSpeechClient()

    with open(ssml_file, 'r') as f:
        ssml = f.read()
        input_text = texttospeech.types.SynthesisInput(ssml=ssml)

    # Note: the voice can also be specified by name.
    # Names of voices can be retrieved with client.list_voices().
    voice = texttospeech.types.VoiceSelectionParams(
        language_code='en-US',name='en-US-Standard-B',
        ssml_gender=texttospeech.enums.SsmlVoiceGender.MALE)


    audio_config = texttospeech.types.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.MP3)

    response = client.synthesize_speech(input_text, voice, audio_config)

    # The response's audio_content is binary.
    with open('output.mp3', 'wb') as out:
        out.write(response.audio_content)
        print('Audio content written to file "output.mp3"')
        time.sleep(1)
        #sound = mixer.Sound('/home/pi/AIY-projects-python/src/examples/voice/output.mp3')
        #print("length",sound.get_length())
        #print("pos",mixer.music.get_pos())
        #len = sound.get_length() - mixer.music.get_pos()
        #print("len",len)
        #os.system("mpg321 output.mp3")
        #sound.play()
      # sound.wait()
        #time.sleep(3)
# [END tts_synthesize_ssml_file]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--text',
                       help='The text file from which to synthesize speech.')
    group.add_argument('--ssml',
                       help='The ssml file from which to synthesize speech.')

    args = parser.parse_args()

    if args.text:
        synthesize_text_file(args.text)
    else:
        synthesize_ssml_file(args.ssml)
