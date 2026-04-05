import sqlite3
import csv
import os
from datetime import datetime

DATABASE = 'edusecure.db'

def generate_attendance_report(date=None):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    if date:
        c.execute("SELECT s.name, a.time, a.status FROM attendance a JOIN students s ON a.student_id = s.id WHERE a.date = ?", (date,))
    else:
        c.execute("SELECT s.name, a.date, a.time, a.status FROM attendance a JOIN students s ON a.student_id = s.id")
    rows = c.fetchall()
    conn.close()

    if not rows:
        print("No attendance records found.")
        return

    filename = f"attendance_report_{date or 'all'}.csv"
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Date", "Time", "Status"])
        writer.writerows(rows)
    print(f"Attendance report saved as {filename}")

def generate_incident_report():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT s.name, i.timestamp, i.clip_path FROM incidents i JOIN students s ON i.student_id = s.id")
    rows = c.fetchall()
    conn.close()

    if not rows:
        print("No incident records found.")
        return

    filename = "incident_report.csv"
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Timestamp", "Clip Path"])
        writer.writerows(rows)
    print(f"Incident report saved as {filename}")

def generate_summary_report():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    # Attendance summary
    c.execute("SELECT COUNT(DISTINCT student_id) FROM attendance")
    total_students = c.fetchone()[0]

    # Incident summary
    c.execute("SELECT student_id, COUNT(*) FROM incidents GROUP BY student_id")
    incident_counts = c.fetchall()

    conn.close()

    filename = "summary_report.txt"
    with open(filename, 'w') as file:
        file.write("EduSecure Summary Report\n")
        file.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        file.write(f"Total students with attendance: {total_students}\n\n")
        file.write("Incidents per student:\n")
        for student_id, count in incident_counts:
            file.write(f"Student ID {student_id}: {count} incidents\n")
    print(f"Summary report saved as {filename}")

if __name__ == "__main__":
    generate_attendance_report()
    generate_incident_report()
    generate_summary_report()