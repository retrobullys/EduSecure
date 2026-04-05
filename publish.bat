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
echo Description: AI-powered exam monitoring system using facial recognition and gaze detection for automated attendance and academic integrity. Features real-time alerts, video recording, and reporting. Built with Python, InsightFace, OpenCV, SQLite.
echo.
echo After creating the repository, run the following commands (replace YOUR_USERNAME with your GitHub username):
echo git remote add origin https://github.com/YOUR_USERNAME/EduSecure.git
echo git push -u origin main
echo.
pause