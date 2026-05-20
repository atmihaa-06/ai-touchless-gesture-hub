import cv2
import mediapipe as mp
import pyautogui
import math
import time
import screen_brightness_control as sbc

# Initialize tools
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)

cap = cv2.VideoCapture(0)

# Tracking variables for smooth vertical motion
prev_y = None
last_action_time = 0

print("AI Gesture Dashboard Active! Press 'q' to quit.")

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        continue

    frame = cv2.flip(frame, 1)
    h, w, c = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    current_time = time.time()

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Get key tracking points
            thumb_tip  = hand_landmarks.landmark[4]
            index_tip  = hand_landmarks.landmark[8]
            middle_tip = hand_landmarks.landmark[12]
            ring_tip   = hand_landmarks.landmark[16]
            pinky_tip  = hand_landmarks.landmark[20]
            
            # Detect if fingers are extended upwards
            index_open  = index_tip.y  < hand_landmarks.landmark[6].y
            middle_open = middle_tip.y < hand_landmarks.landmark[10].y
            ring_open   = ring_tip.y   < hand_landmarks.landmark[14].y
            pinky_open  = pinky_tip.y  < hand_landmarks.landmark[18].y

            # ----------------------------------------------------
            # GESTURE 1: SCROLL MODE (Index & Middle open - Peace Sign ✌️)
            # ----------------------------------------------------
            if index_open and middle_open and not ring_open and not pinky_open:
                current_y = int((index_tip.y + middle_tip.y) / 2 * h)
                if prev_y is not None:
                    if prev_y - current_y > 10:    # Hand moved UP
                        pyautogui.scroll(150)      
                        cv2.putText(frame, "Scrolling Up", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
                    elif current_y - prev_y > 10:  # Hand moved DOWN
                        pyautogui.scroll(-150)    
                        cv2.putText(frame, "Scrolling Down", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
                prev_y = current_y
                cv2.circle(frame, (int(index_tip.x * w), current_y), 15, (255, 255, 0), 2)

            # ----------------------------------------------------
            # GESTURE 2: NEW BRIGHTNESS MODE (Index, Middle, & Ring open - 3 Fingers 🤟)
            # ----------------------------------------------------
            elif index_open and middle_open and ring_open and not pinky_open:
                # Track the average vertical center of the 3 extended fingertips
                current_y = int((index_tip.y + middle_tip.y + ring_tip.y) / 3 * h)
                
                if prev_y is not None:
                    try:
                        # Get your current hardware brightness percentage
                        current_brightness = sbc.get_brightness()[0]
                        
                        if prev_y - current_y > 12:    # Hand moving UP -> Increase Brightness
                            new_brightness = min(current_brightness + 5, 100)
                            sbc.set_brightness(new_brightness)
                            cv2.putText(frame, f"Brightness Up: {new_brightness}%", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                        elif current_y - prev_y > 12:  # Hand moving DOWN -> Decrease Brightness
                            new_brightness = max(current_brightness - 5, 0)
                            sbc.set_brightness(new_brightness)
                            cv2.putText(frame, f"Brightness Down: {new_brightness}%", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                    except Exception as e:
                        # Fallback for some corporate monitor drivers that block direct access
                        pass
                
                prev_y = current_y
                cv2.circle(frame, (int(middle_tip.x * w), current_y), 15, (0, 255, 255), 2)

            # ----------------------------------------------------
            # GESTURE 3: PLAY / PAUSE (Open Hand / High-Five 🖐️)
            # ----------------------------------------------------
            elif index_open and middle_open and ring_open and pinky_open:
                time_passed = current_time - last_action_time
                if time_passed > 1.5:
                    pyautogui.press("space")
                    last_action_time = current_time
                    cv2.putText(frame, "TRIGGERED!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
                else:
                    cv2.putText(frame, f"Wait {1.5 - time_passed:.1f}s", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 2)
                prev_y = None

            # ----------------------------------------------------
            # GESTURE 4: GLOBAL VOLUME CONTROL (Pinch / Stretch Index & Thumb)
            # ----------------------------------------------------
            else:
                prev_y = None
                tx, ty = int(thumb_tip.x * w), int(thumb_tip.y * h)
                ix, iy = int(index_tip.x * w), int(index_tip.y * h)
                distance = math.hypot(ix - tx, iy - ty)
                
                cv2.line(frame, (tx, ty), (ix, iy), (0, 255, 0), 2)
                
                if distance < 35:
                    pyautogui.press("volumedown")
                    cv2.putText(frame, "Volume Down", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                elif distance > 140:
                    pyautogui.press("volumeup")
                    cv2.putText(frame, "Volume Up", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
    else:
        prev_y = None

    cv2.imshow('AI Hand Gesture Controller', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
hands.close()