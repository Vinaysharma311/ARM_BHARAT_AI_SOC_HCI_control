import time
import cv2        #importing all libraries needed
import mediapipe as mp 
import pyautogui as pg
import numpy as np 
import math

# import pulsectl          # pip install pulsectl
pg.FAILSAFE = False
mp_hands = mp.solutions.hands  
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands( min_detection_confidence = 0.7,
                       min_tracking_confidence = 0.7  ,
                       max_num_hands = 1  , 
                        )

cap = cv2.VideoCapture(0) # 0 means the first webcame option available
add = "http://10.26.148.130:4000/video"
cap.open(add)
screen_width ,  screen_height  = pg.size()
screen_width += 100 
screen_height += 100
# XY coordinates have 0, 0 origin at top left corner of the screen. X increases going right, Y increases going down.

#  variables
pinch_count = 0
screenshot_taken = False
last_play_pause_time = 0
PLAY_COOLDOWN_SECONDS = 1.5         # 1.5 se shuru karo, agar spam ho to 2.0–2.5 kar dena
previous_peace_state = False  
thumbh_extended =0  # yeh line bahut zaroori hai – bahar daalni hai

# volume ke variables 

if not cap.isOpened():
    print("Error: Camera nahi khul raha hai!")
    exit()



while cap.isOpened():
     ret, frame = cap.read()
     frame = cv2.flip(frame , 1 )
     coordinates = str(pg.position())
     if not ret:
            break
     h,w ,c = frame.shape     #height , width and color channel is saved in respective variables 
     rgb_frame = cv2.cvtColor(frame , cv2.COLOR_BGR2RGB)
     results = hands.process(rgb_frame) 
     cv2.putText(frame,coordinates,(10, 70), cv2.FONT_HERSHEY_PLAIN , 1 ,(0,255, 255, 0), 2) 
    
     if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks :
            index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            index_finger_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]
            thumb_tip = hand_landmarks.landmark[4]
            ring_finger_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_MCP]
            ring_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
            pinky_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
            pinky_finger_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP]
            mid_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
            mid_finger_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP] 
            landmarks = hand_landmarks.landmark
            x_i = int(index_finger_tip.x * w)
            y_i = int(index_finger_tip.y * h)  

            x_p_t = int (pinky_finger_tip.x * w)
            y_p_t = int( pinky_finger_tip.y * h)

            x_p_m = int(pinky_finger_mcp.x * w)
            y_p_m = int(pinky_finger_mcp.y * h) 

            x_r_m = int(ring_finger_mcp.x * w)
            y_r_m = int(ring_finger_mcp.y * h)

            x_r_t = int(ring_finger_tip.x * w)
            x_r_t = int(ring_finger_tip.y * h)

            x_i_m = int(index_finger_mcp.x * w)
            y_i_m = int(index_finger_mcp.y * h)


            
            pinky_tip_mcp = math.hypot(ring_finger_mcp.x - ring_finger_tip.x , ring_finger_mcp.y - ring_finger_tip.y)
            ring_tip_mcp = math.hypot(pinky_finger_mcp.x - pinky_finger_tip.x , pinky_finger_mcp.y - pinky_finger_tip.y) 
            thumbh_tip_index_mcp = math.hypot(index_finger_mcp.x - thumb_tip.x, index_finger_mcp.y - index_finger_mcp.y)
            index_tip_mcp = math.hypot(index_finger_mcp.x - index_finger_tip.x, index_finger_mcp.y - index_finger_tip.y)
            middle_tip_mcp = math.hypot(mid_finger_mcp.x - mid_finger_tip.x, mid_finger_mcp.y - mid_finger_tip.y )
            index_tip_middle_tip = math.hypot(index_finger_tip.x - mid_finger_tip.x , index_finger_tip.y - mid_finger_tip.y )



            #it returns the pixels value of the screen matlab screen kr pixels ke beech ka distance
            screen_x = np.interp(x_i , [0,w], [0,screen_width])
            screen_y = np.interp(y_i , [0,h], [0,screen_height])
            mp_drawing.draw_landmarks(frame , hand_landmarks , mp_hands.HAND_CONNECTIONS) #draws the landmarks on frame 
            
            fingers = [
                1 if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip-2].y else 0 
                for tip in [8, 12 , 16 , 20 ]
                ]
            
        ####### NEXT / PREVIOUS (Media keys - right side open palm) #######

        right_threshold = 0.58          # ≈ right 42% of screen – adjust if needed
        next_prev_mode = False

        # Cooldown variables (define outside loop if not already present)
        try:
            last_np_time      # already exists? → good
        except NameError:
            last_np_time = 0
        NP_COOLDOWN = 1              # seconds between presses

        if sum(fingers) == 4 and index_finger_tip.x >= right_threshold:
            next_prev_mode = True

        if next_prev_mode:
            y_norm = index_finger_tip.y     # 0.0 = top, 1.0 = bottom

            TOP_ZONE    = 0.30
            BOTTOM_ZONE = 0.70              # bottom starts from 70% → last 30%

            current_time = time.time()

            if current_time - last_np_time >= NP_COOLDOWN:
                action_taken = False

                if y_norm <= TOP_ZONE:
                    pg.press('n')
                    last_np_time = current_time
                    action_taken = True
                    feedback_text = "NEXT (N)"
                    feedback_color = (0, 220, 100)     # green
                    arrow = "→→"

                elif y_norm >= BOTTOM_ZONE:
                    pg.press('p')
                    last_np_time = current_time
                    action_taken = True
                    feedback_text = "PREV (P)"
                    feedback_color = (100, 150, 255)   # blue
                    arrow = "←←"

                if action_taken:
                    cv2.putText(frame, f"{feedback_text} {arrow}",
                                (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.9, feedback_color, 2)
                    
                    # Small circle at index fingertip + label
                tip_x = int(index_finger_tip.x * w)
                tip_y = int(index_finger_tip.y * h)
                cv2.circle(frame, (tip_x, tip_y), 9, (0, 255, 180), 2)
                cv2.putText(frame, f"N/P", (tip_x+12, tip_y-8),
                            cv2.FONT_HERSHEY_PLAIN, 1.0, (0, 255, 180), 1)

            # Visual feedback - always show when mode active
            # Right side boundary line
            line_x = int(w * right_threshold)
            cv2.line(frame, (line_x, 0), (line_x, h), (0, 140, 255), 2)   # orange line

            # Zone guides (optional but very helpful)
            cv2.line(frame, (line_x, int(h*TOP_ZONE)),    (w, int(h*TOP_ZONE)),    (0,255,120), 1)
            cv2.line(frame, (line_x, int(h*BOTTOM_ZONE)), (w, int(h*BOTTOM_ZONE)), (0,255,120), 1)

            # Mode title
            cv2.putText(frame, "NEXT/PREV MODE ACTIVE",
                        (10, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 220, 100), 2)

            # Show current hand Y position as percentage
            y_percent = int(y_norm * 100)
            zone_text = "TOP zone" if y_norm <= TOP_ZONE else "BOTTOM zone" if y_norm >= BOTTOM_ZONE else "middle"
            cv2.putText(frame, f"Y: {y_percent}%  ({zone_text})",
                        (10, 115), cv2.FONT_HERSHEY_PLAIN, 1.1, (200, 220, 255), 1)

        else:
            # Optional: dimmed hint when hand is close to right edge but not fully in
            if sum(fingers) == 4 and index_finger_tip.x >= 0.45:
                cv2.putText(frame, "Move right → NEXT/PREV",
                            (10, 50), cv2.FONT_HERSHEY_PLAIN, 0.9, (160,160,160), 1)
                

            ####### VOLUME CONTROL (Left side open palm - up/down arrows) #######

        left_threshold = 0.20          # ≈ left 20% of screen – adjust if needed
        volume_mode = False

        # Cooldown variables (define outside loop if not already present)
        try:
            last_vol_time      # already exists? → good
        except NameError:
            last_vol_time = 0
        VOL_COOLDOWN = 0.7               # seconds between presses – smaller for faster response, but smoother with 0.7-1.0

        if sum(fingers) == 4 and index_finger_tip.x <= left_threshold:
            volume_mode = True

        if volume_mode:
            y_norm = index_finger_tip.y     # 0.0 = top, 1.0 = bottom

            TOP_ZONE    = 0.30              # top 30% for volume UP
            BOTTOM_ZONE = 0.70              # bottom 30% for volume DOWN

            current_time = time.time()

            if current_time - last_vol_time >= VOL_COOLDOWN:
                action_taken = False

                if y_norm <= TOP_ZONE:
                    pg.press('up')              # volume up
                    last_vol_time = current_time
                    action_taken = True
                    feedback_text = "VOL UP ↑"
                    feedback_color = (0, 220, 100)     # green

                elif y_norm >= BOTTOM_ZONE:
                    pg.press('down')            # volume down
                    last_vol_time = current_time
                    action_taken = True
                    feedback_text = "VOL DOWN ↓"
                    feedback_color = (100, 150, 255)   # blue-ish

                if action_taken:
                    cv2.putText(frame, feedback_text,
                                (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, feedback_color, 2)

            # Visual feedback - always show when mode active
            # Left side boundary line
            line_x = int(w * left_threshold)
            cv2.line(frame, (line_x, 0), (line_x, h), (0, 140, 255), 2)   # orange line

            # Zone guides (horizontal lines for top/bottom zones)
            cv2.line(frame, (0, int(h*TOP_ZONE)),    (line_x, int(h*TOP_ZONE)),    (0,255,120), 1)
            cv2.line(frame, (0, int(h*BOTTOM_ZONE)), (line_x, int(h*BOTTOM_ZONE)), (0,255,120), 1)

            # Mode title
            cv2.putText(frame, "VOLUME MODE ACTIVE",
                        (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 220, 100), 2)

            # Show current hand Y position as percentage
            y_percent = int(y_norm * 100)
            zone_text = "UP zone" if y_norm <= TOP_ZONE else "DOWN zone" if y_norm >= BOTTOM_ZONE else "middle"
            cv2.putText(frame, f"Y: {y_percent}%  ({zone_text})",
                        (10, 160), cv2.FONT_HERSHEY_PLAIN, 1.1, (200, 220, 255), 1)

            # Semi-transparent box (like your original volume code)
            overlay = frame.copy()
            box_left   = 0
            box_top    = 0
            box_right  = line_x
            box_bottom = h
            cv2.rectangle(overlay, (box_left, box_top), (box_right, box_bottom), (100, 50, 150), -1)  # dark purple-red
            alpha = 0.25
            cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
            cv2.rectangle(frame, (box_left, box_top), (box_right, box_bottom), (255, 100, 100), 3)  # bright border

            # Optional: small circle at index fingertip + label (similar to N/P)
            tip_x = int(index_finger_tip.x * w)
            tip_y = int(index_finger_tip.y * h)
            cv2.circle(frame, (tip_x, tip_y), 9, (0, 255, 180), 2)
            cv2.putText(frame, "VOL", (tip_x + 12, tip_y - 8),
                        cv2.FONT_HERSHEY_PLAIN, 1.0, (0, 255, 180), 1)

        else:
            # Optional: dimmed hint when hand is close to left edge but not fully in
            if sum(fingers) == 4 and index_finger_tip.x <= 0.35:
                cv2.putText(frame, "Move left → VOLUME",
                            (10, 130), cv2.FONT_HERSHEY_PLAIN, 0.9, (160,160,160), 1)


            ########## 10 SECONDS FORWARD ###########

            # Get wrist position (origin/reference point)
            wrist_x = landmarks[0].x
            wrist_y = landmarks[0].y

            # Helper function to calculate Euclidean distance (normalized coordinates)
            def dist_to_wrist(lm_id):
                tip_x = landmarks[lm_id].x
                tip_y = landmarks[lm_id].y
                return math.hypot(tip_x - wrist_x, tip_y - wrist_y)

            # 1. Thumb must be extended → thumb tip FAR from wrist
            thumb_tip_dist = dist_to_wrist(4)          # landmark 4 = THUMB_TIP
            if thumb_tip_dist > 0.18 :
             thumbh_extended = thumb_tip_dist     # adjust this threshold (0.18–0.28 typical)

             # 2. Other 4 fingers must be curled → their tips CLOSE to wrist
             folded_threshold = 0.25                   # adjust: 0.12–0.18 common (smaller = stricter)

             fingers_curled = True
             for tip_id in [8, 12, 16, 20]:             # index_tip, middle_tip, ring_tip, pinky_tip
                d = dist_to_wrist(tip_id)
                if d > folded_threshold:
                    fingers_curled = False
                    break

             # Optional extra check: thumb should be somewhat "up/sideways" relative to palm
             # (helps avoid false positives when fist + thumb slightly out)
             thumb_ip_dist   = dist_to_wrist(3)         # THUMB_IP
             thumb_mcp_dist  = dist_to_wrist(2)         # THUMB_MCP
             thumb_sideways_ok = thumb_tip_dist > thumb_ip_dist + 0.03   # tip farther than IP

             # Final condition
            is_thumbs_up = thumbh_extended and fingers_curled # and thumb_sideways_ok

            # Handedness helps if you want stricter sideways check (optional)
            if results.multi_handedness:
                handedness = results.multi_handedness[0].classification[0].label
                # You can add: if Right hand → thumb x should be left of index_mcp_x, etc.
                # But distance-to-wrist often works without it

            if is_thumbs_up:
                thumbUP = True
                # cv2.putText(frame, "THUMBS UP ", (50, 100),
                #             cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 100), 4)
                            
                # Optional: show distances for tuning
                # cv2.putText(frame, f"Thumb dist: {thumb_tip_dist:.2f}", (50, 140), ...)

                if thumbUP :
                    if thumb_tip.x > 0.65 :
                     pg.hotkey( 'alt ', 'right')
                     cv2.putText(frame, " 10sec ++ ", (50, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 100), 4)
                
                    if thumb_tip.x < 0.35:
                     pg.hotkey('alt' , 'left')
                     cv2.putText(frame, "10 sec-- ", (50, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 100), 4)




            fingers = [
                1 if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip-2].y else 0 
                for tip in [8, 12 , 16 , 20 ]
             ]
            last_play_pause_time = 0          # last time space press hua tha
            COOLDOWN_SECONDS = 1.2
            index_extended = landmarks[8].y < landmarks[6].y - 0.02   # index tip PIP se upar
            middle_extended = landmarks[12].y < landmarks[10].y - 0.02
            ring_curled   = landmarks[16].y > landmarks[14].y + 0.01
            pinky_curled  = landmarks[20].y > landmarks[18].y + 0.01
            thumb_curled  = landmarks[4].y > landmarks[3].y + 0.02



            # Yeh line sahi hai (pixels mein)
            idx_x = int(index_finger_tip.x * w)
            idx_y = int(index_finger_tip.y * h)
            mid_x = int(mid_finger_tip.x * w)
            mid_y = int(mid_finger_tip.y * h)

            finger_dist = math.hypot(idx_x - mid_x, idx_y - mid_y)
            if index_extended and middle_extended and ring_curled and pinky_curled:
             peace_sign_active = True
             cv2.putText(frame, "PEACE SIGN ACTIVE ", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 150), 2 )
                
                # Distance screen par dikhao (tuning ke liye helpful)
             cv2.putText( frame, f"Dist: {finger_dist:.0f} px", (10 , 80),
                     cv2.FONT_HERSHEY_PLAIN, 1.2, (255, 215, 0), 2)

                # Visual line draw karo (distance dikhane ke liye)
            #  cv2.line(frame, (index_finger_tip.x, index_finger_tip.y), (mid_finger_tip.x, mid_finger_tip.y), (255, 215, 0), 3)  # gold line
            #  cv2.circle(frame, (index_finger_tip.x,index_finger_tip.y), 10, (0, 255, 0), -1)
            #  cv2.circle(frame, (mid_finger_tip.x, mid_finger_tip.y), 10, (0, 255, 0), -1)
             #  Distance screen par dikhao (tuning ke liye helpful)
             cv2.putText(frame, f"Dist: {finger_dist:.0f} px",
             (10, 180),  # fixed position ya finger ke paas
              cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 255), 2)

        # ──────────────── PEACE SIGN DEBUG VERSION ────────────────

        index_extended  = landmarks[8].y  < landmarks[6].y  - 0.02
        middle_extended = landmarks[12].y < landmarks[10].y - 0.02
        ring_curled     = landmarks[16].y > landmarks[14].y  + 0.01
        pinky_curled    = landmarks[20].y > landmarks[18].y  + 0.01

        is_peace = index_extended and middle_extended and ring_curled and pinky_curled

        idx_x = int(index_finger_tip.x * w)
        idx_y = int(index_finger_tip.y * h)
        mid_x = int(mid_finger_tip.x * w)
        mid_y = int(mid_finger_tip.y * h)
        finger_dist = math.hypot(idx_x - mid_x, idx_y - mid_y)

        current_time = time.time()

        # Debug prints (console mein dikhega)
        print(f"is_peace: {is_peace} | prev_state: {previous_peace_state} | dist: {finger_dist:.1f} | cooldown left: {current_time - last_play_pause_time:.1f}s")

        if is_peace:
            cv2.putText(frame, "PEACE SIGN ACTIVE", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 150), 2)
            cv2.putText(frame, f"Dist: {finger_dist:.0f} px", (10, 180),
                        cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 255), 2)

            cv2.line(frame, (idx_x, idx_y), (mid_x, mid_y), (255, 215, 0), 2)
            cv2.circle(frame, (idx_x, idx_y), 8, (0, 255, 100), -1)
            cv2.circle(frame, (mid_x, mid_y), 8, (0, 255, 100), -1)

            if not previous_peace_state:
                print("   → New peace gesture detected!")
                if current_time - last_play_pause_time >= PLAY_COOLDOWN_SECONDS:
                    print(f"   → Cooldown passed → checking dist > 55 ({finger_dist > 55})")
                    if finger_dist > 30 :  # yeh value apne haath ke hisaab adjust karo
                        print("   → SPACE PRESSED!")
                        pg.press('space')
                        last_play_pause_time = current_time
                        cv2.putText(frame, "PLAY/PAUSE TRIGGERED", (10, 100),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 220, 100), 3)
                        cv2.rectangle(frame, (5, 90), (320, 130), (0, 255, 100), 3)
                else:
                    print("   → Cooldown abhi baki hai")

            previous_peace_state = True

        else:
            if previous_peace_state:    
                print("   → Peace sign ended")
            previous_peace_state = False
            # last_play_pause_time = 0   ← bilkul mat lagao yahan

     cv2.imshow('Webcam Feed', frame)
            
     if cv2.waitKey(1) & 0xFF == ord('s'):
       break 

cap.release()
cv2.destroyAllWindows()


