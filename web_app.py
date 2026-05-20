import streamlit as st
import cv2
import pyautogui
import math
import time
import screen_brightness_control as sbc
from cvzone.HandTrackingModule import HandDetector

# 1. Page Configuration
st.set_page_config(page_title="AI Gesture Hub", page_icon="🌐", layout="centered")

# 2. Injecting Your Custom Color Palette via CSS
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #741D2D 0%, #A4798E 50%, #4D648D 100%);
        color: #FFFFFF !important;
    }
    h1, h2, h3, p, label, .stMarkdown {
        color: #FFFFFF !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .status-card {
        background: rgba(255, 255, 255, 0.12);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 25px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.2);
        margin: 20px 0px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }
    [data-testid="stSidebar"] {
        background-color: rgba(116, 29, 45, 0.4) !important;
        backdrop-filter: blur(15px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
    .sidebar-list {
        padding-left: 0px;
        font-family: 'Segoe UI', sans-serif;
    }
    .sidebar-item {
        padding: 10px 0px;
        font-size: 15px;
        line-height: 1.4;
    }
    .stCheckbox label {
        font-size: 18px !important;
        font-weight: 600 !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🌐 AI Touchless Gesture Hub")
st.markdown("##### Wireless Over-the-Air Control Panel")

# Persistent state management
if "tracking_on" not in st.session_state:
    st.session_state.tracking_on = False

# Sidebar layout
st.sidebar.header("📋 Gesture Command Map")
st.sidebar.markdown("<hr style='border-color: rgba(255,255,255,0.2)'>", unsafe_allow_html=True)

sidebar_html = """
<div class="sidebar-list">
    <div class="sidebar-item">🖐️ <b>Open Palm:</b> Play / Pause Media</div>
    <div class="sidebar-item">✌️ <b>Peace Sign:</b> Scroll Web Page</div>
    <div class="sidebar-item">🤏 <b>Finger Pinch:</b> Volume Down</div>
    <div class="sidebar-item">🫲 <b>Finger Stretch:</b> Volume Up</div>
    <div class="sidebar-item">🤟 <b>3-Finger Wave:</b> Brightness Adjust</div>
</div>
"""
st.sidebar.markdown(sidebar_html, unsafe_allow_html=True)

# Master Activation Checkbox
toggle = st.checkbox("🔌 Activate AI Camera Engine", value=st.session_state.tracking_on)
st.session_state.tracking_on = toggle

# Dynamic UI Placeholders
status_placeholder = st.empty()
video_placeholder = st.empty()

# Run Engine Live directly if toggled on
if st.session_state.tracking_on:
    # Initialize optimized cvzone detector engine
    detector = HandDetector(maxHands=1, detectionCon=0.7)
    cap = cv2.VideoCapture(0)
    
    prev_y = None
    last_action_time = 0

    while st.session_state.tracking_on and cap.isOpened():
        success, frame = cap.read()
        if not success:
            status_placeholder.error("Error: Could not connect to webcam hardware layer.")
            break

        frame = cv2.flip(frame, 1)
        
        # This scans the hands and draws the skeletal lines flawlessly via the fresh environment modules
        hands, frame = detector.findHands(frame, draw=True, flipType=False)
        current_time = time.time()
        
        status_text = "System Online • Listening for Gestures... ⚡"

        if hands:
            hand = hands[0]
            lmList = hand["lmList"]  # The 21 standard coordinate map landmarks
            fingers = detector.fingersUp(hand)  # Binary checklist array of finger states [thumb, index, middle, ring, pinky]
            h, w, _ = frame.shape

            # 1. SCROLL (Index & Middle fingers open)
            if fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0 and fingers[4] == 0:
                current_y = int((lmList[8][1] + lmList[12][1]) / 2)
                if prev_y is not None:
                    if prev_y - current_y > 10:
                        pyautogui.scroll(150)
                        status_text = "Action: Scrolling Page Up ✌️"
                    elif current_y - prev_y > 10:
                        pyautogui.scroll(-150)
                        status_text = "Action: Scrolling Page Down ✌️"
                prev_y = current_y

            # 2. BRIGHTNESS (Index, Middle, & Ring open)
            elif fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 0:
                current_y = int((lmList[8][1] + lmList[12][1] + lmList[16][1]) / 3)
                if prev_y is not None:
                    try:
                        cb = sbc.get_brightness()[0]
                        if prev_y - current_y > 12: 
                            sbc.set_brightness(min(cb + 5, 100))
                            status_text = f"Action: Brightness Up ({min(cb+5,100)}%) 🤟"
                        elif current_y - prev_y > 12: 
                            sbc.set_brightness(max(cb - 5, 0))
                            status_text = f"Action: Brightness Down ({max(cb-5,0)}%) 🤟"
                    except: pass
                prev_y = current_y

            # 3. PLAY/PAUSE (Full open palm)
            elif fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 1:
                if current_time - last_action_time > 1.5:
                    pyautogui.press("space")
                    last_action_time = current_time
                    status_text = "Action: Toggle Play/Pause 🖐️"
                else:
                    status_text = f"Media Command Cooldown... ({1.5 - (current_time - last_action_time):.1f}s)"
                prev_y = None

            # 4. VOLUME (Dynamic Pinch Tracking)
            else:
                prev_y = None
                # Measure physical screen pixel distance between index tip (8) and thumb tip (4)
                length, info, frame = detector.findDistance(lmList[4][:2], lmList[8][:2], frame)
                if length < 35: 
                    pyautogui.press("volumedown")
                    status_text = "Action: Volume Down 🤏"
                elif length > 140: 
                    pyautogui.press("volumeup")
                    status_text = "Action: Volume Up 🫲"
        else:
            prev_y = None
            status_text = "System Online • No Hand Detected Camera Scanning... 👀"

        # Update HUD Display Card cleanly
        status_placeholder.markdown(f"""
            <div class='status-card'>
                <h4 style='margin:0; color:rgba(255,255,255,0.7) !important; font-size:14px; letter-spacing:1px;'>LIVE TRACKING HUD</h4>
                <h2 style='margin:10px 0 0 0; font-weight:bold; font-size:24px;'>{status_text}</h2>
            </div>
        """, unsafe_allow_html=True)
        
        view_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        video_placeholder.image(view_frame, channels="RGB", use_container_width=True)
        
        time.sleep(0.01)

    cap.release()
    video_placeholder.empty()
else:
    status_placeholder.markdown("""
        <div class='status-card'>
            <h4 style='margin:0; color:rgba(255,255,255,0.7) !important; font-size:14px; letter-spacing:1px;'>LIVE TRACKING HUD</h4>
            <h2 style='margin:10px 0 0 0; font-weight:bold; font-size:24px;'>System Offline • Ready to Connect</h2>
        </div>
    """, unsafe_allow_html=True)