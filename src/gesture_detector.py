import numpy as np

class GestureDetector:
    def __init__(self):
        # Distance threshold for thumb-finger touch (normalized)
        self.touch_threshold = 0.15
        # Distance threshold for fist (fingertips to wrist, normalized)
        self.fist_threshold = 0.35

    def get_distance(self, p1, p2):
        """Calculates Euclidean distance between two points."""
        return np.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2 + (p1.z - p2.z)**2)

    def get_angle(self, p1, p2, p3):
        """Calculates the angle at p2 given points p1, p2, p3."""
        v1 = np.array([p1.x - p2.x, p1.y - p2.y, p1.z - p2.z])
        v2 = np.array([p3.x - p2.x, p3.y - p2.y, p3.z - p2.z])
        
        # Avoid division by zero
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        if norm1 == 0 or norm2 == 0:
            return 0
            
        unit_v1 = v1 / norm1
        unit_v2 = v2 / norm2
        
        dot_product = np.dot(unit_v1, unit_v2)
        # Clip to avoid numerical errors with acos
        angle = np.arccos(np.clip(dot_product, -1.0, 1.0))
        return np.degrees(angle)

    def detect(self, landmarks):
        if not landmarks:
            return "Unknown"

        # 1. Normalization: Hand size (Wrist to Middle MCP)
        wrist = landmarks[0]
        middle_mcp = landmarks[9]
        hand_size = self.get_distance(wrist, middle_mcp)
        if hand_size == 0:
            return "Unknown"

        # 2. Extract key components for angles
        # Indices: [MCP, PIP, DIP]
        finger_indices = {
            "index": [5, 6, 7],
            "middle": [9, 10, 11],
            "ring": [13, 14, 15],
            "pinky": [17, 18, 19]
        }
        
        # MCP angles: [Wrist, MCP, PIP]
        mcp_indices = {
            "index": [0, 5, 6],
            "middle": [0, 9, 10],
            "ring": [0, 13, 14],
            "pinky": [0, 17, 18]
        }

        pip_angles = {name: self.get_angle(landmarks[idx[0]], landmarks[idx[1]], landmarks[idx[2]]) 
                      for name, idx in finger_indices.items()}
        
        mcp_angles = {name: self.get_angle(landmarks[idx[0]], landmarks[idx[1]], landmarks[idx[2]]) 
                       for name, idx in mcp_indices.items()}

        # 3. Detect Gestures (Priority Order)
        
        # A. Thumb to Finger Touch (Highly specific)
        thumb_tip = landmarks[4]
        finger_tips = {"Thumb-Index": 8, "Thumb-Middle": 12, "Thumb-Ring": 16, "Thumb-Pinky": 20}
        for name, tip_idx in finger_tips.items():
            dist = self.get_distance(thumb_tip, landmarks[tip_idx])
            if dist / hand_size < self.touch_threshold:
                return name

        # B. Knuckle Bend
        # PIP angles > 140 (mostly straight), MCP angles < 120 (bent)
        is_knuckle_bend = (all(angle > 140 for angle in pip_angles.values()) and 
                           all(angle < 120 for angle in mcp_angles.values()))
        if is_knuckle_bend:
            return "Knuckle Bend"

        # C. Karate Chop
        # PIP angles between 70-110
        is_karate_chop = all(70 <= angle <= 110 for angle in pip_angles.values())
        if is_karate_chop:
            return "Karate Chop"

        # D. Closed Fist
        # Robust check: A finger is folded if its tip is closer to the wrist than its MCP
        finger_pairs = [(8, 5), (12, 9), (16, 13), (20, 17)]
        folded_count = 0
        for tip_idx, mcp_idx in finger_pairs:
            dist_tip = self.get_distance(landmarks[tip_idx], wrist)
            dist_mcp = self.get_distance(landmarks[mcp_idx], wrist)
            if dist_tip < dist_mcp:
                folded_count += 1
        
        # Consider it a fist if at least 3 fingers are folded
        if folded_count >= 3:
            # Also check if thumb is somewhat folded/tucked
            # Thumb tip to index MCP distance
            thumb_folded = self.get_distance(thumb_tip, landmarks[5]) / hand_size < 1.0
            if thumb_folded:
                return "Fist"

        # E. Open Palm (The "Extended" state)
        # All fingers extended: PIP angles > 150
        all_pip_extended = all(angle > 150 for angle in pip_angles.values())
        if all_pip_extended:
            return "Open Palm"

        return "Unknown"
