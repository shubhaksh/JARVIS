import logging
import speech_recognition as sr
import pyttsx3
import datetime
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import webbrowser
import google.generativeai as genai
from APIKeys import googleapikey
from APIKeys import weatherapikey
from APIKeys import newsapikey
from APIKeys import spclientid
from APIKeys import spclientsecret

# Initialize text-to-speech engine
engine = pyttsx3.init()

rate = engine.getProperty('rate')
engine.setProperty('rate', rate - 25)

# Spotify credentials
SPOTIPY_CLIENT_ID = spclientid
SPOTIPY_CLIENT_SECRET = spclientsecret
SPOTIPY_REDIRECT_URI = 'http://localhost:8888/callback'

# Spotify OAuth
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                               client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri=SPOTIPY_REDIRECT_URI,
                                               scope='user-modify-playback-state,user-read-playback-state'))

# Initialize the Gemini client
google_api_key = googleapikey
genai.configure(api_key=google_api_key)

# Logging setup
logging.basicConfig(level=logging.INFO)

def speak(text):
    engine.say(text)
    engine.runAndWait()

def set_voice(voice_name):
    voices = engine.getProperty('voices')
    for voice in voices:
        if voice.name == voice_name:
            engine.setProperty('voice', voice.id)
            break

def greet():
    hour = datetime.datetime.now().hour
    if 0 <= hour < 12:
        speak("Good Morning Sir!")
    elif 12 <= hour < 18:
        speak("Good Afternoon Sir!")
    else:
        speak("Good Evening Sir!")
    speak("How can I assist you today?")

def shut_down_pc():
    os.system("shutdown /s /t 1")

def restart_pc():
    os.system("shutdown /r /t 1")

def take_command():
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Listening for command...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source)
            try:
                print("Recognizing command...")
                query = recognizer.recognize_google(audio, language='en-in')
                print(f"User said: {query}\n")
                return query.lower()
            except sr.UnknownValueError:
                speak("Sir I was unable to hear")
                activate_jarvis()
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")
                activate_jarvis()
    except OSError as e:
        print(f"Could not access microphone; {e}")

def get_weather():
    api_key = weatherapikey
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    city_name = "DehraDun"
    complete_url = base_url + "appid=" + api_key + "&q=" + city_name
    response = requests.get(complete_url)
    data = response.json()

    if data["cod"] != "404":
        main = data["main"]
        weather = data["weather"][0]
        temperature = main["temp"] - 273.15  # Convert Kelvin to Celsius
        humidity = main["humidity"]
        description = weather["description"]
        weather_report = f"The temperature is {temperature:.2f} degrees Celsius, humidity is {humidity} percent, and the weather description is {description}."
        return weather_report
    else:
        return "City Not Found."

def activate_jarvis():
    while True:
        recognizer = sr.Recognizer()
        try:
            with sr.Microphone() as source:
                print("Say 'Jarvis' to activate...")
                recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = recognizer.listen(source)
                try:
                    trigger_word = recognizer.recognize_google(audio, language='en-in')
                    if "jarvis" in trigger_word.lower():
                        speak("Listening Sir.")
                        command_mode()
                except sr.UnknownValueError:
                    pass
                except sr.RequestError as e:
                    print(f"Could not request results from Google Speech Recognition service; {e}")
        except OSError as e:
            print(f"Could not access microphone; {e}")

def get_latest_news():
    api_key = newsapikey
    base_url = "http://newsapi.org/v2/top-headlines?country=us&apiKey=" + api_key
    response = requests.get(base_url)
    data = response.json()

    if data["status"] == "ok":
        articles = data["articles"]
        top_articles = articles[:5]
        news_report = "Here are the top 5 news headlines: "
        for i, article in enumerate(top_articles):
            news_report += f"Headline {i+1}: {article['title']}. "
        return news_report
    else:
        return "I couldn't fetch the news at the moment."
    
conversation_history = ""
def get_google_response(query):
    try:
        global conversation_history
        conversation_history += f"Shubhaksh: {query}\nJarvis: "
        
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(conversation_history)
        reply = response.text.strip()
        conversation_history += f"{reply}\n"
        return reply
    
    except Exception as e:
        return f"Problem: {e}"

def command_mode():
    query = take_command()
    if query is None:
        return

    if 'current time' in query:
        strTime = datetime.datetime.now().strftime("%H:%M:%S")
        speak(f"The current time is {strTime} sir")

    elif 'current date' in query:
        currentDate = datetime.datetime.now().strftime("%A, %B %d, %Y")
        speak(f"Today is {currentDate} sir")

    elif 'weather' in query:
        weather_report = get_weather()
        speak("Telling Sir")
        speak(weather_report)

    elif 'google' in query:
        speak("Opening Sir")
        webbrowser.open("https://www.google.com")

    elif 'youtube' in query:
        speak("What do you want to search for, sir?")
        searchyt = take_command()
        if 'nothing' in searchyt:
            speak("Okay, sir. Opening Youtube.")
            webbrowser.open("https://www.youtube.com")
        else:
            speak("Okay, sir. Opening Youtube.")
            webbrowser.open(f"https://www.youtube.com/results?search_query={searchyt}")

    elif 'meet' in query:
        speak("Opening Sir")
        webbrowser.open("https://meet.google.com")

    elif 'whatsapp' in query:
        speak("Opening Sir")
        webbrowser.open("https://web.whatsapp.com")

    elif 'classroom' in query:
        speak("Opening Sir")
        webbrowser.open("https://classroom.google.com/u/0/c/NTE4NDIwMDE2NjMy")

    elif 'chat gpt' in query:
        speak("Opening Sir")
        webbrowser.open("https://www.chatgpt.com")
    
    elif 'github' in query:
        speak("Opening Sir")
        webbrowser.open("https://github.com/shubhaksh")
    
    elif 'gmail' in query:
        speak("Opening Sir")
        webbrowser.open("https://mail.google.com")
        
    elif 'instagram' in query:
        speak('Opening Sir')
        webbrowser.open("https://instagram.com")
    
    elif 'chrome' in query:
        speak("Opening Sir")
        os.system('"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"')

    elif 'search for' in query:
        query = query.replace("search for", "")
        webbrowser.open(f"https://www.google.com/search?q={query}")

    elif 'notepad' in query:
        speak("Opening Sir")
        os.system('notepad.exe')
        
    elif 'explorer' in query:
        speak("Opening Sir")
        os.system('explorer.exe')

    elif 'shut down' in query or 'shutdown' in query:
        speak("Shutting Down your system.")
        shut_down_pc()

    elif 'restart' in query:
        speak("Restarting your system.")
        restart_pc()

    elif 'avengers age of ultron' in query:
        speak("Starting Sir")
        os.system("F:/Movies/Marvel/Avengers/Avengers_Age_Of_Ultron.mp4")

    elif 'avengers infinity war' in query:
        speak("Starting Sir")
        os.system("F:/Movies/Marvel/Avengers/Avengers_Infinity_War.mp4")

    elif 'avengers end game' in query:
        speak("Starting Sir")
        os.system("F:/Movies/Marvel/Avengers/Avengers_Endgame.mp4")
    
    elif 'captain america civil war' in query:
        speak("Starting Sir")
        os.system("F:/Movies/Marvel/Captain_America/Captain_America_Civil_War.mp4")
    
    elif 'jc' in query:
        speak("Starting Sir")
        os.system("F:/Movies/Julius_Caesar.mp4")

    elif '12th fail' in query:
        speak("Starting Sir")
        os.system("F:/Movies/12th_Fail.mp4")

    elif 'music' in query:
        speak("What would you like to hear?")
        song = take_command()
        if song:
            results = sp.search(q=song, limit=1)
            if results['tracks']['items']:
                track = results['tracks']['items'][0]
                sp.start_playback(uris=[track['uri']])
                speak(f"Playing {track['name']} by {track['artists'][0]['name']} on Spotify.")
            else:
                speak("I couldn't find the song on Spotify.")

    elif 'news' in query:
        news_report = get_latest_news()
        speak(news_report)

    elif 'reset my conversation history' in query:
        global conversation_history
        conversation_history = ""
        speak("Conversation history has been reset.")

    elif 'show my conversation history' in query:
        print(f"\n {conversation_history}")
        speak("Here is your conversation history.")

    else:
        while True:
            if 'exit' in query:
                speak("Talk to you later, bye sir!")
                break
            response = get_google_response(query)
            print(response)
            speak(response)
            query = take_command()

def start_listening():
    activate_jarvis()

if __name__ == "__main__":
    set_voice("Microsoft David Desktop - Hindi (India)")  # Set the desired voice
    greet()
    start_listening()