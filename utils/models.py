import datetime

import pyttsx3
import speech_recognition as sr
from interface import agent_response
from utils.modules import TerminationModule


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
#
# ai = VoiceAssistant()
# ai.speak('hi')
