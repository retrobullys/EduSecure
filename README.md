# EduSecure: Real-Time Attendance Alert System

EduSecure is an AI-powered monitoring system designed to automate attendance recording and enhance academic integrity during examinations.

## Features

- **Automated Attendance Verification**: Facial recognition to mark attendance.
- **Real-Time Gaze Detection**: Monitors gaze deviation and records incidents.
- **Email Notifications**: Sends alerts to teachers with video clips.
- **Data Logging**: Stores attendance and incident data in a local database.
- **Report Generation**: Generates CSV and text reports.

## Installation

1. Install Python 3.11 (recommended for best compatibility).
2. Install dependencies: `pip install -r requirements.txt`

**Note**: The project uses InsightFace for facial recognition instead of face-recognition to ensure better compatibility with modern Python versions.

## Usage

### 1. Register Students

Run `python register_students.py` to register students' faces.

### 2. Run the Main System

Run `python main.py` to start the monitoring system.

- Press 'q' to quit.
- The system will automatically mark attendance and detect gaze deviations.

### 3. Generate Reports

Run `python report.py` to generate reports.

## Configuration

Edit the configuration variables in `main.py`:

- `EMAIL_SENDER`: Your email address
- `EMAIL_PASSWORD`: Your email password
- `EMAIL_RECEIVER`: Teacher's email
- `SMTP_SERVER`: SMTP server (e.g., 'smtp.gmail.com')
- `SMTP_PORT`: SMTP port (e.g., 587)

## Security Note

- Facial data is stored locally.
- Video clips are stored in the `video_clips` directory.
- Ensure compliance with privacy laws.

## Requirements

- Webcam
- Internet connection for email alerts
- Python libraries as listed in `requirements.txt`