# ======================================================
#  IMPORTS, HELPERS & FEATURES
# ======================================================
import os
import datetime
import webbrowser
import requests
import threading
import speech_recognition as sr
import customtkinter as ctk
import sys
import json
import random
import psutil


listening_flag = False  # global flag for mic animation

def animate_bars():
    for bar in bars:
        height = random.randint(5, 30)
        bar.configure(height=height)
    if listening_flag:  # only animate while listening
        app.after(100, animate_bars)  # repeat every 100ms


# ======================================================
#  VOICE INPUT 
# ======================================================
def listen():
    global listening_flag
    listening_flag = True
    animate_bars()  # start animation

    r = sr.Recognizer()
    with sr.Microphone() as source:
        status_label.configure(text="🎙️ Listening...")
        r.pause_threshold = 1
        audio = r.listen(source, phrase_time_limit=7)

    listening_flag = False  # stop animation
    for bar in bars:  # reset bars to default height
        bar.configure(height=5)

    try:
        status_label.configure(text="Recognizing...")
        query = r.recognize_google(audio, language="en-US")
        status_label.configure(text=f"You said: {query}")

        insert_user_message(query)
        execute_command(query.lower())

    except sr.UnknownValueError:
        status_label.configure(text="Sorry, I didn’t understand that.")
    except sr.RequestError:
        status_label.configure(text="Speech recognition unavailable.")
    except Exception as e:
        status_label.configure(text=f"Mic error: {e}")


# ======================================================
#  AI (GROQ) 
# ======================================================
chat_history = [{"role": "system", "content": "You are Jarvis, a helpful AI assistant."}]


def get_ai_response(prompt):
    try:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            insert_bot_message("No Groq API key found. Please set it first.")
            return

        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        chat_history.append({"role": "user", "content": prompt})
        data = {"model": "llama-3.1-8b-instant", "messages": chat_history}

        response = requests.post(url, headers=headers, json=data, timeout=15)
        if response.status_code == 200:
            ai_reply = response.json()["choices"][0]["message"]["content"]
            chat_history.append({"role": "assistant", "content": ai_reply})
            insert_bot_message(ai_reply)
        else:
            insert_bot_message(f"AI Error: {response.status_code}")

    except requests.exceptions.Timeout:
        insert_bot_message("AI took too long to respond.")
    except Exception as e:
        insert_bot_message(f"AI connection error: {e}")



# ======================================================
#  CHAT MESSAGE HELPERS 
# ======================================================
def insert_user_message(text):
    chat_log.insert("end", f"🧑 Umair:\n", "user_name")
    chat_log.insert("end", f"{text}\n\n", "user_message")
    chat_log.see("end")


def insert_bot_message(text):
    chat_log.insert("end", f"🤖 Jarvis:\n", "bot_name")
    chat_log.insert("end", f"{text}\n\n", "bot_message")
    chat_log.see("end")


# ======================================================
#  WEBSITE OPENER ("open ___")
# Only opens websites / searches. NEVER launches apps.
# ======================================================
def smart_open_website(query):
    """
    Handles:
    - 'open youtube'
    - 'open google images'
    - 'open python docs'
    - 'open example.com'
    - 'open stackoverflow'
    """
    site = query.replace("open", "", 1).strip()

    if not site:
        return "What website should I open?"

    # If user provided a domain
    if "." in site:
        if not site.startswith("http"):
            site = "https://" + site
        webbrowser.open(site)
        return f"Opening {site}"

    # Known direct mappings
    known_sites = {
        "youtube": "https://youtube.com",
        "google": "https://google.com",
        "facebook": "https://facebook.com",
        "instagram": "https://instagram.com",
        "whatsapp": "https://web.whatsapp.com",
        "github": "https://github.com",
        "stackoverflow": "https://stackoverflow.com",
        "reddit": "https://reddit.com",
        "twitter": "https://x.com",
        "x": "https://x.com",
        "maps": "https://maps.google.com"
    }

    key = site.lower().strip()
    # direct match
    if key in known_sites:
        webbrowser.open(known_sites[key])
        return f"Opening {key}"

    # If it contains words (e.g., "python docs") -> search Google
    search_query = key.replace(" ", "+")
    google_search_url = f"https://www.google.com/search?q={search_query}"
    webbrowser.open(google_search_url)
    return f"Searching for: {site}"


# ======================================================
#  SMART SEARCH ("search ..." or "search for ...")
# ======================================================
def smart_search(query):
    search_text = (
        query.replace("search for", "", 1)
             .replace("search", "", 1)
             .strip()
    )

    if not search_text:
        return "What should I search for?"

    url = f"https://www.google.com/search?q={search_text.replace(' ', '+')}"
    webbrowser.open(url)
    return f"Searching for: {search_text}"


# ======================================================
#  YOUTUBE VIDEO OPENER ("play ...")
# Opens YouTube search results page for the query.
# ======================================================
def play_youtube_video(query):
    video_name = query.replace("play", "", 1).strip()
    if not video_name:
        return "What video do you want me to play?"

    url = f"https://www.youtube.com/results?search_query={video_name.replace(' ', '+')}"
    webbrowser.open(url)
    return f"Playing on YouTube: {video_name}"


# ======================================================
#  CUSTOM COMMANDS FEATURE (load/save/add)
# custom_commands maps trigger_phrase -> action (URL or app path)
# ======================================================
CUSTOM_COMMANDS_FILE = "custom_commands.json"


def load_custom_commands():
    if os.path.exists(CUSTOM_COMMANDS_FILE):
        try:
            with open(CUSTOM_COMMANDS_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_custom_commands(commands):
    try:
        with open(CUSTOM_COMMANDS_FILE, "w") as f:
            json.dump(commands, f, indent=4)
    except Exception as e:
        print("Error saving custom commands:", e)


custom_commands = load_custom_commands()


def add_custom_command(phrase, action):
    phrase = phrase.lower().strip()
    custom_commands[phrase] = action
    save_custom_commands(custom_commands)
    insert_bot_message(f"Custom command added: '{phrase}' → {action}")


def open_custom_command_window():
    popup = ctk.CTkToplevel(app)
    popup.title("Add Custom Command")
    popup.geometry("400x300")

    label1 = ctk.CTkLabel(popup, text="Trigger phrase (without 'launch'):")
    label1.pack(pady=5)
    phrase_entry = ctk.CTkEntry(popup, width=300)
    phrase_entry.pack(pady=5)

    label2 = ctk.CTkLabel(popup, text="Action (URL or full App Path):")
    label2.pack(pady=5)
    action_entry = ctk.CTkEntry(popup, width=300)
    action_entry.pack(pady=5)

    def save_cmd():
        phrase = phrase_entry.get().strip().lower()
        action = action_entry.get().strip()
        if phrase and action:
            add_custom_command(phrase, action)
            popup.destroy()

    save_btn = ctk.CTkButton(popup, text="Save Command", command=save_cmd)
    save_btn.pack(pady=20)


# ======================================================
#  OPTIMIZED COMMAND ROUTER 
# ======================================================
def execute_command(query):
    query = query.strip()

    # 1️⃣ CUSTOM COMMANDS — Triggered by "launch <phrase>"
    if query.startswith("launch "):
        # phrase = everything after "launch "
        phrase = query.replace("launch ", "", 1).strip().lower()
        # direct custom command match
        if phrase in custom_commands:
            action = custom_commands[phrase]
            try:
                if action.startswith("http"):
                    webbrowser.open(action)
                else:
                    # try starting a file/program path
                    try:
                        os.startfile(action)
                    except Exception:
                        # fallback: try to open as URL
                        webbrowser.open(action)
                insert_bot_message(f"Launching: {phrase}")
            except Exception as e:
                insert_bot_message(f"Failed to launch: {e}")
            return
        else:
            # If not a saved custom command, attempt to launch as app/file path directly
            try:
                os.startfile(phrase)
                insert_bot_message(f"Launching {phrase}")
            except Exception:
                insert_bot_message("I couldn't find that launch command.")
            return

    # Smart Search: "search ..." or "search for ..."
    if query.startswith("search") or query.startswith("search for"):
        response = smart_search(query)
        insert_bot_message(response)
        return

    #  Play YouTube videos: "play ..."
    if query.startswith("play "):
        response = play_youtube_video(query)
        insert_bot_message(response)
        return

    # Website Opener: "open ..."
    if query.startswith("open "):
        response = smart_open_website(query)
        insert_bot_message(response)
        return

    #  Built-in quick commands (time, date, calculate, exit)
    if "time" == query or query.startswith("time "):
        insert_bot_message(f"The time is {datetime.datetime.now().strftime('%I:%M %p')}")
        return

    if "date" == query or query.startswith("date "):
        insert_bot_message(f"Today is {datetime.datetime.now().strftime('%A, %B %d, %Y')}")
        return

    if query.startswith("calculate"):
        try:
            expression = query.replace("calculate", "", 1).strip()
            result = eval(expression)
            insert_bot_message(f"The answer is {result}.")
        except Exception:
            insert_bot_message("Sorry, I couldn’t calculate that.")
        return

    if any(word == query or query.startswith(word + " ") for word in ["stop", "exit", "quit", "close"]):
        insert_bot_message("Goodbye, boss.")
        try:
            app.destroy()
        except:
            pass
        return

    #  Fallback to AI
    get_ai_response(query)


# ======================================================
#  USER INTERFACE (UI)
# ======================================================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Jarvis AI Assistant")
app.geometry("900x650")

# Title
title_label = ctk.CTkLabel(app, text="🤖 Jarvis AI Assistant", font=("Arial", 26, "bold"))
title_label.pack(pady=15)

# Chat Frame
chat_frame = ctk.CTkFrame(app, width=760, height=450)
chat_frame.pack(padx=10, pady=10)

chat_log = ctk.CTkTextbox(chat_frame, width=740, height=430, wrap="word", font=("Consolas", 14))
chat_log.pack(padx=10, pady=10)

chat_log.tag_config("user_name", foreground="#00FF7F", justify="right")
chat_log.tag_config("bot_name", foreground="#1E90FF", justify="left")
chat_log.tag_config("user_message", foreground="#FFFFFF", justify="right")
chat_log.tag_config("bot_message", foreground="#E0E0E0", justify="left")
chat_log.tag_config("normal_text", foreground="#FFFFFF")

chat_log.insert("end", "🤖 Jarvis:\n", "bot_name")
chat_log.insert("end", "Hello Umair. I'm online and ready to assist!\n\n", "bot_message")

# Input Area
input_frame = ctk.CTkFrame(app)
input_frame.pack(pady=10)

entry = ctk.CTkEntry(input_frame, placeholder_text="Type your message here...", width=500, height=40)
entry.pack(side="left", padx=10)



    # ----------------------------
    # Voice Activity Bar Frame
    # ----------------------------
activity_frame = ctk.CTkFrame(app, width=200, height=30)
activity_frame.pack(pady=5)

bars = []
for i in range(5):  # 5 small bars
    bar = ctk.CTkLabel(activity_frame, text="", width=20, height=30, fg_color="#1E90FF")
    bar.pack(side="left", padx=2)
    bars.append(bar)


    # ----------------------------
    # System Resource Monitor
    # ----------------------------
resource_frame = ctk.CTkFrame(app, width=300, height=50)
resource_frame.pack(pady=5)

cpu_label = ctk.CTkLabel(resource_frame, text="CPU: 0%", font=("Arial", 12))
cpu_label.pack(side="left", padx=10)

ram_label = ctk.CTkLabel(resource_frame, text="RAM: 0%", font=("Arial", 12))
ram_label.pack(side="left", padx=10)



def send_message():
    user_input = entry.get()
    if not user_input.strip():
        return
    insert_user_message(user_input)
    entry.delete(0, "end")
    threading.Thread(target=lambda: execute_command(user_input.lower()), daemon=True).start()


send_button = ctk.CTkButton(input_frame, text="Send", width=100, command=send_message)
send_button.pack(side="left", padx=5)

mic_button = ctk.CTkButton(input_frame, text="🎙️ Speak", width=100, command=lambda: threading.Thread(target=listen, daemon=True).start())
mic_button.pack(side="left", padx=5)

custom_button = ctk.CTkButton(input_frame, text="⚙ Custom Commands", width=150,
                              command=open_custom_command_window)
custom_button.pack(side="left", padx=5)

status_label = ctk.CTkLabel(app, text="Ready.", font=("Arial", 12))
status_label.pack(pady=10)


# ======================================================
#  OPEN ON STARTUP
# ======================================================
def enable_startup():
    try:
        startup_dir = os.path.join(
            os.getenv("APPDATA"),
            "Microsoft\\Windows\\Start Menu\\Programs\\Startup"
        )
        script_path = os.path.abspath(sys.argv[0])
        bat_path = os.path.join(startup_dir, "JarvisStartup.bat")

        with open(bat_path, "w") as f:
            f.write(f'start "" "{script_path}"')

        print("Jarvis will launch on startup.")

    except Exception as e:
        print(f"Startup Error: {e}")


threading.Thread(target=enable_startup, daemon=True).start()


# ======================================================
#  HOTWORD DETECTION (“jarvis”) — background non-blocking
# ======================================================
_bg_stop_listening = None


def _hotword_callback(recognizer, audio):
    try:
        spoken = recognizer.recognize_google(audio, language="en-US").lower()
        print(f"[hotword] heard: {spoken}")
    except sr.UnknownValueError:
        return
    except sr.RequestError as e:
        print(f"[hotword] SR request error: {e}")
        return
    except Exception as e:
        print(f"[hotword] unexpected error: {e}")
        return

    if "jarvis" in spoken:
        try:
            try:
                status_label.configure(text="Hotword detected! Listening...")
            except Exception:
                pass
            threading.Thread(target=listen, daemon=True).start()
        except Exception as e:
            print(f"[hotword] failed to start listen(): {e}")


def start_hotword_detection():
    global _bg_stop_listening

    r = sr.Recognizer()
    r.dynamic_energy_threshold = True
    r.energy_threshold = 400

    try:
        mic = sr.Microphone()
    except Exception as e:
        print(f"[hotword] Microphone error: {e}")
        return

    try:
        with mic as source:
            print("[hotword] Calibrating for ambient noise (1s)...")
            r.adjust_for_ambient_noise(source, duration=1)
    except Exception as e:
        print(f"[hotword] ambient noise calibration failed: {e}")

    try:
        _bg_stop_listening = r.listen_in_background(mic, _hotword_callback, phrase_time_limit=3)
        print("[hotword] Background hotword listener started.")
    except Exception as e:
        print(f"[hotword] Failed to start background listener: {e}")


threading.Thread(target=start_hotword_detection, daemon=True).start()


#=================================
#  FUNCTION FOR CPU AND RAM USAGE
#=================================
def update_resources():
    cpu_percent = psutil.cpu_percent()
    ram_percent = psutil.virtual_memory().percent

    cpu_label.configure(text=f"CPU: {cpu_percent}%")
    ram_label.configure(text=f"RAM: {ram_percent}%")

    app.after(1000, update_resources)  # update every 1 second

update_resources()  # start the monitor


# ======================================================
# RUN THE APP
# ======================================================
app.mainloop()