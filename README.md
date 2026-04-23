<div align="center">

<img src="assets/Main Characters/Ninja Frog/Run (32x32).png" width="64" alt="Ninja Frog"/>

# 🐸 FingerQuest

### A Gesture-Controlled Serious Game for Hand Rehabilitation

*Turn your physical therapy into an adventure. No controllers. Just your hand.*

---

[![Python](https://img.shields.io/badge/Python-3.10-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-Hands-00897B?style=for-the-badge&logo=google&logoColor=white)](https://mediapipe.dev)
[![Pygame](https://img.shields.io/badge/Pygame-2D_Engine-EF6C00?style=for-the-badge)](https://pygame.org)
[![OpenCV](https://img.shields.io/badge/OpenCV-Vision-5C3317?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

---

**SBES345 — Assistive Technology · Cairo University · Team 5**

*Malak Sherif · Hassan Badawy · Yomna Sabry · Karim Mohamed · Khadija Zakaria · Mohammed Abdelrazek*

</div>

---

## 🎬 See It In Action

> Watch a real playthrough — hand gestures controlling the game live:

[![FingerQuest Demo](https://img.shields.io/badge/▶_Watch_Demo-Google_Drive-4285F4?style=for-the-badge&logo=googledrive&logoColor=white)](https://drive.google.com/file/d/1d2iILJg3PzBocKok1DAzj06LisaGIvRy/view)

---

## 🧠 The Problem We're Solving

Arthritis affects millions of people worldwide, progressively destroying hand joints and stripping away the ability to perform simple daily tasks — holding a cup, writing, buttoning a shirt.

The prescribed treatment? **Daily Range of Motion (ROM) exercises** — repeatedly opening and closing the fingers to stretch tendons and preserve joint mobility.

The reality? **Most patients stop within days.**

The exercises are painful, repetitive, done alone at home, and offer zero feedback. There's no way to know if you're improving. There's no reason to keep going.

**FingerQuest changes that.** We didn't build a game *alongside* therapy — we built a game *where the therapy IS the game*. Every gesture you make to control the character is a prescribed rehabilitation exercise. You play. You heal. You don't even notice you're doing both.

---

## 🎮 How It Works

A standard webcam watches your hand. **MediaPipe Hands** tracks 21 3D landmarks across your fingers and palm in real time. A custom gesture classifier reads those landmarks and maps your hand shapes to in-game actions — no controller, no glove, no special hardware.

### 🤚 Gesture Controls

| Hand Gesture | In-Game Action |
|---|---|
| 🖐️ **Open Palm** | Jump |
| 🤙 **Thumb + Pinky touch** | Move Right |
| 🤏 **Thumb + Index touch** | Move Left |
| 🤘 **Thumb + Ring** | Diagonal Jump Right |
| 🖖 **Thumb + Middle** | Diagonal Jump Left |
| 👊 **Knuckle Bend** | Cast Spell (Attack) |
| ✊ **Fist → Karate Chop** | Special Attack Combo |

### 🏟️ Three Levels of Increasing Challenge

```
Level 1 — The Forest      🌲  Orientation. Learn the controls. Warm up your joints.
Level 2 — The Caverns     🪨  Faster enemies. Narrower platforms. Push your range.
Level 3 — The Gauntlet    ⚡  Dynamic hazards. Timed sequences. Full endurance test.
```

Each level demands more from your hand — more gestures, faster transitions, wider spreads — naturally escalating the therapeutic challenge without the patient ever thinking about it clinically.

---

## 📊 Rehabilitation Tracking

The game silently records every session in the background. While you're busy surviving Level 3, the system is building your rehabilitation profile:

| Metric | What It Measures |
|---|---|
| `range_of_motion_max` | Peak thumb-to-pinky spread — your ROM ceiling this session |
| `gesture_counts` | How many times each gesture was performed |
| `gesture_time` | How long you held each hand position (in seconds) |
| `active_time` | Total time your hand was on-camera and active |
| `jumps` | Number of Open Palm activations |
| `left_moves / right_moves` | Directional movement frequency |
| `timeline` | Full timestamped log of every gesture transition |

> **Clinical note:** Thumb-to-pinky spread distance (landmarks 4 → 20) is a validated proxy for finger ROM — the same metric physiotherapists measure with a goniometer in clinic. We measure it automatically, every session, without the patient doing anything extra.

---

## 🔬 Technical Architecture

```
Webcam Feed
    │
    ▼
OpenCV (frame capture + mirror)
    │
    ▼
MediaPipe Hands (21 landmark detection @ ~30fps)
    │
    ▼
GestureDetector (angle analysis + distance thresholding)
    │           │
    │           └── PIP/MCP joint angles → finger curl/extension
    │           └── Normalized inter-landmark distances → touch detection
    │           └── Fist folding check → closed hand state
    │
    ▼
CVController (gesture → game input mapping + stats tracking)
    │
    ▼
Pygame Game Engine (rendering, physics, animation, audio)
```

**Two-method gesture classification:**
- **Angle-based** — PIP and MCP joint angles computed from landmark triplets identify finger curl and extension states
- **Distance-based** — distances normalized to wrist-to-middle-MCP hand size, making detection scale-invariant across different hand sizes and camera distances

---

## 🗂️ Project Structure

```
assistive-tech-game/
│
├── src/
│   ├── main.py              # Entry point
│   ├── game.py              # Core game loop, level setup, scoring
│   ├── player.py            # Ninja Frog physics, animation, spell casting
│   ├── cv_controller.py     # Webcam pipeline, MediaPipe, stats tracking
│   ├── gesture_detector.py  # Angle + distance gesture classification
│   ├── sprites.py           # All game objects (tiles, enemies, fruits, traps)
│   ├── levels.py            # Level map definitions
│   └── settings.py          # Game constants and configuration
│
├── assets/
│   ├── Main Characters/     # Ninja Frog sprite sheets
│   ├── Terrain/             # Platform tiles
│   ├── Items/               # Fruits, boxes, checkpoints
│   ├── Traps/               # Spikes, saws, fire, falling platforms
│   ├── handGestures/        # Gesture reference images
│   ├── Menu/                # UI buttons and level previews
│   └── soundtracks/         # Background music and SFX
│
└── requirements.txt
```

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.10+
- A working webcam
- Good lighting (affects gesture detection accuracy)

### Install

```bash
# Clone the repository
git clone https://github.com/YomnaSabry172/assistive-tech-game-
cd assistive-tech-game-

# Install dependencies
pip install -r requirements.txt
```

### Run

```bash
cd src
python main.py
```

### Dependencies

```
pygame
mediapipe
opencv-python
numpy
```

---

## 💡 Tips for Best Experience

- 🌟 **Lighting matters** — play in a well-lit room with your hand clearly visible
- 📏 **Distance** — keep your hand ~40–60cm from the camera
- ✋ **Use one hand** — the system tracks a single hand; keep the other out of frame
- 🔄 **Warm up** — spend 30 seconds in Level 1 getting familiar with gesture detection before pushing into Level 3
- 🩺 **For patients** — rest between sessions; the goal is gradual ROM improvement, not speed

---

## 📚 Research Foundation

This project is grounded in peer-reviewed research on game-based hand rehabilitation:

1. **[Hand Gestures for Controlling Video Games in a Rehabilitation Exergame System](https://www.mdpi.com/2073-431X/14/1/25)**
   *Computers, MDPI — January 2025*
   Foundation for our gesture-to-game-control mapping using MediaPipe.

2. **[A VR Serious Game for Rehabilitation of Hand and Finger Function](https://pmc.ncbi.nlm.nih.gov/articles/PMC11387912/)**
   *JMIR Serious Games — August 2024*
   Clinical evidence that gamification improves patient adherence and outcomes.

3. **[ReHAb Playground: A DL-Based Framework for Game-Based Hand Rehabilitation](https://www.mdpi.com/1999-5903/17/11/522)**
   *Future Internet, MDPI — November 2025*
   Validates the MediaPipe Hands + game engine technical stack for rehabilitation.

---

## 👥 Team 5 — Cairo University

| Name | GitHub |
|---|---|
| Malak Sherif | — |
| Hassan Badawy | — |
| Yomna Sabry | [@YomnaSabry172](https://github.com/YomnaSabry172) |
| Karim Mohamed | [@Karim-Mohamed-Elsayed](https://github.com/Karim-Mohamed-Elsayed) |
| Khadija Zakaria | — |
| Mohammed Abdelrazek | — |

**Course:** SBES345 Assistive Technology
**Institution:** Faculty of Engineering, Cairo University
**Year:** 2026

---

## 📄 License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

*Built with 🐸 and a webcam. No controllers harmed in the making of this game.*

**[▶ Watch the Demo](https://drive.google.com/file/d/1d2iILJg3PzBocKok1DAzj06LisaGIvRy/view)**

</div>
