import datetime
import os
import time
import io
import re
import logging
import uuid
import pygame

import pyttsx3
import speech_recognition as sr

from interface import agent_response
from utils.modules import TerminationModule

from google.cloud import dialogflow, texttospeech
from google.auth.exceptions import GoogleAuthError
from google.api_core.exceptions import GoogleAPIError


class VoiceAssistant:
    def __init__(self, language: str = 'en-AU', engine: str = 'sapi5', voice: int = 0, show_input=True,
                 show_response=True):
        self.language = language
        self.engine = pyttsx3.init(engine)  # 'sapi5' a Microsoft Text to speech engine used for voice recognition
        self.engine.setProperty('voice', self.engine.getProperty('voices')[voice].id)  # 0 for male, 1 for female
        self.should_show_input = show_input
        self.should_show_response = show_response
        self.modules = {TerminationModule(self)}

    def speak(self, text: str):
        if self.should_show_response:
            print(text)
        self.engine.say(text)
        self.engine.runAndWait()

    def recognize_speech(self, timeout: int = 2) -> str:
        """
        Transcribe speech from recorded from default microphone.

        :param timeout: the maximum number of seconds that this will wait for a phrase to start before giving up \
        and throwing an speech_recognition.WaitTimeoutError exception. If timeout is None, there will be no wait \
        timeout.
        :return: transcribed speech in text
        """

        r = sr.Recognizer()
        while True:
            try:
                with sr.Microphone() as source:
                    r.adjust_for_ambient_noise(source, duration=0.5)
                    audio = r.listen(source, timeout=timeout)
                transcript = r.recognize_google(audio, language=self.language)
                break
            except sr.WaitTimeoutError:
                self.speak(agent_response.WAIT_TIME_OUT_ERROR_MESSAGE)
            except sr.UnknownValueError:
                self.speak(agent_response.UNKNOWN_VALUE_ERROR_MESSAGE)

        if self.should_show_input:
            print(transcript)

        return transcript

    def greet_user(self) -> None:
        hour = datetime.datetime.now().hour
        if 0 <= hour < 12:
            self.speak("Hello, Good Morning")
        elif 12 <= hour < 18:
            self.speak("Hello, Good Afternoon")
        else:
            self.speak("Hello, Good Evening")

    def run(self) -> None:
        self.speak(agent_response.ON_RUN_START)
        self.greet_user()

        self.speak(agent_response.ASK_COMMAND)
        try:
            input_text = self.recognize_speech()
        except sr.RequestError:
            self.speak(agent_response.REQUEST_ERROR_MESSAGE)
            return

        for module in self.modules:
            if module.activate(input_text):
                return

    def exit(self) -> None:
        raise NotImplementedError
        pass


class DialogFlowVoiceAssistant:
    def __init__(self, project_id: str or int, key_path: str):
        self._project_id = project_id
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_path
        self._language = 'en-AU'
        self._voice_name = 'en-AU-Wavenet-C'
        self._sample_rate_hertz = 16000
        self._session_id = None
        self._time_at_last_response_seconds = time.time()

    @staticmethod
    def _play(audio):
        pygame.mixer.Sound(io.BytesIO(audio)).play()
        while pygame.mixer.get_busy():
            time.sleep(0.1)

    def _text_to_speech(self, text):
        client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(language_code=self._language, name=self._voice_name)
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.LINEAR16)
        response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
        return response.audio_content

    def speak(self, text: str):
        self._play(self._text_to_speech(text))

    def boot(self) -> None:
        pygame.mixer.init()

        # self.greet_user()
        self.listen()

    def listen(self, ask_back: bool = True) -> None:
        # def root_equals(intent, other):
        #     # Check if intent requires any action
        #
        #     try:
        #         root = re.findall(r'^\w+', intent)[0]
        #         other_root = re.findall(r'^\w+', other)[0]
        #     except IndexError:
        #         return False
        #     else:
        #         return root.lower() == other_root.lower()

        # start new session if not already in one or it's been more than 3 minutes since the last response
        if not self._session_id or time.time() - self._time_at_last_response_seconds > 3 * 60:
            self._session_id = uuid.uuid4()

        try:
            detection_result, audio_response = self._detect_intent_stream()
        except (GoogleAPIError, GoogleAuthError) as e:
            # log error and play error message
            logging.error(e, e)
            with open('../assets/error-message.wav', 'rb') as f:
                self._play(f.read())
        else:
            if detection_result.intent.is_fallback:
                if ask_back:
                    self._play(audio_response)
                    self.listen(ask_back=False)
                else:
                    self.speak("Sorry, I'm not sure I understand.")

            elif re.match(r'^(smalltalk|jokes|easteregg)\.', detection_result.intent.display_name):
                self._play(audio_response)

            # elif root_equals(detection_result.intent.display_name, 'date'):
            #     tell the weather

            elif detection_result.intent.display_name == 'conversation.end':
                self._play(audio_response)

            if detection_result.intent.end_interaction:
                self._session_id = None

    @staticmethod
    def _handle_intermediate_transcript(transcript):
        print(transcript, end='\r')

    def _detect_intent_stream(self):
        """Returns the result of detect intent with streaming audio as input.

        Using the same `_session_id` between requests allows continuation
        of the conversation."""
        def generate_request():
            # The first request contains the configuration.
            yield dialogflow.StreamingDetectIntentRequest(
                session=session_path,
                query_input=dialogflow.QueryInput(audio_config=audio_config),
                output_audio_config=output_audio_config
            )

            # The later requests contains audio data from microphone
            with sr.Microphone(sample_rate=audio_config.sample_rate_hertz) as audio_source:
                while chunk := audio_source.stream.read(4096):
                    yield dialogflow.StreamingDetectIntentRequest(input_audio=chunk)

        session_client = dialogflow.SessionsClient()

        session_path = session_client.session_path(self._project_id, self._session_id)
        logging.info(f"Session path: {session_path}\n")

        audio_config = dialogflow.InputAudioConfig(
            audio_encoding=dialogflow.AudioEncoding.AUDIO_ENCODING_LINEAR_16,
            language_code=self._language,
            sample_rate_hertz=self._sample_rate_hertz,
            single_utterance=True
        )
        voice = dialogflow.VoiceSelectionParams(name=self._voice_name)
        output_audio_config = dialogflow.OutputAudioConfig(
            # audio_encoding=dialogflow.OutputAudioEncoding.OUTPUT_AUDIO_ENCODING_MP3_64_KBPS
            audio_encoding=dialogflow.OutputAudioEncoding.OUTPUT_AUDIO_ENCODING_LINEAR_16,
            synthesize_speech_config=dialogflow.SynthesizeSpeechConfig(voice=voice)
        )

        responses = session_client.streaming_detect_intent(requests=generate_request())
        query_result = response = None
        for response in responses:
            self._handle_intermediate_transcript(response.recognition_result.transcript)
            if response.query_result.intent.display_name:
                query_result = response.query_result

        return query_result, response.output_audio


key_path = "C:/Users/Mason Z/GoogleCloud/keys/isaac-drqa-0ea7d58d60db.json"
project_id = 'isaac-drqa'
agent = DialogFlowVoiceAssistant(project_id, key_path)
agent.boot()
# ai = VoiceAssistant()
# ai.speak('hi')
