import pyttsx3
import datetime
import wikipedia
import webbrowser
import os
import time
import subprocess
# from ecapture import ecapture as ec
import wolframalpha
import json
import requests
import speech_recognition as sr

from interface import agent_response

engine = pyttsx3.init('sapi5')  # a Microsoft Text to speech engine used for voice recognition
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # 0 for male voice, 1 for female voice

wolframalpha_client_key = 'R2K75H-7ELALHR35X'
weather_error_codes = {'401', '404'}
language = 'en-AU'
should_show_input = True
should_show_speech = True


def speak(text: str):
    if should_show_speech:
        print(text)
    engine.say(text)
    engine.runAndWait()


def recognize_speech_from(timeout: int = 2) -> str:
    """
    Transcribe speech from recorded from default microphone.

    :param timeout: the maximum number of seconds that this will wait for a phrase to start before giving up \
    and throwing an speech_recognition.WaitTimeoutError exception. If timeout is None, there will be no wait \
    timeout.
    :return: transcribed speech in text
    """

    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        audio = r.listen(source, timeout=timeout)
    transcript = r.recognize_google(audio, language=language)

    if should_show_input:
        print(transcript)

    return transcript


def greet_user() -> None:
    hour = datetime.datetime.now().hour

    if 0 <= hour < 12:
        speak("Good Morning")
    elif 12 <= hour < 18:
        speak("Good Afternoon")
    else:
        speak("Good Evening")


def is_number(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False


if __name__ == '__main__':
    speak("Loading your AI personal assistant G-One")
    greet_user()

    while True:
        speak("Tell me how can I help you now?")
        while True:
            try:
                statement = recognize_speech_from().lower()
                break
            except sr.WaitTimeoutError:
                speak(agent_response.WAIT_TIME_OUT_ERROR_MESSAGE)
                continue
            except sr.UnknownValueError:
                speak(agent_response.UNKNOWN_VALUE_ERROR_MESSAGE)
                continue

        if "good bye" in statement or "ok bye" in statement or "stop" in statement:
            speak('Your personal assistant G-one is shutting down. Goodbye.')
            break

        # Fetch comment from wikipedia
        if 'wikipedia' in statement:
            speak('Searching Wikipedia...')
            statement = statement.replace("wikipedia", "")
            results = wikipedia.summary(statement, sentences=3, auto_suggest=False)  # auto_suggest causes errors
            speak("According to Wikipedia")
            speak(results)

        elif 'open youtube' in statement:
            webbrowser.open_new_tab("https://www.youtube.com")
            speak("Opening Youtube...")
            time.sleep(5)

        elif 'open google' in statement:
            webbrowser.open_new_tab("https://www.google.com")
            speak("Opening browser...")
            time.sleep(5)

        elif 'open gmail' in statement:
            webbrowser.open_new_tab("https://www.gmail.com")
            speak("Opening Gmail...")
            time.sleep(5)

        elif 'time' in statement:
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            speak(f"It's {current_time}.")

        elif 'date' in statement:
            current_date = datetime.datetime.now().strftime("%m/%d/%Y")
            speak(f"It's {current_date}.")

        elif 'news' in statement:
            speak('Here are some headlines from the Times of India. Happy reading')
            news = webbrowser.open_new_tab("https://timesofindia.indiatimes.com/home/headlines")
            time.sleep(6)

        # elif "camera" in statement or "take a photo" in statement:
        #     ec.capture(0,"robo camera","img.jpg")

        elif 'search' in statement:
            statement = statement.replace("search", "")
            webbrowser.open_new_tab(statement)
            time.sleep(5)

        elif 'ask' in statement:
            speak('I can answer computational and geographical questions and what questions do you want to ask now')
            question = takeCommand()
            app_id = "Paste your unique ID here "
            client = wolframalpha.Client(wolframalpha_client_key)
            res = client.query(question)
            answer = next(res.results).text
            if answer.is_number:
                answer = f"{answer:.3f}"
            speak(answer)
            print(answer)

        elif 'who are you' in statement or 'what can you do' in statement:
            speak('I am G-one version 1 point O your personal assistant. I am programmed to minor tasks like'
                  'opening youtube, google chrome, gmail and stackoverflow, predict time, take a photo, '
                  'search wikipedia, predict weather in different cities, get top headline news from times of india '
                  'and you can ask me computational or geographical questions too!')

        elif "who made you" in statement or "who created you" in statement or "who discovered you" in statement:
            speak("I was built by Mirthula")
            print("I was built by Mirthula")

        elif "weather" in statement:
            api_key = "Apply your unique ID"
            base_url = "https://api.openweathermap.org/data/2.5/weather?"
            speak("what is the city name")
            city_name = takeCommand()
            complete_url = base_url + "appid=" + api_key + "&q=" + city_name
            response = requests.get(complete_url)
            x = response.json()
            if x["cod"] not in weather_error_codes:
                y = x["main"]
                current_temperature = y["temp"]
                current_humidity = y["humidity"]
                z = x["weather"]
                weather_description = z[0]["description"]
                speak(" Temperature in kelvin unit is " +
                      str(current_temperature) +
                      "\n humidity in percentage is " +
                      str(current_humidity) +
                      "\n description  " +
                      str(weather_description))
                print(" Temperature in kelvin unit = " +
                      str(current_temperature) +
                      "\n humidity (in percentage) = " +
                      str(current_humidity) +
                      "\n description = " +
                      str(weather_description))
