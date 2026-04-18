import cv2
import numpy as np
import pygame
import time
import mediapipe as mp
from gesture_detector import GestureDetector

USED_GESTURES = ["Open-Palm", "Thumb-Pinky", "Thumb-Index"]

class CVController:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Initialize MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # Initialize Gesture Detector
        self.detector = GestureDetector()
        
        # Inputs returned to game
        self.direction_x = 0
        self.jump = False
        self.gesture_label = "Unknown"
        
        # State
        self.surface = None
        self.was_jumping_gesture = False
        
        # Stats
        self.stats = {
            'jumps': 0,
            'max_openness': 0.0,
            'active_time': 0.0,
            'left_moves': 0,
            'right_moves': 0
        }
        self.start_time = time.time()
        self.last_frame_time = self.start_time

    def process_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        now = time.time()
        dt = now - self.last_frame_time
        self.last_frame_time = now
        
        frame = cv2.flip(frame, 1) # Mirror
        h, w, _ = frame.shape

        # Convert the BGR image to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame with MediaPipe Hands
        results = self.hands.process(rgb_frame)
        
        self.direction_x = 0
        self.jump = False
        self.gesture_label = "No Hand"

        if results.multi_hand_landmarks:
            self.stats['active_time'] += dt
            hand_landmarks = results.multi_hand_landmarks[0]
            
            # 1. Draw landmarks
            self.mp_draw.draw_landmarks(
                frame, 
                hand_landmarks, 
                self.mp_hands.HAND_CONNECTIONS,
                self.mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=4),
                self.mp_draw.DrawingSpec(color=(0, 0, 255), thickness=2)
            )

            # 2. Extract Landmarks for Detector
            landmarks = hand_landmarks.landmark
            
            # 3. Detect Gesture
            self.gesture_label = self.detector.detect(landmarks)
            
            # 4. Map Gesture to vertical Jump
            # Using "Open Palm" as jump trigger
            is_jumping_gesture = (self.gesture_label == "Open Palm")
            if is_jumping_gesture and not self.was_jumping_gesture:
                self.jump = True
                self.stats['jumps'] += 1
            self.was_jumping_gesture = is_jumping_gesture

            # 4.2. Handle Diagonal jumps
            is_jumping_gesture = (self.gesture_label == "Thumb-Ring")
            if is_jumping_gesture and not self.was_jumping_gesture:
                self.jump = True
                self.direction_x = 1
                self.stats['right_moves'] +=1
                self.stats['jumps'] += 1
            self.was_jumping_gesture = is_jumping_gesture

            is_jumping_gesture = (self.gesture_label == "Thumb-Middle")
            if is_jumping_gesture and not self.was_jumping_gesture:
                self.jump = True
                self.direction_x = -1
                self.stats['left_moves'] +=1
                self.stats['jumps'] += 1
            self.was_jumping_gesture = is_jumping_gesture

            # 5. Map Position to direction_x
            # Palm center (landmark 9: Middle Finger MCP)

            # palm_x_norm = landmarks[9].x
            
            # # Left zone: < 0.4, Right zone: > 0.6
            # if palm_x_norm < 0.4:
            #     self.direction_x = -1
            #     self.stats['left_moves'] += 1
            # elif palm_x_norm > 0.6:
            #     self.direction_x = 1
            #     self.stats['right_moves'] += 1

            # 5.2. Map position to right
            if (self.gesture_label == "Thumb-Pinky"):
                self.direction_x = 1
                self.stats['right_moves'] += 1
            elif (self.gesture_label == "Thumb-Index"):
                self.direction_x = -1
                self.stats['left_moves'] += 1

            # Debug Overlay on frame
            cv2.line(frame, (int(w*0.4), 0), (int(w*0.4), h), (255, 255, 255), 1)
            cv2.line(frame, (int(w*0.6), 0), (int(w*0.6), h), (255, 255, 255), 1)
            
            # color = (0, 255, 0) if is_jumping_gesture else (0, 0, 255)
            color = (0, 255, 0) if self.gesture_label in USED_GESTURES else (0, 0, 255)
            cv2.putText(frame, f"Gesture: {self.gesture_label}", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        # Convert to pygame Surface
        annotated_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.surface = pygame.image.frombuffer(annotated_rgb.tobytes(), (w, h), 'RGB')

    def release(self):
        self.cap.release()
        self.hands.close()
