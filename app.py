from flask import Flask, render_template, Response
import cv2
import mediapipe as mp
import math
from gtts import gTTS
import os
import threading  
from playsound import playsound

app = Flask(__name__)

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose_video = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, model_complexity=1)

# Function to calculate angles between three landmarks
def calculateAngle(landmark1, landmark2, landmark3):
    x1, y1, _ = landmark1
    x2, y2, _ = landmark2
    x3, y3, _ = landmark3
    angle = math.degrees(math.atan2(y3 - y2, x3 - x2) - math.atan2(y1 - y2, x1 - x2))
    if angle < 0:
        angle += 360
    return angle

# Function to classify the yoga pose based on angles
def classifyPose(landmarks, frame):
    label = 'Unknown Pose'
    color = (0, 0, 255)  # Red color for unknown pose
    correction_instruction = ''

    # Calculate angles for various joints
    left_elbow_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value],
                                      landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value],
                                      landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value])
    right_elbow_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value],
                                       landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value],
                                       landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value])
    left_shoulder_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value],
                                         landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value],
                                         landmarks[mp_pose.PoseLandmark.LEFT_HIP.value])
    right_shoulder_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value],
                                          landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value],
                                          landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value])
    left_knee_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.LEFT_HIP.value],
                                     landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value],
                                     landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value])
    right_knee_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value],
                                      landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value],
                                      landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value])
    left_hip_angle = calculateAngle(
        landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value],
        landmarks[mp_pose.PoseLandmark.LEFT_HIP.value],
        landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
    )
    right_hip_angle = calculateAngle(
        landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value],
        landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value],
        landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value]
    )

    # Classify pose based on angles (simplified version)
    if left_elbow_angle > 165 and left_elbow_angle < 195 and right_elbow_angle > 165 and right_elbow_angle < 195:
        if left_shoulder_angle > 80 and left_shoulder_angle < 110 and right_shoulder_angle > 80 and right_shoulder_angle < 110:
            if (left_knee_angle > 165 and left_knee_angle < 195) or (right_knee_angle > 165 and right_knee_angle < 195):
                label = 'Warrior Pose'
                correction_instruction = "Warrior Pose or Virabhadrasana. This pose strengthens the legs, opens hips, and enhances stamina."
            if (left_knee_angle > 160 and left_knee_angle < 195) and (right_knee_angle > 160 and right_knee_angle < 195):
                if (160 <= left_hip_angle <= 200 and 160 <= right_hip_angle <= 200):
                    label = 'T Pose'
                    correction_instruction = "T pose or Tadasana. Tadasana improves posture, strengthens legs, and enhances focus."

    if (290 <= left_elbow_angle <= 345 and 20 <= right_elbow_angle <= 70 and 30 <= left_shoulder_angle <= 80 and
        20 <= right_shoulder_angle <= 70 and 160 <= left_knee_angle <= 210 and 150 <= right_knee_angle <= 200):
        label = 'Prayer Pose'
        correction_instruction = "Prayer pose or Pranamasana. Pranamasana calms the mind, improves posture, and prepares for deeper poses."

    if (140 <= left_elbow_angle <= 200 and 140 <= right_elbow_angle <= 200 and 50 <= left_shoulder_angle <= 110 and
        100 <= right_shoulder_angle <= 160 and 150 <= left_knee_angle <= 200 and 150 <= right_knee_angle <= 200 and
        ((20 <= left_hip_angle <= 80 and 110 <= right_hip_angle <= 170) or
         (290 <= right_hip_angle <= 340 and 190 <= left_hip_angle <= 260))):
        label = 'Triangle Pose'
        correction_instruction = "Triangle Pose or Trikonasana. It stretches the legs, groin, and torso while improving digestion and balance."

    if left_knee_angle > 165 and left_knee_angle < 195 or right_knee_angle > 165 and right_knee_angle < 195:
        if left_knee_angle > 315 and left_knee_angle < 335 or right_knee_angle > 25 and right_knee_angle < 45:
            label = 'Tree Pose'
            correction_instruction = "Tree Pose or Vrikshasana. It strengthens legs, improves balance, and stretches the inner thighs."

    if label != 'Unknown Pose':
        color = (0, 255, 0)  # Green color for known pose

    cv2.putText(frame, label, (10, 30), cv2.FONT_HERSHEY_PLAIN, 2, color, 2)
    return frame, label, correction_instruction

# Detect pose from the image
def detectPoseFromImg(frame, pose):
    imageRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(imageRGB)

    height, width, _ = frame.shape
    landmarks = []

    if results.pose_landmarks:
        mp_drawing.draw_landmarks(
            image=frame,
            landmark_list=results.pose_landmarks,
            connections=mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2),
            connection_drawing_spec=mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2)
        )

        for landmark in results.pose_landmarks.landmark:
            landmarks.append((int(landmark.x * width), int(landmark.y * height), int(landmark.z * width)))

    return frame, landmarks

# Function to play audio
def play_audio(text):
    tts = gTTS(text=text, lang='en')
    audio_file = "instruction.mp3"
    tts.save(audio_file)
    playsound(audio_file)
    os.remove(audio_file)

# Function to generate frames from the camera
def generate_frames():
    camera = cv2.VideoCapture(0)
    last_pose = None
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            frame = cv2.flip(frame, 1)
            frame_height, frame_width, _ = frame.shape
            frame = cv2.resize(frame, (int(frame_width * (640 / frame_height)), 640))

            frame, landmarks = detectPoseFromImg(frame, pose_video)

            if landmarks:
                frame, label, correction_instruction = classifyPose(landmarks, frame)

                if label != 'Unknown Pose' and label != last_pose:
                    threading.Thread(target=play_audio, args=(f"{correction_instruction}",)).start()
                    last_pose = label

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Flask routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
