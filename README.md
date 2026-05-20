# 🌐 AI-Powered Wireless Touchless Gesture Hub

An advanced Computer Vision and Human-Computer Interaction (HCI) system that transforms a standard webcam into an over-the-air local network automation server. By utilizing deep learning landmark models, users can seamlessly manage media control, webpage navigation, volume adjustments, and system display brightness across their local home network via a custom glassmorphism web dashboard.

---

## 🛠️ Tech Stack & Architecture

- **Core Runtime Environment:** Python 3.10
- **Computer Vision Framework:** Google MediaPipe (Hand Landmarking ML Pipeline tracking 21 key coordinate joints at 30+ FPS)
- **Image Processing Engine:** OpenCV (Real-time video matrix transformations and frame optimization)
- **Local Network Web Layer:** Streamlit (Multi-threaded backend integration utilizing custom CSS and responsive glassmorphism UI)
- **OS Automation API:** PyAutoGUI & Screen-Brightness-Control (Direct kernel-level OS event routing)

---

## 📋 Gesture Mapping Protocol

| Hand Gesture | System Trigger Command | Action Executed |
| :--- | :--- | :--- |
| 🖐️ **Open Palm** | `pyautogui.press("space")` | Play / Pause Web Media Container |
| ✌️ **Peace Sign** | `pyautogui.scroll(±150)` | Dynamic Scroll (Up / Down) based on vector delta |
| 🤏 **Thumb-Index Pinch** | `pyautogui.press("volumedown")` | Linear Volume Reduction |
| 🫲 **Thumb-Index Stretch** | `pyautogui.press("volumeup")` | Linear Volume Amplification |
| 🤟 **Three-Finger Wave** | `sbc.set_brightness()` | Hardware Backlight Manipulation |

---

## 🚀 Installation & Local Environment Setup

This project isolates its dependencies inside a dedicated virtual environment to prevent package conflicts with system-level binaries.

### 1. Recreate the Virtual Workspace
Open your Anaconda Prompt and run the following command sequence:
```bash
# Create an isolated python environment
conda create -n gesture_env python=3.10 -y

# Activate the workspace environment
conda activate gesture_env