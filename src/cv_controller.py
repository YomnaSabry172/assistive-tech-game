import cv2
import numpy as np
import pygame
import time
import mediapipe as mp
from gesture_detector import GestureDetector

USED_GESTURES = ["Open Palm", "Thumb-Pinky", "Thumb-Index", "Thumb-Ring", "Thumb-Middle"]

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
        self.hand_pos = pygame.math.Vector2(0.5, 0.5) # Normalized 0-1
        self.is_clicking = False
        self.attack = False
        self.special_attack = False
        self.landmarks = None
        self.gesture_label = "No Hand"
        
        # Combo System
        self.combo_buffer: list[str] = []
        self.last_unique_gesture: str | None = None
        self.combo_timeout: float = 1.5 # seconds
        self.combo_timer: float = 0.0
        
        # Stats
        self.stats = {
            'jumps': 0,
            'max_openness': 0.0,
            'active_time': 0.0,
            'left_moves': 0,
            'right_moves': 0,
            'range_of_motion_max': 0.0,
            'gesture_counts': {},
            'gesture_time': {},
            'timeline': []
        }
        self.last_logged_gesture = None
        
        # State
        self.surface = None
        self.was_jumping_gesture = False
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
        self.is_clicking = False
        self.attack = False

        if results.multi_hand_landmarks:
            self.stats['active_time'] += dt
            landmarks = results.multi_hand_landmarks[0].landmark
            self.landmarks = landmarks
            
            # 1. Update Hand Position (Mid-palm landmark 9)
            self.hand_pos.x = landmarks[9].x
            self.hand_pos.y = landmarks[9].y

            # 2. Detect Gesture
            self.gesture_label = self.detector.detect(landmarks)
            
            # --- MEDICAL / REHAB TRACKING STATS ---
            if self.gesture_label != "Unknown" and self.gesture_label != "No Hand":
                # Time tracking
                if self.gesture_label not in self.stats['gesture_time']:
                    self.stats['gesture_time'][self.gesture_label] = 0.0
                self.stats['gesture_time'][self.gesture_label] += dt
                
                # Hand openness (Range of motion surrogate)
                thumb_tip = np.array([landmarks[4].x, landmarks[4].y, landmarks[4].z])
                pinky_tip = np.array([landmarks[20].x, landmarks[20].y, landmarks[20].z])
                dist = np.linalg.norm(thumb_tip - pinky_tip)
                if dist > self.stats['range_of_motion_max']:
                    self.stats['range_of_motion_max'] = float(dist)

                # Event/Count tracking edge detection
                if self.gesture_label != self.last_logged_gesture:
                    if self.gesture_label not in self.stats['gesture_counts']:
                        self.stats['gesture_counts'][self.gesture_label] = 0
                    self.stats['gesture_counts'][self.gesture_label] += 1
                    
                    self.stats['timeline'].append({
                        "time": round(self.stats['active_time'], 2),
                        "gesture": self.gesture_label
                    })
                    self.last_logged_gesture = self.gesture_label

            # 3. Detect Clicking (Fist)
            self.is_clicking = (self.gesture_label == "Fist")
            
            # 3.1 Detect Attack (Knuckle Bend)
            self.attack = (self.gesture_label == "Knuckle Bend")

            # 4. Map Gesture to vertical Jump
            is_jumping_gesture = (self.gesture_label == "Open Palm")
            if is_jumping_gesture and not self.was_jumping_gesture:
                self.jump = True
                self.stats['jumps'] += 1
            self.was_jumping_gesture = is_jumping_gesture

            # 4.2. Handle Diagonal jumps
            is_jumping_gesture_r = (self.gesture_label == "Thumb-Ring")
            if is_jumping_gesture_r:
                self.jump = True
                self.direction_x = 1
            
            is_jumping_gesture_l = (self.gesture_label == "Thumb-Middle")
            if is_jumping_gesture_l:
                self.jump = True
                self.direction_x = -1

            # 5. Map position to horizontal move
            if (self.gesture_label == "Thumb-Pinky"):
                self.direction_x = 1
                self.stats['right_moves'] += 1
            elif (self.gesture_label == "Thumb-Index"):
                self.direction_x = -1
                self.stats['left_moves'] += 1

            # 6. Combo Logic (Fist -> Karate Chop)
            if self.gesture_label != self.last_unique_gesture and self.gesture_label != "Unknown":
                # New gesture detected
                if time.time() - self.combo_timer > self.combo_timeout:
                    self.combo_buffer = [] # Reset on timeout
                
                self.combo_buffer.append(self.gesture_label)
                self.combo_timer = time.time()
                self.last_unique_gesture = self.gesture_label
                
                # Check for combo
                if len(self.combo_buffer) >= 2:
                    last_two = self.combo_buffer[-2:]
                    if last_two == ["Fist", "Karate Chop"]:
                        self.special_attack = True
                        self.combo_buffer = [] # Clear after trigger

            # Debug Overlay
            color = (0, 255, 0) if self.gesture_label in USED_GESTURES else (0, 0, 255)
            cv2.putText(frame, f"Gesture: {self.gesture_label}", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            
            # Draw landmarks
            self.mp_draw.draw_landmarks(frame, results.multi_hand_landmarks[0], self.mp_hands.HAND_CONNECTIONS)

        annotated_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.surface = pygame.image.frombuffer(annotated_rgb.tobytes(), (w, h), 'RGB')

    def release(self):
        self.cap.release()
        self.hands.close()
