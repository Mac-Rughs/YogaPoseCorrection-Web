import math
import cv2
import mediapipe as mp
import matplotlib.pyplot as plt
from gtts import gTTS
import os
import threading
from playsound import playsound

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

def play_audio(text):
    """
    Generates and plays an audio instruction based on the provided text.
    
    Args:
        text: The text to be converted into speech and played.
    """
    print("Generating audio...")
    tts = gTTS(text=text, lang='en')
    audio_file = "instruction.mp3"
    tts.save(audio_file)
    print(f"Audio file {audio_file} created.")
    
    # Ensure audio file exists before attempting to play
    if os.path.exists(audio_file):
        print("Playing audio...")
        playsound(audio_file)
        print("Audio playback completed.")
        os.remove(audio_file)
    else:
        print("Error: Audio file not found.")

def calculateAngle(landmark1, landmark2, landmark3):
    """
    Calculates the angle between three landmarks.
    
    Args:
        landmark1, landmark2, landmark3: The landmarks containing x, y, and z coordinates.
        
    Returns:
        angle: The calculated angle in degrees.
    """
    x1, y1, _ = landmark1
    x2, y2, _ = landmark2
    x3, y3, _ = landmark3
    angle = math.degrees(math.atan2(y3 - y2, x3 - x2) - math.atan2(y1 - y2, x1 - x2))
    if angle < 0:
        angle += 360
    return angle

def classifyPose(landmarks, frame, display=False):
    """
    Classifies the yoga pose based on angles between landmarks and adds text to the image.
    
    Args:
        landmarks: List of detected landmarks.
        frame: The input image from the webcam.
        display: Boolean indicating whether to display images side by side.
        
    Returns:
        output_image: Image with detected pose landmarks drawn and pose label added.
        label: The classified pose label.
    """
    output_image = frame.copy()
    label = 'Unknown Pose'
    color = (0, 0, 255)  # Red color for unknown pose
    correction_instruction = None
    
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

    # Determine pose based on angles
    if left_elbow_angle > 165 and left_elbow_angle < 195 and right_elbow_angle > 165 and right_elbow_angle < 195:
        if left_shoulder_angle > 80 and left_shoulder_angle < 110 and right_shoulder_angle > 80 and right_shoulder_angle < 110:
            if left_knee_angle > 165 and left_knee_angle < 195 or right_knee_angle > 165 and right_knee_angle < 195:
                if left_knee_angle > 90 and left_knee_angle < 120 or right_knee_angle > 90 and right_knee_angle < 120:
                    label = 'Warrior Pose'
                    correction_instruction = "Warrior Pose or Virabhadrasana.You've extended one leg forward in a deep lunge, with arms stretched parallel and gaze forward.This pose strengthens the legs, opens hips, and enhances stamina."
            if left_knee_angle > 160 and left_knee_angle < 195 and right_knee_angle > 160 and right_knee_angle < 195:
                if(160<= left_hip_angle <= 200 and 160 <= right_hip_angle <= 200):
                    label = 'T Pose'
                    correction_instruction = "T pose or Tadasana.ou've successfully stood firm with feet together, arms raised straight up, spine elongated, and balanced.Tadasana improves posture, strengthens legs, and enhances focus."

    if (290 <= left_elbow_angle <= 345 and
    20 <= right_elbow_angle <= 70 and
    30 <= left_shoulder_angle <= 80 and
    20 <= right_shoulder_angle <= 70 and
    160 <= left_knee_angle <= 210 and
    150 <= right_knee_angle <= 200):
        label = 'Prayer Pose.'
        correction_instruction = "Prayer pose or Pranamasana.You've brought your palms together in front of your chest, standing tall with feet together.Pranamasana calms the mind, improves posture, and prepares for deeper poses."

    if (140 <= left_elbow_angle <= 200 and
      140 <= right_elbow_angle <= 200 and
      50 <= left_shoulder_angle <= 110 and
      100 <= right_shoulder_angle <= 160 and
      150 <= left_knee_angle <= 200 and
      150 <= right_knee_angle <= 200 and
      (20 <= left_hip_angle <= 80 and 110 <= right_hip_angle <= 170)or
      (290 <= right_hip_angle <= 340 and 190 <= left_hip_angle <= 260)):
        label = 'Triangle Pose'
        correction_instruction = "Triangle Pose or Trikonasana. You've successfully bent sideways with legs wide apart, one arm reaching to the ground, and the other extended upward. It stretches the legs, groin, and torso while improving digestion and balance."

    if left_knee_angle > 165 and left_knee_angle < 195 or right_knee_angle > 165 and right_knee_angle < 195:
        if left_knee_angle > 315 and left_knee_angle < 335 or right_knee_angle > 25 and right_knee_angle < 45:
            label = 'Tree Pose'
            correction_instruction = "Tree Pose or Vrikshasana. You've balanced on one leg, with the other foot placed against the inner thigh, hands joined in prayer above the head. It strengthens legs, improves balance, and stretches the inner thighs. "

    # Set color based on pose detected
    if label != 'Unknown Pose':
        color = (0, 255, 0)  # Green color for known pose
        if correction_instruction:
            # Start a new thread for playing the audio instruction
            print("Starting audio thread...")
            threading.Thread(target=play_audio, args=(correction_instruction,)).start()
    
    # Add pose label to image
    cv2.putText(output_image, label, (10, 30), cv2.FONT_HERSHEY_PLAIN, 2, color, 2)
    
    if display:
        # Display original and output images side by side
        plt.figure(figsize=[22,22])
        plt.subplot(121); plt.imshow(frame[:,:,::-1]); plt.title("Original Image"); plt.axis('off');
        plt.subplot(122); plt.imshow(output_image[:,:,::-1]); plt.title("Classified Output Image"); plt.axis('off');
        plt.show()
    
    return output_image, label

def detectPoseFromImg(image, pose, display=False):
    """
    Detects pose landmarks from an image using MediaPipe Pose.
    
    Args:
        image: Input image in BGR format.
        pose: MediaPipe Pose object.
        display: Boolean indicating whether to display the images.
        
    Returns:
        output_image: Image with pose landmarks drawn.
        landmarks: List of pose landmarks.
    """
    output_image = image.copy()
    imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(imageRGB)
    height, width, _ = image.shape
    landmarks = []
    if results.pose_landmarks:
        # Draw landmarks and connections on the image
        landmark_style = mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=5)
        connection_style = mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=3)
        mp_drawing.draw_landmarks(
            image=output_image,
            landmark_list=results.pose_landmarks,
            connections=mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=landmark_style,
            connection_drawing_spec=connection_style
        )
        # Extract landmark coordinates
        for landmark in results.pose_landmarks.landmark:
            landmarks.append((int(landmark.x * width), int(landmark.y * height),
                              int(landmark.z * width)))
    
    if display:
        # Display original and output images side by side
        plt.figure(figsize=[22,22])
        plt.subplot(121); plt.imshow(image[:,:,::-1]); plt.title("Original Image"); plt.axis('off');
        plt.subplot(122); plt.imshow(output_image[:,:,::-1]); plt.title("Output Image"); plt.axis('off');
        plt.show()
    
    return output_image, landmarks

def process_vid_classification(pose_video):
    """
    Processes video input from the webcam, performs pose detection and classification, and displays the result.
    
    Args:
        pose_video: MediaPipe Pose object configured for video processing.
        
    Returns:
        None
    """
    camera_video = cv2.VideoCapture(0)  # Use 0 for default webcam
    
    if not camera_video.isOpened():
        print("Error: Unable to access the webcam!")
        return
    
    cv2.namedWindow('Pose Classification', cv2.WINDOW_NORMAL)
    
    while camera_video.isOpened():
        ok, frame = camera_video.read()
        
        if not ok:
            print("Error: Unable to read frame from webcam!")
            break
        
        frame = cv2.flip(frame, 1)
        
        frame_height, frame_width, _ = frame.shape
        frame = cv2.resize(frame, (int(frame_width * (640 / frame_height)), 640))
        
        # Detect pose landmarks
        frame, landmarks = detectPoseFromImg(frame, pose_video, display=False)
        
        if landmarks:
            # Classify pose and display the result
            frame, _ = classifyPose(landmarks, frame, display=False)
        
        cv2.imshow('Pose Classification', frame)
        
        if cv2.waitKey(1) & 0xFF == 27:  # Press 'ESC' to exit
            break
    
    camera_video.release()
    cv2.destroy
