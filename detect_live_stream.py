import time
import os

import speech_recognition as sr

from pydub import AudioSegment
from pydub.playback import play
import io
import pygame
from google.cloud import dialogflow


def detect_intent_stream(project_id, session_id, audio_file_path, language_code):
    """Returns the result of detect intent with streaming audio as input.

    Using the same `session_id` between requests allows continuation
    of the conversation."""

    session_client = dialogflow.SessionsClient()

    # Note: hard coding audio_encoding and sample_rate_hertz for simplicity.
    audio_encoding = dialogflow.AudioEncoding.AUDIO_ENCODING_LINEAR_16
    sample_rate_hertz = 16000

    session_path = session_client.session_path(project_id, session_id)
    print("Session path: {}\n".format(session_path))

    def request_generator(audio_config, audio_file_path, output_audio_config):
        query_input = dialogflow.QueryInput(audio_config=audio_config)
        query_input.audio_config.single_utterance = True

        # The first request contains the configuration.
        yield dialogflow.StreamingDetectIntentRequest(
            session=session_path, query_input=query_input,
            output_audio_config=output_audio_config
        )

        # Here we are reading small chunks of audio data from a local
        # audio file.  In practice these chunks should come from
        # an audio input device.
        with open(audio_file_path, 'rb') if audio_file_path else sr.Microphone(sample_rate=16000) as audio_file:
            while True:
                chunk = audio_file.read(4096) if audio_file_path else audio_file.stream.read(4096)
                if not chunk:
                    break
                # The later requests contains audio data.
                yield dialogflow.StreamingDetectIntentRequest(input_audio=chunk)

    audio_config = dialogflow.InputAudioConfig(
        audio_encoding=audio_encoding,
        language_code=language_code,
        sample_rate_hertz=sample_rate_hertz,
    )

    # Set the query parameters with sentiment analysis
    output_audio_config = dialogflow.OutputAudioConfig(
        # audio_encoding=dialogflow.OutputAudioEncoding.OUTPUT_AUDIO_ENCODING_MP3_64_KBPS
        audio_encoding=dialogflow.OutputAudioEncoding.OUTPUT_AUDIO_ENCODING_LINEAR_16
    )

    requests = request_generator(audio_config, audio_file_path, output_audio_config)
    responses = session_client.streaming_detect_intent(requests=requests)

    print("=" * 20)
    for response in responses:
        print(
            'Intermediate transcript: "{}".'.format(
                response.recognition_result.transcript
            )
        )
        if response.query_result.intent.display_name:
            print(response.query_result.intent.display_name)

    # Note: The result from the last response is the final transcript along
    # with the detected content.
    query_result = response.query_result

    print("=" * 20)
    print("Query text: {}".format(query_result.query_text))
    print(
        "Detected intent: {} (confidence: {})\n".format(
            query_result.intent.display_name, query_result.intent_detection_confidence
        )
    )
    print("Fulfillment text: {}\n".format(query_result.fulfillment_text))

    # The response's audio_content is binary.
    pygame.mixer.init()
    sound = pygame.mixer.Sound(io.BytesIO(response.output_audio))
    sound.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)


# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:/Users/Mason Z/GoogleCloud/keys/newagent-umpx-57b11a68ca3e.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:/Users/Mason Z/GoogleCloud/keys/isaac-drqa-0ea7d58d60db.json"
project_id = 'isaac-drqa'
session_id = 1234567899
# audio_file_path = 'microphone-results.raw'
audio_file_path = ''
language_code = 'en-AU'

detect_intent_stream(project_id, session_id, audio_file_path, language_code)

# import speech_recognition as sr
# import wave

# obtain audio from the microphone
# r = sr.Recognizer()
# with sr.Microphone(sample_rate=16000) as source:
#     print("Say something!")
#     r.adjust_for_ambient_noise(source, duration=0.5)
#     audio = r.listen(source, timeout=3)
#
# # write audio to a RAW file
# with open("microphone-results.raw", "wb") as f:
#     f.write(audio.get_raw_data())
