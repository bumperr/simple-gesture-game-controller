import cv2
import mediapipe as mp
from pynput.keyboard import Controller, Key
import win32gui
import win32con
from camera_selector import select_camera_gui


keyboard = Controller()
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(select_camera_gui())
prev_action = None

font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 1
font_thickness = 2
font_color = (255, 255, 255)  

def fingers_up(hand_landmarks):
    tip_ids = [4, 8, 12, 16, 20]
    fingers = []

    fingers.append(hand_landmarks.landmark[tip_ids[0]].x < hand_landmarks.landmark[tip_ids[0] - 1].x)

    for i in range(1, 5):
        fingers.append(hand_landmarks.landmark[tip_ids[i]].y < hand_landmarks.landmark[tip_ids[i] - 2].y)

    return fingers

def get_hand_position(landmarks, frame_width):
    cx = int(landmarks.landmark[0].x * frame_width)
    return cx
#--------Gesture to Action Mapping---------
def gesture_to_action(fingers, cx, width, region):
    if region == 'left':
        if fingers == [0, 0, 0, 0, 0]:  
            return 'left'
        elif fingers == [1, 1, 1, 1, 1]:  
            return 'left+jump'
    elif region == 'right':
        if fingers == [0, 0, 0, 0, 0]:  
            return 'right'
        elif fingers == [1, 1, 1, 1, 1]:  
            return 'right+jump'
    return 'stop'
#--------Key Pressing Function---------
def press_key(action):
    global prev_action
    keys = {'left': Key.left, 'right': Key.right, 'jump': Key.space, 'left+jump': [Key.left, Key.space], 'right+jump': [Key.right, Key.space]}

    if action != prev_action:

        if prev_action in keys:
            if isinstance(keys[prev_action], list):
                for key in keys[prev_action]:
                    keyboard.release(key)
            else:
                keyboard.release(keys[prev_action])

        if action in keys:
            if isinstance(keys[action], list):
                for key in keys[action]:
                    keyboard.press(key)
            else:
                keyboard.press(keys[action])

        prev_action = action

def set_window_always_on_top(window_name):
    hwnd = win32gui.FindWindow(None, window_name)
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)
    height, width, _ = frame.shape
    #--------Resize frame with aspect ration 4:3---------
    resize_width = 320
    resize_height = 240
    frame_resized = cv2.resize(frame, (resize_width, resize_height))

    third = resize_width // 3
    cv2.rectangle(frame_resized, (0, 0), (third, resize_height), (0, 255, 0), 2)  
    cv2.rectangle(frame_resized, (third, 0), (2 * third, resize_height), (255, 255, 0), 2)  
    cv2.rectangle(frame_resized, (2 * third, 0), (resize_width, resize_height), (0, 0, 255), 2)  
    #--------Draw text for each region---------
    cv2.putText(frame_resized, "<- Move Left", (10, resize_height - 30), font, 0.4, (0, 255, 0), 2, cv2.LINE_AA)  
    cv2.putText(frame_resized, "Do Nothing", (third + 10, resize_height - 30), font, 0.4, (0, 255, 255), 2, cv2.LINE_AA)  
    cv2.putText(frame_resized, "-> Move Right", (2 * third + 10, resize_height - 30), font, 0.4, (0, 0, 255), 2, cv2.LINE_AA)  

    action_text = ""

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame_resized, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            fingers = fingers_up(hand_landmarks)
            cx = get_hand_position(hand_landmarks, resize_width)

            if cx < third:
                action = gesture_to_action(fingers, cx, resize_width, 'left')
            elif cx > 2 * third:
                action = gesture_to_action(fingers, cx, resize_width, 'right')
            else:
                action = 'stop'

            press_key(action)
            action_text = f"Action: {action}"

            cv2.putText(frame_resized, action_text, (10, 40), font, 1, font_color, font_thickness)

    else:
        press_key('stop')  
        action_text = "No hand detected"

    cv2.imshow("Mario Gesture Controller", frame_resized)

    set_window_always_on_top("Mario Gesture Controller")

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()