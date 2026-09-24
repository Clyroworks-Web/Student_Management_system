# ================================================================
# STUDENT COURSE MANAGEMENT SYSTEM — Complete Source Code
# ================================================================
# Framework: CustomTkinter (Python GUI)
# Database: SQLite
# Auth: OTP via Gmail SMTP
# 
# Files: 13 Python modules
# ================================================================


# ================================================================
# FILE 1: main.py — Entry Point
# ================================================================
import customtkinter as ctk

from database import create_tables
from login import LoginWindow

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def main():
    create_tables()
    root = ctk.CTk()
    root.title("Student Management System")
    root.geometry("450x520")
    root.resizable(False, False)

    def on_login_success():
        """Called after OTP verification — clear login UI and launch main App."""
        for widget in root.winfo_children():
            widget.destroy()
        root.geometry("1280x750")
        root.resizable(True, True)
        from ui import App
        App(root, on_logout=lambda: restart_login(root))

    def restart_login(root):
        """Called on logout — tear down App and rebuild the login screen."""
        for widget in root.winfo_children():
            widget.destroy()
        root.geometry("450x520")
        root.resizable(False, False)
        LoginWindow(root, on_success=on_login_success)

    LoginWindow(root, on_success=on_login_success)
    root.mainloop()


if __name__ == "__main__":
    main()


# ================================================================
# FILE 2: database.py — SQLite Database Setup & Migrations
# ================================================================
import os
import sqlite3

DB_NAME = "school.db"


def connect():
    return sqlite3.connect(DB_NAME)


def create_tables():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON")

    # Admins table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admins(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT NOT NULL,
        email TEXT UNIQUE
    )
    """)

    # Students table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER,
        email TEXT UNIQUE,
        phone TEXT,
        gender TEXT,
        dob TEXT,
        address TEXT,
        status TEXT DEFAULT 'Active'
    )
    """)

    # Courses table (with department and duration)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS courses(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_name TEXT NOT NULL,
        course_code TEXT UNIQUE,
        department TEXT DEFAULT '',
        duration TEXT DEFAULT ''
    )
    """)

    # Enrollments table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS enrollments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        course_id INTEGER,
        marks REAL DEFAULT 0,
        grade TEXT DEFAULT 'N/A',
        FOREIGN KEY(student_id) REFERENCES students(id),
        FOREIGN KEY(course_id) REFERENCES courses(id)
    )
    """)

    # --- Migrations for existing installations ---

    # Students: add missing columns
    cursor.execute("PRAGMA table_info(students)")
    existing_columns = [col[1] for col in cursor.fetchall()]
    student_new_cols = {
        "phone": "TEXT",
        "gender": "TEXT",
        "dob": "TEXT",
        "status": "TEXT DEFAULT 'Active'",
    }
    for col_name, col_type in student_new_cols.items():
        if col_name not in existing_columns:
            cursor.execute(f"ALTER TABLE students ADD COLUMN {col_name} {col_type}")

    # Enrollments: add missing columns
    cursor.execute("PRAGMA table_info(enrollments)")
    existing_cols = [col[1] for col in cursor.fetchall()]
    if "marks" not in existing_cols:
        cursor.execute("ALTER TABLE enrollments ADD COLUMN marks REAL DEFAULT 0")
    if "grade" not in existing_cols:
        cursor.execute("ALTER TABLE enrollments ADD COLUMN grade TEXT DEFAULT 'N/A'")

    # Courses: add missing columns
    cursor.execute("PRAGMA table_info(courses)")
    course_cols = [col[1] for col in cursor.fetchall()]
    if "department" not in course_cols:
        cursor.execute("ALTER TABLE courses ADD COLUMN department TEXT DEFAULT ''")
    if "duration" not in course_cols:
        cursor.execute("ALTER TABLE courses ADD COLUMN duration TEXT DEFAULT ''")

    # Default admin accounts
    cursor.execute(
        "INSERT OR IGNORE INTO admins (username, password, email) VALUES (?, ?, ?)",
        ("admin", "admin123", "Studentadmin45@gmail.com"),
    )
    cursor.execute(
        "INSERT OR IGNORE INTO admins (username, password, email) VALUES (?, ?, ?)",
        ("teacher1", "teacher123", "teacher1@gmail.com"),
    )

    conn.commit()
    conn.close()


def add_admin(username, password, email):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO admins (username, password, email) VALUES (?, ?, ?)",
        (username, password, email),
    )
    conn.commit()
    conn.close()


# ================================================================
# FILE 3: auth.py — User Authentication (Hashed Passwords)
# ================================================================
import hashlib
from database import connect

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def create_users_table():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'Admin'
        )
    """)
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        default_pass = hash_password("admin123")
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                       ("admin", default_pass, "Admin"))
        conn.commit()
    conn.close()

def authenticate_user(username, password):
    conn = connect()
    cursor = conn.cursor()
    hashed = hash_password(password)
    cursor.execute("SELECT id, username, role FROM users WHERE username = ? AND password = ?", 
                   (username, hashed))
    user = cursor.fetchone()
    conn.close()
    return user


# ================================================================
# FILE 4: otp.py — OTP Generation & Email Sending
# ================================================================
import random
import smtplib
from email.mime.text import MIMEText


def generate_otp():
    return str(random.randint(100000, 999999))


def send_otp(receiver_email: str, otp: str) -> bool:
    sender_email = "Studentadmin45@gmail.com"
    app_password = "eenkpvtptygfzstp"

    subject = "Student Management System OTP"
    body = f"Your OTP is: {otp}"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.send_message(msg)
        return True
    except smtplib.SMTPAuthenticationError:
        print("Email could not be sent because the Gmail credentials are invalid.")
        return False
    except smtplib.SMTPException as e:
        print(f"SMTP error occurred while sending email: {e}")
        return False
    except Exception as e:
        print(f"Email could not be sent: {e}")
        return False


# ================================================================
# FILE 5: otp_window.py — OTP Verification Window
# ================================================================
import customtkinter as ctk
from tkinter import messagebox


class OTPWindow:
    def __init__(self, root, generated_otp, on_success=None, on_cancel=None):
        self.root = root
        self.generated_otp = str(generated_otp)
        self.on_success = on_success
        self.on_cancel = on_cancel

        self.root.title("OTP Verification")
        self.root.geometry("420x320")
        self.root.resizable(False, False)
        self.root.configure(fg_color="#0F172A")

        try:
            self.root.grab_set()
        except Exception:
            pass

        self.root.lift()
        self.root.focus_force()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        card = ctk.CTkFrame(root, fg_color="#1E293B", corner_radius=14)
        card.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(card, text="🔐", font=("Segoe UI", 42)).pack(pady=(25, 5))
        ctk.CTkLabel(card, text="OTP Verification", font=("Segoe UI", 20, "bold"), text_color="#F8FAFC").pack(pady=(0, 5))
        ctk.CTkLabel(card, text="Enter the 6-digit OTP sent to your email", font=("Segoe UI", 12), text_color="#94A3B8").pack(pady=(0, 15))

        self.otp_entry = ctk.CTkEntry(card, placeholder_text="Enter OTP", width=280, height=42,
            fg_color="#0F172A", border_color="#334155", text_color="#F8FAFC", font=("Segoe UI", 16), justify="center")
        self.otp_entry.pack(pady=8)

        ctk.CTkButton(card, text="Verify OTP", command=self.verify_otp, width=280, height=42,
            fg_color="#6366F1", hover_color="#4F46E5", font=("Segoe UI", 14, "bold"), corner_radius=8).pack(pady=(15, 20))

    def on_close(self):
        try:
            self.root.grab_release()
        except Exception:
            pass
        self.root.destroy()
        if self.on_cancel:
            self.on_cancel()

    def verify_otp(self):
        entered_otp = self.otp_entry.get().strip()
        if entered_otp == self.generated_otp:
            messagebox.showinfo("Success", "OTP Verified", parent=self.root)
            on_success = self.on_success
            try:
                self.root.grab_release()
            except Exception:
                pass
            self.root.destroy()
            if on_success:
                on_success()
        else:
            messagebox.showerror("Error", "Invalid OTP", parent=self.root)


# ================================================================
# FILE 6: login.py — Login Window with Forgot Password Flow
# ================================================================
import customtkinter as ctk
from tkinter import messagebox
from database import connect
from otp import generate_otp, send_otp
from otp_window import OTPWindow
from reset_password import ResetPasswordWindow


class LoginWindow:
    def __init__(self, root, on_success=None):
        self.root = root
        self.on_success = on_success
        self.root.title("Student Management System")
        self.root.configure(fg_color="#0F172A")

        card = ctk.CTkFrame(root, fg_color="#1E293B", corner_radius=16, width=380, height=460)
        card.pack(expand=True, pady=30, padx=35)
        card.pack_propagate(False)

        ctk.CTkLabel(card, text="🎓", font=("Segoe UI", 48)).pack(pady=(30, 5))
        ctk.CTkLabel(card, text="Student Management", font=("Segoe UI", 22, "bold"), text_color="#F8FAFC").pack(pady=(0, 2))
        ctk.CTkLabel(card, text="Sign in to your account", font=("Segoe UI", 13), text_color="#94A3B8").pack(pady=(0, 25))

        ctk.CTkLabel(card, text="Username", font=("Segoe UI", 12), text_color="#94A3B8", anchor="w").pack(padx=30, anchor="w")
        self.username = ctk.CTkEntry(card, placeholder_text="Enter username", width=320, height=40,
            fg_color="#0F172A", border_color="#334155", text_color="#F8FAFC")
        self.username.pack(padx=30, pady=(4, 12))

        ctk.CTkLabel(card, text="Password", font=("Segoe UI", 12), text_color="#94A3B8", anchor="w").pack(padx=30, anchor="w")
        self.password = ctk.CTkEntry(card, placeholder_text="Enter password", show="*", width=320, height=40,
            fg_color="#0F172A", border_color="#334155", text_color="#F8FAFC")
        self.password.pack(padx=30, pady=(4, 20))

        ctk.CTkButton(card, text="Sign In", command=self.login, width=320, height=42,
            fg_color="#6366F1", hover_color="#4F46E5", font=("Segoe UI", 14, "bold"), corner_radius=8).pack(padx=30)

        ctk.CTkButton(card, text="Forgot Password?", command=self.forgot_password, width=320, height=30,
            fg_color="transparent", hover_color="#1E293B", text_color="#6366F1", font=("Segoe UI", 12)).pack(pady=(10, 15))

    def login(self):
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admins WHERE username=? AND password=?",
            (self.username.get().strip(), self.password.get().strip()))
        admin = cursor.fetchone()
        conn.close()

        if admin:
            otp = generate_otp()
            success = send_otp("Studentadmin45@gmail.com", otp)
            if success:
                messagebox.showinfo("Success", "OTP sent successfully")
                otp_root = ctk.CTkToplevel(self.root)
                OTPWindow(otp_root, otp, on_success=self._on_otp_verified)
            else:
                messagebox.showerror("Error", "Failed to send OTP")
        else:
            messagebox.showerror("Error", "Invalid Username or Password")

    def _on_otp_verified(self):
        if self.on_success:
            self.on_success()

    def forgot_password(self):
        self.forget_window = ctk.CTkToplevel(self.root)
        self.forget_window.title("Forgot Password")
        self.forget_window.geometry("420x300")
        self.forget_window.resizable(False, False)
        self.forget_window.configure(fg_color="#0F172A")
        self.forget_window.grab_set()
        self.forget_window.lift()
        self.forget_window.focus_force()

        card = ctk.CTkFrame(self.forget_window, fg_color="#1E293B", corner_radius=14)
        card.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(card, text="🔑", font=("Segoe UI", 36)).pack(pady=(20, 5))
        ctk.CTkLabel(card, text="Forgot Password", font=("Segoe UI", 20, "bold"), text_color="#F8FAFC").pack(pady=(0, 5))
        ctk.CTkLabel(card, text="Enter your username to receive an OTP", font=("Segoe UI", 12), text_color="#94A3B8").pack(pady=(0, 15))

        self.fp_username = ctk.CTkEntry(card, placeholder_text="Username", width=300, height=40,
            fg_color="#0F172A", border_color="#334155", text_color="#F8FAFC")
        self.fp_username.pack(pady=5)

        ctk.CTkButton(card, text="Send OTP", command=self.send_reset_otp, width=300, height=40,
            fg_color="#6366F1", hover_color="#4F46E5", font=("Segoe UI", 13, "bold")).pack(pady=(15, 20))

    def send_reset_otp(self):
        username = self.fp_username.get().strip()
        if not username:
            messagebox.showwarning("Warning", "Please enter a username.", parent=self.forget_window)
            return

        conn = connect()
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM admins WHERE username=?", (username,))
        result = cursor.fetchone()
        conn.close()

        if not result or not result[0]:
            messagebox.showwarning("Warning", f"No account found for username: {username}", parent=self.forget_window)
            return

        receiver_email = result[0]
        otp = generate_otp()
        success = send_otp(receiver_email, otp)

        if success:
            messagebox.showinfo("Success", "OTP sent successfully!", parent=self.forget_window)
            self._reset_username = username
            self.forget_window.withdraw()
            otp_root = ctk.CTkToplevel(self.root)
            OTPWindow(otp_root, otp, on_success=self.open_reset_password)
        else:
            messagebox.showerror("Error", "Failed to send OTP.", parent=self.forget_window)
            try:
                self.forget_window.grab_release()
            except Exception:
                pass
            self.forget_window.destroy()

    def open_reset_password(self):
        username = self._reset_username
        try:
            self.forget_window.grab_release()
        except Exception:
            pass
        self.forget_window.destroy()
        reset_root = ctk.CTkToplevel(self.root)
        ResetPasswordWindow(reset_root, username)


# ================================================================
# FILE 7: reset_password.py — Password Reset Window
# ================================================================
import customtkinter as ctk
from tkinter import messagebox
from database import connect


class ResetPasswordWindow:
    def __init__(self, root, username, on_success=None):
        self.root = root
        self.username = username
        self.on_success = on_success

        self.root.title("Reset Password")
        self.root.geometry("420x450")
        self.root.resizable(False, False)
        self.root.configure(fg_color="#0F172A")

        try:
            self.root.grab_set()
        except Exception:
            pass
        self.root.lift()
        self.root.focus_force()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        card = ctk.CTkFrame(root, fg_color="#1E293B", corner_radius=14)
        card.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(card, text="🔒", font=("Segoe UI", 42)).pack(pady=(25, 5))
        ctk.CTkLabel(card, text="Reset Password", font=("Segoe UI", 20, "bold"), text_color="#F8FAFC").pack(pady=(0, 3))
        ctk.CTkLabel(card, text=f"Resetting password for: {self.username}", font=("Segoe UI", 12), text_color="#94A3B8").pack(pady=(0, 20))

        ctk.CTkLabel(card, text="New Password", font=("Segoe UI", 12), text_color="#94A3B8", anchor="w").pack(padx=40, anchor="w")
        self.new_password = ctk.CTkEntry(card, placeholder_text="Enter new password", show="*", width=300, height=40,
            fg_color="#0F172A", border_color="#334155", text_color="#F8FAFC")
        self.new_password.pack(padx=40, pady=(4, 10))

        ctk.CTkLabel(card, text="Confirm Password", font=("Segoe UI", 12), text_color="#94A3B8", anchor="w").pack(padx=40, anchor="w")
        self.confirm_password = ctk.CTkEntry(card, placeholder_text="Confirm new password", show="*", width=300, height=40,
            fg_color="#0F172A", border_color="#334155", text_color="#F8FAFC")
        self.confirm_password.pack(padx=40, pady=(4, 15))

        ctk.CTkButton(card, text="Update Password", command=self.update_password, width=300, height=42,
            fg_color="#6366F1", hover_color="#4F46E5", font=("Segoe UI", 14, "bold"), corner_radius=8).pack(padx=40, pady=(5, 20))

    def on_close(self):
        try:
            self.root.grab_release()
        except Exception:
            pass
        self.root.destroy()

    def update_password(self):
        new_password = self.new_password.get().strip()
        confirm_password = self.confirm_password.get().strip()

        if not new_password or not confirm_password:
            messagebox.showwarning("Warning", "Please fill all fields.", parent=self.root)
            return
        if new_password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match.", parent=self.root)
            return

        conn = connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM admins WHERE username=?", (self.username,))
        if not cursor.fetchone():
            conn.close()
            messagebox.showerror("Error", "Username not found.", parent=self.root)
            return

        cursor.execute("UPDATE admins SET password=? WHERE username=?", (new_password, self.username))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Password updated successfully.", parent=self.root)
        self.on_close()
        if self.on_success:
            self.on_success()


# ================================================================
# FILE 8: student.py — Student CRUD + Excel/PDF Export
# ================================================================
from database import connect
from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle


def add_student(name, age, email, phone="", gender="", dob="", status="Active"):
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO students (name, age, email, phone, gender, dob, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (name, age, email, phone, gender, dob, status))
        conn.commit()
        return "Student Added Successfully"
    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            return "Email address already exists"
        return str(e)
    finally:
        conn.close()


def get_students():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, age, email, phone, gender, dob, status FROM students WHERE status != 'Archived'")
    data = cursor.fetchall()
    conn.close()
    return data


def update_student(student_id, name, age, email, phone="", gender="", dob="", status="Active"):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("UPDATE students SET name=?, age=?, email=?, phone=?, gender=?, dob=?, status=? WHERE id=?",
        (name, age, email, phone, gender, dob, status, student_id))
    conn.commit()
    conn.close()
    return "Student Updated Successfully"


def search_students(keyword):
    conn = connect()
    cursor = conn.cursor()
    query = f"%{keyword}%"
    cursor.execute("SELECT id, name, age, email, phone, gender, dob, status FROM students WHERE status != 'Archived' AND (name LIKE ? OR email LIKE ? OR phone LIKE ?)",
        (query, query, query))
    data = cursor.fetchall()
    conn.close()
    return data


def delete_student(student_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("UPDATE students SET status='Archived' WHERE id=?", (student_id,))
    conn.commit()
    conn.close()
    return "Student deleted (Moved to Archive)."


def count_students():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM students WHERE status != 'Archived'")
    total = cursor.fetchone()[0]
    conn.close()
    return total


def export_students_excel():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, age, email, phone, gender, dob, status FROM students")
    rows = cursor.fetchall()
    conn.close()
    wb = Workbook()
    ws = wb.active
    ws.title = "students"
    ws.append(["ID", "Name", "Age", "Email", "Phone", "Gender", "DOB", "Status"])
    for row in rows:
        ws.append(row)
    wb.save("students_report.xlsx")
    return "students_report.xlsx"


def export_students_pdf():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, age, email, phone, gender, dob, status FROM students")
    rows = cursor.fetchall()
    conn.close()
    data = [["ID", "Name", "Age", "Email", "Phone", "Gender", "DOB", "Status"]]
    for row in rows:
        data.append(list(row))
    pdf = SimpleDocTemplate("students_report.pdf")
    table = Table(data)
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
    ]))
    pdf.build([table])
    return "students_report.pdf"


# ================================================================
# FILE 9: course.py — Course CRUD
# ================================================================
from database import connect


def add_course(course_name, course_code, department="", duration=""):
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO courses(course_name, course_code, department, duration) VALUES(?, ?, ?, ?)",
            (course_name, course_code, department, duration))
        conn.commit()
        return "Course Added"
    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            return "Course code already exists"
        return str(e)
    finally:
        conn.close()


def get_courses():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT id, course_name, course_code, department, duration FROM courses")
    data = cursor.fetchall()
    conn.close()
    return data


def count_courses():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM courses")
    count = cursor.fetchone()[0]
    conn.close()
    return count


# ================================================================
# FILE 10: enrollment.py — Enrollment CRUD + Grade Assignment
# ================================================================
from database import connect


def enroll_student(student_id, course_id):
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM enrollments WHERE student_id = ? AND course_id = ?", (student_id, course_id))
        if cursor.fetchone():
            return "Student is already enrolled"
        cursor.execute("INSERT INTO enrollments (student_id, course_id) VALUES(?, ?)", (student_id, course_id))
        conn.commit()
        return "Enrollment Successful"
    except Exception as e:
        return str(e)
    finally:
        conn.close()


def get_enrollments():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT enrollments.id, students.name, courses.course_name, enrollments.marks, enrollments.grade
        FROM enrollments
        JOIN students ON enrollments.student_id = students.id
        JOIN courses ON enrollments.course_id = courses.id
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows


def count_enrollments():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM enrollments")
    total = cursor.fetchone()[0]
    conn.close()
    return total


def update_grade(enrollment_id, marks, grade):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("UPDATE enrollments SET marks = ?, grade = ? WHERE id = ?", (marks, grade, enrollment_id))
    conn.commit()
    conn.close()
    return "Grade updated successfully!"


def search_enrollments(keyword):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT enrollments.id, students.name, courses.course_name, enrollments.marks, enrollments.grade
        FROM enrollments
        JOIN students ON enrollments.student_id = students.id
        JOIN courses ON enrollments.course_id = courses.id
        WHERE students.name LIKE ? OR courses.course_name LIKE ?
    """, (f"%{keyword}%", f"%{keyword}%"))
    rows = cursor.fetchall()
    conn.close()
    return rows


# ================================================================
# FILE 11: csv_utils.py — CSV Import/Export
# ================================================================
import csv
from tkinter import filedialog
from database import connect

def export_students_to_csv():
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        title="Export Students Data"
    )
    if not file_path:
        return None
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, age, email, phone, gender, dob, status FROM students")
    rows = cursor.fetchall()
    conn.close()
    headers = ["ID", "Name", "Age", "Email", "Phone", "Gender", "DOB", "Status"]
    with open(file_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    return file_path

def import_students_from_csv():
    file_path = filedialog.askopenfilename(
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        title="Import Students CSV"
    )
    if not file_path:
        return None, 0
    conn = connect()
    cursor = conn.cursor()
    imported_count = 0
    with open(file_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                cursor.execute("INSERT INTO students (name, age, email, phone, gender, dob, status) VALUES (?, ?, ?, ?, ?, ?, ?)", (
                    row.get("Name", "").strip(),
                    int(row.get("Age", 0)),
                    row.get("Email", "").strip(),
                    row.get("Phone", "").strip(),
                    row.get("Gender", "Other").strip(),
                    row.get("DOB", "").strip(),
                    row.get("Status", "Active").strip()
                ))
                imported_count += 1
            except Exception:
                continue
    conn.commit()
    conn.close()
    return file_path, imported_count


# ================================================================
# FILE 12: validators.py — Input Validation
# ================================================================
import re

def validate_student_inputs(name, age, email, phone, dob):
    if not name or len(name.strip()) < 2:
        return False, "Name must be at least 2 characters long."
    if not age.isdigit() or not (5 <= int(age) <= 100):
        return False, "Age must be a valid number between 5 and 100."
    email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not re.match(email_pattern, email.strip()):
        return False, "Please enter a valid email address (e.g., user@domain.com)."
    phone_pattern = r"^\d{10}$"
    if not re.match(phone_pattern, phone.strip()):
        return False, "Phone number must be exactly 10 digits."
    dob_pattern = r"^\d{4}-\d{2}-\d{2}$"
    if not re.match(dob_pattern, dob.strip()):
        return False, "DOB must be in YYYY-MM-DD format."
    return True, "Valid"


# ================================================================
# FILE 13: ui.py — Main Application UI (1550+ lines)
# See the separate ui.py file for the complete code.
# It contains the App class with 6 pages:
#   - Dashboard (welcome card, stats, quick actions)
#   - Students (CRUD table, search, import/export CSV)
#   - Courses (CRUD table with department & duration)
#   - Enrollment (enroll, assign grades, search, export)
#   - Reports (4 report cards)
#   - Settings (Profile, App, Database, Notification, Security)
#   - Logout confirmation page
# ================================================================
# The ui.py file is too large to include inline here.
# Please refer to the separate ui.py file in the project.

