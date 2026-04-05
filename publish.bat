@echo off
echo Setting up Git configuration...
git config user.name "retrobullys"
git config user.email "panadollll2000@gmail.com"

echo Initializing Git repository...
git init

echo Adding files...
git add .

echo Committing files...
git commit -m "Initial commit: EduSecure AI-powered exam monitoring system"

echo.
echo Now, create a new repository on GitHub.com with the following details:
echo Repository name: EduSecure
echo Description: EduSecure: AI-Powered Exam Monitoring System - An intelligent surveillance solution that automates attendance tracking and maintains academic integrity during examinations using facial recognition and real-time gaze detection. Features automated alerts, video clip recording, and comprehensive reporting. *Key Technologies: Python, InsightFace, OpenCV, SQLite*
echo.
echo After creating the repository, run the following commands (replace YOUR_USERNAME with your GitHub username):
echo git remote add origin https://github.com/YOUR_USERNAME/EduSecure.git
echo git push -u origin main
echo.
pause