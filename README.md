Jarvis AI – Your Personal Voice Assistant (Iron Man Style)
License: MIT
Python
Groq
A beautiful, fast, and fully functional desktop assistant built in pure Python. Just say “Jarvis” and take control of your PC with natural voice or text commands.
Jarvis AI in action
Features

Hotword activation — say “Jarvis” anywhere, it wakes up instantly
Real-time voice recognition with cool animated mic bars
Groq + Llama-3.1-8B instant AI chat (super fast & free tier friendly)
Smart built-in commands:
→ open youtube · play perfect by ed sheeran · search for python tutorials
→ what’s the time · date · calculate 48 × 27
Custom commands — teach it to launch any app or website
→ launch spotify · launch obsidian · launch my project
Live CPU & RAM monitor in the UI
Sleek dark-mode interface (CustomTkinter)
Optional auto-start on Windows boot
100% open source & easy to extend

Tech Stack

Python 3.9+

CustomTkinter – modern GUI

SpeechRecognition + PyAudio

Groq API (Llama-3.1-8B-Instant)

psutil – system monitoring

Quick Start
Bashgit clone https://github.com/UmairA1i/jarvis-ai.git
cd jarvis-ai
pip install -r requirements.txt

# Set your Groq API key (get free at https://console.groq.com)
setx GROQ_API_KEY "gsk_your_key_here"        # Windows
export GROQ_API_KEY="gsk_..."             # macOS / Linux

python jarvis.py
Say “Jarvis” or click the mic button → become Tony Stark for a minute.
Screenshots
Chat view
Custom commands
Roadmap

Offline mode with Ollama / Whisper.cpp
Multi-language voice support
Desktop notifications & reminders
Smart home / IoT integration

Made with passion by Umair © 2025
Inspired by Tony Stark, built for everyday superheroes.
Star this repo if you ever wanted your own JARVIS
Contributions, ideas, and bug reports are very welcome!
License: MIT – feel free to fork, modify, and show the world your version.
