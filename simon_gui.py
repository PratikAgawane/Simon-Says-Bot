import speech_recognition as sr
import pyttsx3
import os
import random
import requests
import wikipedia
import tkinter as tk
from tkinter import scrolledtext
import threading

# === Speech Setup ===
engine = pyttsx3.init()
engine.setProperty('rate', 150)
last_spoken_text = ""

# === GUI Setup ===
root = tk.Tk()
root.title("Simon - Voice Assistant")
root.geometry("600x500")
root.configure(bg="#0f1117")

# === Header
title = tk.Label(root, text="🤖 SIMON Assistant", font=("Helvetica", 22, "bold"), bg="#0f1117", fg="#00ffe1")
title.pack(pady=10)

# === Animated Listening Label
listening_label = tk.Label(root, text="● Listening...", font=("Helvetica", 14), bg="#0f1117", fg="#0f1117")
listening_label.pack()

def animate_listening():
    current = listening_label.cget("fg")
    next_color = "#00FF99" if current == "#0f1117" else "#0f1117"
    listening_label.config(fg=next_color)
    root.after(600, animate_listening)

animate_listening()

# === Output Area
output_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=65, height=15, font=("Courier", 10),
                                        bg="#1a1c23", fg="#00FFAA", borderwidth=0)
output_area.pack(padx=10, pady=10)

# === Speak Function
def gui_speak(text):
    global last_spoken_text
    last_spoken_text = text

    def do_speak():
        engine.say(text)
        engine.runAndWait()

    output_area.insert(tk.END, f"Simon: {text}\n")
    output_area.see(tk.END)
    root.after(100, do_speak)

# === Voice Input
def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        output_area.insert(tk.END, "🎤 Listening...\n")
        output_area.see(tk.END)
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
    try:
        command = r.recognize_google(audio)
        output_area.insert(tk.END, f"You said: {command}\n")
        output_area.see(tk.END)
        return command.lower()
    except sr.UnknownValueError:
        gui_speak("Sorry, I didn't understand that.")
    except sr.RequestError:
        gui_speak("Sorry, I am having trouble with the speech service.")
    return ""

# === Weather
def get_weather(city="Mumbai"):
    gui_speak(f"Fetching weather for {city}...")
    try:
        geo_url = f"https://nominatim.openstreetmap.org/search?q={city}&format=json"
        headers = {"User-Agent": "SimonAssistant/1.0"}
        geo_response = requests.get(geo_url, headers=headers).json()
        if not geo_response:
            gui_speak("I couldn't find that city.")
            return
        lat = geo_response[0]['lat']
        lon = geo_response[0]['lon']
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        weather_response = requests.get(weather_url).json()
        temp = weather_response['current_weather']['temperature']
        windspeed = weather_response['current_weather']['windspeed']
        gui_speak(f"The temperature in {city} is {temp}°C with wind speed {windspeed} km/h.")
    except Exception as e:
        gui_speak("Sorry, I couldn't fetch the weather right now.")
        print("Weather Error:", e)

# === Wikipedia
def search_wikipedia(topic):
    try:
        gui_speak(f"Searching Wikipedia for {topic}...")
        summary = wikipedia.summary(topic, sentences=2)
        gui_speak(summary)
    except wikipedia.exceptions.DisambiguationError:
        gui_speak("That topic is too broad. Try being more specific.")
    except wikipedia.exceptions.PageError:
        gui_speak("I couldn't find anything on that topic.")
    except Exception as e:
        gui_speak("Something went wrong while searching Wikipedia.")
        print("Wiki Error:", e)

# === Music
def play_music():
    music_dir = "F:\\Music"  # 🎵 Change this path
    try:
        songs = os.listdir(music_dir)
        if songs:
            song = random.choice(songs)
            os.startfile(os.path.join(music_dir, song))
            gui_speak(f"Playing {song}")
        else:
            gui_speak("No songs found in the music folder.")
    except Exception as e:
        gui_speak("Something went wrong while trying to play music.")
        print("Music Error:", e)

# === Command Processing
def process_command(command):
    if "play music" in command:
        play_music()
    elif "weather" in command:
        if "in" in command:
            city = command.split("in")[-1].strip()
            get_weather(city)
        else:
            get_weather()
    elif "who is" in command or "what is" in command or "tell me about" in command:
        topic = command.replace("who is", "").replace("what is", "").replace("tell me about", "").strip()
        search_wikipedia(topic)
    else:
        gui_speak("I don't know how to do that yet.")

# === Core Voice Loop
def run_simon_once():
    command = listen()
    if "simon says" in command:
        real_command = command.replace("simon says", "").strip()
        if real_command:
            process_command(real_command)
        else:
            gui_speak("You didn't say any command after Simon says.")
    else:
        gui_speak("Say 'Simon says' to activate me.")

def start_listening():
    threading.Thread(target=run_simon_once).start()

def speak_again():
    if last_spoken_text:
        engine.say(last_spoken_text)
        engine.runAndWait()

# === Buttons
def create_button(text, command, color):
    return tk.Button(root, text=text, command=command, font=("Helvetica", 13), bg=color, fg="white", activebackground="#222", padx=18, pady=8, borderwidth=0)

listen_btn = create_button("🎧 Start Listening", start_listening, "#00AAFF")
listen_btn.pack(pady=8)

speak_btn = create_button("🔊 Speak Again", speak_again, "#33CC99")
speak_btn.pack(pady=5)

# === Intro
gui_speak("Hello, I am Simon. Can you hear me?")

root.mainloop()
