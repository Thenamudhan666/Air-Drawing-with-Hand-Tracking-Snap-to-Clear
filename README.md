# Air-Drawing-with-Hand-Tracking-Snap-to-Clear
A real-time AI-powered Air Canvas that lets you draw in the air using your index finger—captured via webcam—and instantly clear the screen with a finger snap detected through your microphone.
Built using OpenCV, MediaPipe Hands, NumPy, and SoundDevice.

🚀 Features

🖐 Hand-tracking–based drawing using the index finger tip

🎤 Snap-to-clear gesture using audio detection

🧠 Real-time drawing overlay

🖼 Automatic canvas handling and cleanup logic

💻 Simple to run on any system with a webcam + microphone

⚡ Lightweight and fast (MediaPipe real-time tracking)

📂 Project Structure
├── main.py          # Main application code (hand tracking + drawing + snap detection) :contentReference[oaicite:0]{index=0}
├── requirements.txt # List of required Python libraries       :contentReference[oaicite:1]{index=1}
├── run.bat          # Windows batch file to run the app
└── README.md        # Project documentation

📦 Dependencies

Install all dependencies using:

pip install -r requirements.txt


This installs:

opencv-python
mediapipe
numpy
sounddevice


(From your requirements.txt file)

▶️ How to Run
Windows

Double-click:

run.bat


Or run manually:

python main.py

Mac/Linux

Run:

python3 main.py

🛠 How It Works
1. Hand Tracking

Uses MediaPipe Hands to detect 21 hand landmarks

Tracks landmark #8 → Index finger tip

Draws a line between consecutive index-finger positions

2. Canvas

Initializes a transparent canvas overlay

Merges webcam feed + drawing using bitwise operations

3. Snap Detection

Audio is captured using sounddevice callback

If RMS amplitude crosses a threshold → snap detected

A cooldown prevents multiple triggers

On snap → canvas is cleared instantly

🎮 Controls
Action	Description
Move index finger	Draws on screen
Snap fingers near mic	Clears the entire canvas
Q	Quit the application
🧪 Requirements

A webcam

A microphone

Python 3.7+

Windows/Mac/Linux

⭐ Future Improvements

Color selection with gestures

Eraser mode

Multi-color palette

Gesture-based UI

Save drawings to file

AI shape recognition

🤝 Contributions

Open to PRs and improvements!
Feel free to submit issues or feature requests.
