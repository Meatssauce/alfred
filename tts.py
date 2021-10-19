"""Synthesizes speech from the input string of text or ssml.

Note: ssml must be well-formed according to:
    https://www.w3.org/TR/speech-synthesis/
"""
import io
import os
import time

import pygame
from google.cloud import texttospeech

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:/Users/Mason Z/GoogleCloud/keys/isaac-drqa-0ea7d58d60db.json"

# Instantiates a client
client = texttospeech.TextToSpeechClient()

# Set the text input to be synthesized
synthesis_input = texttospeech.SynthesisInput(text="Sorry, there is a problem with the connection. "
                                                   "Please try again later.")

# Build the voice request, select the _language code ("en-US") and the ssml
# voice gender ("neutral")
voice = texttospeech.VoiceSelectionParams(
    language_code="en-AU", name='en-AU-Wavenet-C'
)

# Select the type of audio file you want returned
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.LINEAR16
)

# Perform the text-to-speech request on the text input with the selected
# voice parameters and audio file type
response = client.synthesize_speech(
    input=synthesis_input, voice=voice, audio_config=audio_config
)

# The response's audio_content is binary.
with open("assets/error-message.wav", "wb") as out:
    # Write the response to the output file.
    out.write(response.audio_content)
    print('Audio content written to file "ouput.wav"')

pygame.mixer.init()
pygame.mixer.Sound(io.BytesIO(response.audio_content)).play()
while pygame.mixer.get_busy():
    time.sleep(1)
