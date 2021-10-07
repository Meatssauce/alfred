import speech_recognition as sr
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

engine = pyttsx3.init('sapi5')  # a Microsoft Text to speech engine used for voice recognition
voices = engine.getProperty('voices')
engine.setProperty('voice', 'voices[1].id')  # 0 for male voice, 1 for female voice

wolframalpha_client_key = 'R2K75H-7ELALHR35X'
weather_error_codes = {'401', '404'}


def speak(text: str):
    engine.say(text)
    engine.runAndWait()


def wishMe():
    hour = datetime.datetime.now().hour
    if 0 <= hour < 12:
        speak("Hello, Good Morning")
        print("Hello, Good Morning")
    elif 12 <= hour < 18:
        speak("Hello, Good Afternoon")
        print("Hello, Good Afternoon")
    else:
        speak("Hello, Good Evening")
        print("Hello, Good Evening")


def takeCommand() -> str:
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)

        try:
            statement = r.recognize_google(audio, language='en-in')
            print(f"user said:{statement}\n")

        except Exception as e:
            speak("Pardon me, please say that again")
            return "None"
        return statement


def is_number(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False


print("Loading your AI personal assistant G-One")
speak("Loading your AI personal assistant G-One")
wishMe()

if __name__ == '__main__':
    while True:
        speak("Tell me how can I help you now?")
        statement = takeCommand().lower()
        if statement == 0:
            continue

        if "good bye" in statement or "ok bye" in statement or "stop" in statement:
            speak('your personal assistant G-one is shutting down,Good bye')
            print('your personal assistant G-one is shutting down,Good bye')
            break

        # Fetch comment from wikipedia
        if 'wikipedia' in statement:
            speak('Searching Wikipedia...')
            statement = statement.replace("wikipedia", "")
            results = wikipedia.summary(statement, sentences=3, auto_suggest=False)  # auto_suggest causes errors
            speak("According to Wikipedia")
            print(results)
            speak(results)

        elif 'open youtube' in statement:
            webbrowser.open_new_tab("https://www.youtube.com")
            speak("youtube is open now")
            time.sleep(5)

        elif 'open google' in statement:
            webbrowser.open_new_tab("https://www.google.com")
            speak("Google chrome is open now")
            time.sleep(5)

        elif 'open gmail' in statement:
            webbrowser.open_new_tab("https://www.gmail.com")
            speak("Google Mail is open now")
            time.sleep(5)

        elif 'time' in statement:
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            speak(f"the time is {current_time}")

        elif 'date' in statement:
            current_date = datetime.datetime.now().strftime("%m/%d/%Y")
            speak(f"the date is {current_date}")

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
            speak('I can answer to computational and geographical questions  and what question do you want to ask now')
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
