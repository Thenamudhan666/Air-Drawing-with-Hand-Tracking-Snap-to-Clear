import cv2
import mediapipe as mp
import numpy as np
import sounddevice as sd
import threading

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7,
    max_num_hands=1
)
mp_draw = mp.solutions.drawing_utils

# Global variables for snap detection
snap_detected = False
SNAP_THRESHOLD = 3.0  # Adjusted based on user feedback
COOLDOWN = 0
COOLDOWN_LIMIT = 20 # Frames to wait after a snap

def audio_callback(indata, frames, time, status):
    global snap_detected
    if status:
        print(status)
    
    # Calculate volume (RMS amplitude)
    volume_norm = np.linalg.norm(indata) * 10
    
    # Simple threshold check
    if volume_norm > SNAP_THRESHOLD:
        snap_detected = True

def main():
    global snap_detected, COOLDOWN
    
    # Start Audio Stream
    try:
        stream = sd.InputStream(callback=audio_callback)
        stream.start()
        print("Audio stream started. Listening for snaps...")
    except Exception as e:
        print(f"Error starting audio stream: {e}")
        return

    # Open Webcam
    cap = cv2.VideoCapture(0)
    
    # Set resolution to Full HD (1920x1080)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    print("Webcam opened. Press 'q' to exit.")
    
    # Create a named window and set to full screen
    cv2.namedWindow("Air Canvas", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Air Canvas", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # Drawing variables
    canvas = None
    prev_x, prev_y = 0, 0
    draw_color = (255, 0, 255) # Magenta
    brush_thickness = 5

    while True:
        success, img = cap.read()
        if not success:
            print("Failed to read frame.")
            break

        # Flip the image horizontally
        img = cv2.flip(img, 1)
        
        # Initialize canvas if needed
        if canvas is None:
            canvas = np.zeros_like(img)

        # Check for snap to clear
        if snap_detected and COOLDOWN == 0:
            print("Snap detected! Clearing canvas.")
            canvas = np.zeros_like(img)
            snap_detected = False
            COOLDOWN = COOLDOWN_LIMIT
            cv2.putText(img, "CLEARED!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        if COOLDOWN > 0:
            COOLDOWN -= 1
            # Force snap_detected to False during cooldown to prevent double clears
            snap_detected = False

        # Convert to RGB for MediaPipe
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Process
        results = hands.process(img_rgb)
        
        # Check for hands
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw landmarks
                mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                # Get index finger tip (Landmark 8)
                h, w, c = img.shape
                index_tip = hand_landmarks.landmark[8]
                cx, cy = int(index_tip.x * w), int(index_tip.y * h)
                
                # Draw circle at tip
                cv2.circle(img, (cx, cy), 10, draw_color, cv2.FILLED)

                # Drawing Logic
                if prev_x == 0 and prev_y == 0:
                    prev_x, prev_y = cx, cy

                cv2.line(canvas, (prev_x, prev_y), (cx, cy), draw_color, brush_thickness)
                prev_x, prev_y = cx, cy
        else:
            prev_x, prev_y = 0, 0

        # Merge canvas and image
        img_gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
        _, img_inv = cv2.threshold(img_gray, 50, 255, cv2.THRESH_BINARY_INV)
        img_inv = cv2.cvtColor(img_inv, cv2.COLOR_GRAY2BGR)
        img = cv2.bitwise_and(img, img_inv)
        img = cv2.bitwise_or(img, canvas)

        # Display
        cv2.imshow("Air Canvas", img)

        # Exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    stream.stop()
    stream.close()
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
