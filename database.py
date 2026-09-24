import os
import sqlite3


DB_NAME = "school.db"


def connect():
    return sqlite3.connect(DB_NAME)


def create_tables():
    from auth import hash_password
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

    # Scramble the default passwords
    default_hashed = hash_password("admin123")
    teacher_hashed = hash_password("teacher123")

    # Pull your email from .env
    admin_email = os.getenv("GMAIL_SENDER", "Studentadmin45@gmail.com")

    # Default admin accounts
    cursor.execute(
        "INSERT OR IGNORE INTO admins (username, password, email) VALUES (?, ?, ?)",
        ("admin", default_hashed, admin_email),
    )
    cursor.execute(
        "INSERT OR IGNORE INTO admins (username, password, email) VALUES (?, ?, ?)",
        ("teacher1", teacher_hashed, "teacher1@gmail.com"),
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


if __name__ == "__main__":
    create_tables()