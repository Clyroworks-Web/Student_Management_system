from database import connect
from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle


def add_student(name, age, email, phone="", gender="", dob="", status="Active"):
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO students (name, age, email, phone, gender, dob, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (name, age, email, phone, gender, dob, status),
        )
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
    cursor.execute(
        """
        SELECT id, name, age, email, phone, gender, dob, status
        FROM students
        WHERE status != 'Archived'
        """
    )
    data = cursor.fetchall()
    conn.close()
    return data


def update_student(student_id, name, age, email, phone="", gender="", dob="", status="Active"):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE students
        SET name=?, age=?, email=?, phone=?, gender=?, dob=?, status=?
        WHERE id=?
    """,
        (name, age, email, phone, gender, dob, status, student_id),
    )
    conn.commit()
    conn.close()
    return "Student Updated Successfully"


def search_students(keyword):
    conn = connect()
    cursor = conn.cursor()
    query = f"%{keyword}%"
    cursor.execute(
        """
        SELECT id, name, age, email, phone, gender, dob, status 
        FROM students
        WHERE status != 'Archived'
        AND (name LIKE ? OR email LIKE ? OR phone LIKE ?)
    """,
        (query, query, query),
    )
    data = cursor.fetchall()
    conn.close()
    return data


def delete_student(student_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE students SET status='Archived' WHERE id=?",
        (student_id,),
    )
    conn.commit()
    conn.close()
    return "Student deleted (Moved to Archive)."


def count_students():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM students WHERE status != 'Archived'"
    )
    total = cursor.fetchone()[0]
    conn.close()
    return total


def export_students_excel():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, age, email, phone, gender, dob, status FROM students"
    )
    rows = cursor.fetchall()
    conn.close()

    wb = Workbook()
    ws = wb.active
    ws.title = "students"
    ws.append(
        ["ID", "Name", "Age", "Email", "Phone", "Gender", "DOB", "Status"]
    )

    for row in rows:
        ws.append(row)

    wb.save("students_report.xlsx")
    return "students_report.xlsx"


def export_students_pdf():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, age, email, phone, gender, dob, status FROM students"
    )
    rows = cursor.fetchall()
    conn.close()

    data = [["ID", "Name", "Age", "Email", "Phone", "Gender", "DOB", "Status"]]
    for row in rows:
        data.append(list(row))

    pdf = SimpleDocTemplate("students_report.pdf")
    table = Table(data)
    table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ]
        )
    )
    pdf.build([table])
    return "students_report.pdf"

