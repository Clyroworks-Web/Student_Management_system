import csv
from tkinter import filedialog
from database import connect

def export_students_to_csv():
    # Ask user where to save the CSV
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
    # Ask user to pick a CSV file
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
                cursor.execute("""
                    INSERT INTO students (name, age, email, phone, gender, dob, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
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
                continue # Skip duplicates or invalid rows gracefully

    conn.commit()
    conn.close()
    return file_path, imported_count