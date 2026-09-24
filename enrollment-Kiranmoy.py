from database import connect

def enroll_student(student_id,course_id):

    conn = connect()

    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT * FROM enrollments
            WHERE student_id = ?
            AND course_id=?
            """,
            (student_id,course_id)
        )
        
        existing = cursor.fetchone()
        
        if existing:
            return "Student is already enrolled"
        
        cursor.execute(
            """
            INSERT INTO enrollments
            (student_id, course_id)
            VALUES(?, ?)
            """,
            (student_id, course_id)
        )

        conn.commit()

        return "Enrollment Successful"
    except Exception as e:
        return str(e)
    finally:
        conn.close()


def get_enrollments():

    conn = connect()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            enrollments.id,
            students.name,
            courses.course_name,
            enrollments.marks,
            enrollments.grade
        FROM enrollments

        JOIN students ON enrollments.student_id = students.id
        JOIN courses ON enrollments.course_id = courses.id
        """
    )

    rows = cursor.fetchall()

    conn.close()
    return rows


def update_grade(enrollment_id, marks, grade):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE enrollments
        SET marks = ?, grade = ?
        WHERE id = ?
        """,
        (marks, grade, enrollment_id)
    )

    conn.commit()
    conn.close()
    return "Grade Updated Successfully"


def count_enrollments():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM enrollments")
    total = cursor.fetchone()[0]

    conn.close()
    return total
    
