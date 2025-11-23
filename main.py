
import cv2
import mediapipe as mp
import numpy as np
import speech_recognition as sr
import threading
import math

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7,
    max_num_hands=1
)
mp_draw = mp.solutions.drawing_utils

# Global variables
command_detected = None # "clear", "circle", "square", "rectangle", "triangle", "pentagon", "hexagon"
COOLDOWN = 0
COOLDOWN_LIMIT = 20

# Speech Recognition Function (Background Thread)
def speech_listener():
    global command_detected
    recognizer = sr.Recognizer()
    
    try:
        mic = sr.Microphone()
        with mic as source:
            recognizer.adjust_for_ambient_noise(source)
            print("Voice Recognition Ready. Listening for 'Clear' or Shapes...")
            
        def callback(recognizer, audio):
            global command_detected
            try:
                text = recognizer.recognize_google(audio).lower()
                print(f"Heard: {text}")
                
                if "clear" in text:
                    command_detected = "clear"
                elif "circle" in text:
                    command_detected = "circle"
                elif "square" in text:
                    command_detected = "square"
                elif "rectangle" in text:
                    command_detected = "rectangle"
                elif "triangle" in text:
                    command_detected = "triangle"
                elif "pentagon" in text:
                    command_detected = "pentagon"
                elif "hexagon" in text:
                    command_detected = "hexagon"
            except sr.UnknownValueError:
                pass
            except sr.RequestError:
                print("Speech Service Error")

        # Start background listening
        stop_listening = recognizer.listen_in_background(mic, callback)
        return stop_listening
        
    except Exception as e:
        print(f"Error initializing speech recognition: {e}")
        return None

def draw_polygon(image, center, radius, sides, color, thickness):
    points = []
    for i in range(sides):
        angle = 2 * math.pi * i / sides - math.pi / 2 # Start from top
        x = int(center[0] + radius * math.cos(angle))
        y = int(center[1] + radius * math.sin(angle))
        points.append([x, y])
    pts = np.array(points, np.int32)
    pts = pts.reshape((-1, 1, 2))
    cv2.polylines(image, [pts], True, color, thickness)

def main():
    global command_detected, COOLDOWN
    
    # Start Speech Recognition
    stop_speech = speech_listener()

    # Open Webcam
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    cv2.namedWindow("Air Canvas", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Air Canvas", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    canvas = None
    prev_x, prev_y = 0, 0
    draw_color = (255, 0, 255) # Magenta
    brush_thickness = 5

    while True:
        success, img = cap.read()
        if not success:
            break

        img = cv2.flip(img, 1)
        if canvas is None:
            canvas = np.zeros_like(img)
        
        h, w, c = img.shape
        center_x, center_y = w // 2, h // 2 # Default center
        
        # Hand Tracking
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                index_tip = hand_landmarks.landmark[8]
                cx, cy = int(index_tip.x * w), int(index_tip.y * h)
                center_x, center_y = cx, cy # Update center to finger
                
                cv2.circle(img, (cx, cy), 10, draw_color, cv2.FILLED)

                if prev_x == 0 and prev_y == 0:
                    prev_x, prev_y = cx, cy

                cv2.line(canvas, (prev_x, prev_y), (cx, cy), draw_color, brush_thickness)
                prev_x, prev_y = cx, cy
        else:
            prev_x, prev_y = 0, 0

        # Check for Voice Commands
        if command_detected and COOLDOWN == 0:
            print(f"Executing command: {command_detected}")
            
            if command_detected == "clear":
                canvas = np.zeros_like(img)
                cv2.putText(img, "CLEARED!", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            else:
                # Shape drawing
                radius = 100
                color = (0, 255, 255) # Yellow
                
                if command_detected == "circle":
                    cv2.circle(canvas, (center_x, center_y), radius, color, 5)
                elif command_detected == "square":
                    top_left = (center_x - radius, center_y - radius)
                    bottom_right = (center_x + radius, center_y + radius)
                    cv2.rectangle(canvas, top_left, bottom_right, color, 5)
                elif command_detected == "rectangle":
                    top_left = (center_x - radius * 2, center_y - radius)
                    bottom_right = (center_x + radius * 2, center_y + radius)
                    cv2.rectangle(canvas, top_left, bottom_right, color, 5)
                elif command_detected == "triangle":
                    draw_polygon(canvas, (center_x, center_y), radius, 3, color, 5)
                elif command_detected == "pentagon":
                    draw_polygon(canvas, (center_x, center_y), radius, 5, color, 5)
                elif command_detected == "hexagon":
                    draw_polygon(canvas, (center_x, center_y), radius, 6, color, 5)
                
                cv2.putText(img, command_detected.upper() + "!", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            
            command_detected = None
            COOLDOWN = COOLDOWN_LIMIT
        
        if COOLDOWN > 0:
            COOLDOWN -= 1
            command_detected = None

        # Merge
        img_gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
        _, img_inv = cv2.threshold(img_gray, 50, 255, cv2.THRESH_BINARY_INV)
        img_inv = cv2.cvtColor(img_inv, cv2.COLOR_GRAY2BGR)
        img = cv2.bitwise_and(img, img_inv)
        img = cv2.bitwise_or(img, canvas)

        cv2.imshow("Air Canvas", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    if stop_speech:
        stop_speech(wait_for_stop=False)
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
