import cv2
# Try to import InsightFace
try:
    import insightface
    INSIGHTFACE_AVAILABLE = True
    print("INFO: InsightFace available - using advanced facial recognition")
except ImportError:
    INSIGHTFACE_AVAILABLE = False
    print("INFO: Using OpenCV face detection (InsightFace optional)")
import mediapipe as mp
import sqlite3
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import datetime
import os
import threading
import time

# Configuration
DATABASE = 'edusecure.db'
VIDEO_CLIPS_DIR = 'video_clips'
EMAIL_SENDER = 'edusecuresender@gmail.com'
EMAIL_PASSWORD = 'ysbe sscy ynxm azws'
EMAIL_RECEIVER = 'kitomatetaro@gmail.com'
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
CLIP_DURATION = 3  # Reduced from 5 to 3 seconds for better responsiveness

# Enable basic gaze and head position detection
ENABLE_GAZE_DETECTION = True
print("INFO: Eye movement and head position tracking enabled")

# Create directories if not exist
if not os.path.exists(VIDEO_CLIPS_DIR):
    os.makedirs(VIDEO_CLIPS_DIR)

# Database setup
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    encoding BLOB
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY,
                    student_id INTEGER,
                    date TEXT,
                    time TEXT,
                    status TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS incidents (
                    id INTEGER PRIMARY KEY,
                    student_id INTEGER,
                    timestamp TEXT,
                    clip_path TEXT
                )''')
    conn.commit()
    conn.close()

# Initialize InsightFace (if available)
if INSIGHTFACE_AVAILABLE:
    face_app = insightface.app.FaceAnalysis()
    face_app.prepare(ctx_id=0, det_size=(640, 640))
else:
    face_app = None

# Load known faces
def load_known_faces():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT id, name, encoding FROM students")
    known_faces = []
    known_names = []
    known_ids = []
    for row in c.fetchall():
        known_ids.append(row[0])
        known_names.append(row[1])
        # InsightFace uses numpy arrays directly
        import numpy as np
        encoding = np.frombuffer(row[2], dtype=np.float32)
        known_faces.append(encoding)
    conn.close()
    return known_faces, known_names, known_ids

# Mark attendance
def mark_attendance(student_id, name):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    now = datetime.datetime.now()
    date = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    c.execute("INSERT INTO attendance (student_id, date, time, status) VALUES (?, ?, ?, ?)",
              (student_id, date, time_str, 'Present'))
    conn.commit()
    conn.close()
    print(f"Attendance marked for {name}")

# Record incident
def record_incident(student_id, clip_path):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO incidents (student_id, timestamp, clip_path) VALUES (?, ?, ?)",
              (student_id, timestamp, clip_path))
    conn.commit()
    conn.close()

# Send email
def send_email(subject, body, attachment_path):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    if attachment_path:
        attachment = open(attachment_path, "rb")
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(attachment_path)}")
        msg.attach(part)

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(EMAIL_SENDER, EMAIL_PASSWORD)
    text = msg.as_string()
    server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, text)
    server.quit()

# Eye detection and tracking
def detect_eyes(gray, face):
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

    # Handle different face object types
    if hasattr(face, 'bbox'):  # InsightFace face object
        x1, y1, x2, y2 = face.bbox
        x, y, w, h = int(x1), int(y1), int(x2 - x1), int(y2 - y1)
    else:  # OpenCV rectangle tuple
        (x, y, w, h) = face

    roi_gray = gray[y:y+h, x:x+w]
    eyes = eye_cascade.detectMultiScale(roi_gray)
    return [(ex+x, ey+y, ew, eh) for (ex, ey, ew, eh) in eyes]

# Head position analysis
def analyze_head_position(face):
    # Handle different face object types
    if hasattr(face, 'bbox'):  # InsightFace face object
        x1, y1, x2, y2 = face.bbox
        x, y, w, h = int(x1), int(y1), int(x2 - x1), int(y2 - y1)
    else:  # OpenCV rectangle tuple
        (x, y, w, h) = face

    # Calculate head tilt based on face dimensions
    aspect_ratio = float(w) / h

    # Normal head position should have aspect ratio around 0.75-0.85
    if aspect_ratio < 0.7 or aspect_ratio > 0.9:
        return "TILTED", aspect_ratio
    return "NORMAL", aspect_ratio

# Eye movement tracking
def track_eye_movement(eyes, frame_width, frame_height):
    if len(eyes) < 2:
        return "UNKNOWN", []

    eye_centers = []
    for (ex, ey, ew, eh) in eyes:
        center_x = ex + ew/2
        center_y = ey + eh/2
        eye_centers.append((center_x, center_y))

    # Calculate average eye position
    avg_x = sum(x for x, y in eye_centers) / len(eye_centers)
    avg_y = sum(y for x, y in eye_centers) / len(eye_centers)

    # Determine gaze direction
    center_threshold = 0.2  # 20% from center

    if avg_x < frame_width * (0.5 - center_threshold):
        horizontal = "LEFT"
    elif avg_x > frame_width * (0.5 + center_threshold):
        horizontal = "RIGHT"
    else:
        horizontal = "CENTER"

    if avg_y < frame_height * (0.5 - center_threshold):
        vertical = "UP"
    elif avg_y > frame_height * (0.5 + center_threshold):
        vertical = "DOWN"
    else:
        vertical = "CENTER"

    gaze_direction = f"{horizontal}_{vertical}"
    return gaze_direction, eye_centers

# Comprehensive cheating detection
def detect_cheating_behavior(gray, face, frame_width, frame_height):
    cheating_detected = False
    reasons = []

    # 1. Head position analysis
    head_status, aspect_ratio = analyze_head_position(face)
    if head_status == "TILTED":
        cheating_detected = True
        reasons.append(f"Head tilted (ratio: {aspect_ratio:.2f})")

    # 2. Eye detection and gaze analysis
    eyes = detect_eyes(gray, face)
    if len(eyes) >= 2:
        gaze_direction, eye_centers = track_eye_movement(eyes, frame_width, frame_height)

        # Check for suspicious gaze patterns
        if "LEFT" in gaze_direction or "RIGHT" in gaze_direction:
            cheating_detected = True
            reasons.append(f"Gaze deviated {gaze_direction}")

        if "UP" in gaze_direction:
            cheating_detected = True
            reasons.append("Looking up suspiciously")

        if "DOWN" in gaze_direction and len(eye_centers) > 0:
            # Check if looking down at an angle (might be looking at notes)
            avg_eye_y = sum(y for x, y in eye_centers) / len(eye_centers)
            if avg_eye_y > frame_height * 0.7:  # Looking very low
                cheating_detected = True
                reasons.append("Looking down at suspicious angle")
    else:
        reasons.append("Eyes not clearly visible")

    return cheating_detected, reasons

# Record video clip
def record_clip(cap, duration):
    clip_path = os.path.join(VIDEO_CLIPS_DIR, f"clip_{int(time.time())}.avi")
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(clip_path, fourcc, 20.0, (640, 480))

    start_time = time.time()
    while time.time() - start_time < duration:
        ret, frame = cap.read()
        if ret:
            out.write(frame)
        else:
            break

    out.release()
    return clip_path

# Handle incident in background thread
def handle_incident(student_id, reasons, cap):
    # Record incident
    clip_path = record_clip(cap, CLIP_DURATION)

    record_incident(student_id, clip_path)

    # Send alert email (with error handling)
    alert_message = f"Cheating Alert: {', '.join(reasons)}\nVideo evidence recorded: {clip_path}"
    try:
        send_email("EduSecure Cheating Alert", alert_message, clip_path)
        print(f"Incident recorded and alert sent for suspicious behavior")
    except Exception as e:
        print(f"Incident recorded but email failed to send: {e}")
        print(f"Video evidence saved at: {clip_path}")

# Main function
def main():
    init_db()
    known_faces, known_names, known_ids = load_known_faces()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return

    attendance_marked = set()
    frame_count = 0
    processing_interval = 3  # Process every 3rd frame to reduce lag

    print("EduSecure monitoring started. Press 'q' to quit and return to menu.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        should_process = (frame_count % processing_interval == 0)

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Basic face detection using OpenCV (fallback when InsightFace not available)
        if should_process:  # Only process faces every few frames to reduce lag
            if INSIGHTFACE_AVAILABLE and face_app is not None:
                # Use InsightFace when available
                faces = face_app.get(rgb_frame)
                face_encodings = [face.embedding for face in faces]

                for i, face_encoding in enumerate(face_encodings):
                    if known_faces:
                        # Calculate similarity with known faces
                        import numpy as np
                        similarities = [np.dot(face_encoding, known_face) / (np.linalg.norm(face_encoding) * np.linalg.norm(known_face)) for known_face in known_faces]
                        max_similarity = max(similarities) if similarities else 0
                        if max_similarity > 0.5:  # Threshold for match
                            match_index = similarities.index(max_similarity)
                            student_id = known_ids[match_index]
                            name = known_names[match_index]
                            if student_id not in attendance_marked:
                                mark_attendance(student_id, name)
                                attendance_marked.add(student_id)
            else:
                # Fallback: Basic face detection with OpenCV
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                faces = face_cascade.detectMultiScale(gray, 1.1, 4)

                # For demo: Mark attendance for any detected face (since we can't identify individuals yet)
                if len(faces) > 0 and not attendance_marked:
                    # Demo mode: Mark generic attendance
                    mark_attendance(1, "Demo Student")  # Placeholder
                    attendance_marked.add(1)
                    print("Face detected - Demo attendance marked (facial recognition coming soon!)")

            # Advanced cheating detection with eye movement and head position analysis
            if ENABLE_GAZE_DETECTION and len(faces) > 0:
                frame_height, frame_width = frame.shape[:2]

                for face in faces:
                    cheating_detected, reasons = detect_cheating_behavior(gray, face, frame_width, frame_height)

                    if cheating_detected:
                        print(f"ALERT: Cheating behavior detected! Reasons: {', '.join(reasons)}")

                        # Use demo student ID for now (will be associated with individual when facial recognition works)
                        student_id = 1

                        # Handle incident in background thread to prevent freezing
                        threading.Thread(target=handle_incident, args=(student_id, reasons, cap)).start()

                        # Draw warning on frame
                        if hasattr(face, 'bbox'):  # InsightFace face object
                            x1, y1, x2, y2 = face.bbox
                            x, y, w, h = int(x1), int(y1), int(x2 - x1), int(y2 - y1)
                        else:  # OpenCV rectangle tuple
                            (x, y, w, h) = face
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 3)  # Red rectangle
                        cv2.putText(frame, "CHEATING DETECTED!", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

        cv2.imshow('EduSecure', frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("Exiting EduSecure monitoring...")
            break

    cap.release()
    cv2.destroyAllWindows()
    print("EduSecure monitoring stopped. Returning to menu...")

if __name__ == "__main__":
    main()