from database import connect


def add_course(course_name, course_code, department="", duration=""):
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO courses(course_name, course_code, department, duration)
            VALUES(?, ?, ?, ?)
            """,
            (course_name, course_code, department, duration),
        )
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
    cursor.execute(
        "SELECT id, course_name, course_code, department, duration FROM courses"
    )
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
    return count