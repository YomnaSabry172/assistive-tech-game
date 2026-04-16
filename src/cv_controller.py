import cv2
import numpy as np
import pygame
import time
from hand_rehab_game import HandTracker, DIST_PARTIAL

class CVController:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.tracker = HandTracker()
        
        # Inputs returned to game
        self.direction_x = 0
        self.jump = False
        
        # State
        self.surface = None
        self.was_open = False
        
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

        # Process hand
        landmarks_list, annotated = self.tracker.process(frame)
        
        self.direction_x = 0
        self.jump = False

        h, w, _ = frame.shape

        if landmarks_list:
            self.stats['active_time'] += dt
            lm = landmarks_list[0]
            
            # Map X position to left/right
            # Palm center is landmark 9
            palm_x_norm = lm[9][0]
            
            # left zone: < 0.4, right zone: > 0.6
            if palm_x_norm < 0.4:
                self.direction_x = -1
                self.stats['left_moves'] += 1
            elif palm_x_norm > 0.6:
                self.direction_x = 1
                self.stats['right_moves'] += 1
                
            # Map openness to jump
            distances, primary_dist, openness = self.tracker.get_finger_distances(lm)
            
            if openness > self.stats['max_openness']:
                self.stats['max_openness'] = openness
            
            is_open = primary_dist > DIST_PARTIAL
            if is_open and not self.was_open:
                # Trigger jump on rising edge
                self.jump = True
                self.stats['jumps'] += 1
            self.was_open = is_open

            # Add some debugging lines to annotated
            cv2.line(annotated, (int(w*0.4), 0), (int(w*0.4), h), (0,0,255), 2)
            cv2.line(annotated, (int(w*0.6), 0), (int(w*0.6), h), (0,0,255), 2)
            
            # Show open state
            msg = "OPEN" if is_open else "CLOSED"
            color = (0, 255, 0) if is_open else (0, 0, 255)
            cv2.putText(annotated, msg, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        # Convert to pygame Surface
        annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
        self.surface = pygame.image.frombuffer(annotated_rgb.tobytes(), (w, h), 'RGB')

    def release(self):
        self.cap.release()
        self.tracker.release()
