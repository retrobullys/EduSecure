import cv2
import sqlite3
import os

DATABASE = 'edusecure.db'

# Try to import InsightFace, fallback if not available
try:
    import insightface
    INSIGHTFACE_AVAILABLE = True
    print("INFO: Using InsightFace for facial recognition")
except ImportError:
    INSIGHTFACE_AVAILABLE = False
    print("INFO: InsightFace not available, registration disabled")

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    encoding BLOB
                )''')
    conn.commit()
    conn.close()

# Initialize InsightFace if available
if INSIGHTFACE_AVAILABLE:
    face_app = insightface.app.FaceAnalysis()
    face_app.prepare(ctx_id=0, det_size=(640, 640))
else:
    face_app = None

def register_student(name):
    if not INSIGHTFACE_AVAILABLE:
        print("ERROR: Student registration requires InsightFace, which is not installed.")
        print("Please install InsightFace with: pip install insightface")
        print("Note: InsightFace requires Microsoft Visual C++ Build Tools for installation.")
        return

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return

    print(f"Registering {name}. Look at the camera and press 'c' to capture.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow('Register Student', frame)
        if cv2.waitKey(1) & 0xFF == ord('c'):
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            faces = face_app.get(rgb_frame)
            if faces:
                face_encoding = faces[0].embedding
                conn = sqlite3.connect(DATABASE)
                c = conn.cursor()
                c.execute("INSERT INTO students (name, encoding) VALUES (?, ?)",
                          (name, face_encoding.tobytes()))
                conn.commit()
                conn.close()
                print(f"Student {name} registered successfully.")
                break
            else:
                print("No face detected. Try again.")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    init_db()
    name = input("Enter student name: ")
    register_student(name)