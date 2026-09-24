import tkinter as tk
from tkinter import ttk
from datetime import datetime
from typing import Any

import customtkinter as ctk
from csv_utils import export_students_to_csv, import_students_from_csv

from student import (
    add_student,
    get_students,
    delete_student,
    update_student,
    search_students,
    count_students,
    export_students_excel,
    export_students_pdf,
)

from course import add_course, get_courses, count_courses
from enrollment import enroll_student, get_enrollments, count_enrollments, update_grade


# ============================================================
# DESIGN SYSTEM — Color Palette
# ============================================================
C = {
    "primary": "#6366F1",
    "primary_hover": "#4F46E5",
    "secondary": "#10B981",
    "secondary_hover": "#059669",
    "accent": "#F59E0B",
    "accent_hover": "#D97706",
    "danger": "#EF4444",
    "danger_hover": "#DC2626",
    "bg": "#0F172A",
    "card": "#1E293B",
    "card_hover": "#334155",
    "text": "#F8FAFC",
    "muted": "#94A3B8",
    "border": "#334155",
    "transparent": "transparent",
}


class App:
    def __init__(self, root, on_logout=None):
        self.root = root
        self.on_logout = on_logout
        self.root.title("Student Management System")
        self.root.geometry("1280x750")
        self.root.resizable(True, True)
        self.root.configure(fg_color=C["bg"])

        self.nav_buttons = {}
        self.active_page = None

        # ── Treeview dark-mode styling (applied once) ──
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Dark.Treeview",
            background=C["card"],
            foreground="white",
            fieldbackground=C["card"],
            rowheight=32,
            font=("Segoe UI", 10),
            borderwidth=0,
        )
        style.configure(
            "Dark.Treeview.Heading",
            background=C["bg"],
            foreground="white",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            borderwidth=0,
        )
        style.map(
            "Dark.Treeview",
            background=[("selected", C["primary"])],
        )

        # ── Build layout ──
        self._build_sidebar()
        self._build_main_area()
        self._build_dashboard_page()
        self._build_students_page()
        self._build_courses_page()
        self._build_enrollment_page()
        self._build_reports_page()
        self._build_settings_page()
        self._build_logout_page()

        self.show_dashboard()

    # ============================================================
    #  SIDEBAR
    # ============================================================
    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(
            self.root, width=220, corner_radius=0, fg_color=C["bg"]
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color=C["transparent"])
        logo_frame.pack(fill="x", padx=16, pady=(20, 30))

        ctk.CTkLabel(
            logo_frame,
            text="🎓  Student\n     Management System",
            font=("Segoe UI", 13, "bold"),
            text_color=C["text"],
            justify="left",
        ).pack(anchor="w")

        # Nav items
        nav_items = [
            ("📊", "Dashboard", self.show_dashboard),
            ("👨‍🎓", "Students", self.show_students),
            ("📚", "Courses", self.show_courses),
            ("📝", "Enrollment", self.show_enrollments),
            ("📋", "Reports", self.show_reports),
            ("⚙️", "Settings", self.show_settings),
        ]

        for icon, label, cmd in nav_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"  {icon}  {label}",
                command=cmd,
                anchor="w",
                width=190,
                height=40,
                fg_color=C["transparent"],
                hover_color=C["card"],
                text_color=C["muted"],
                font=("Segoe UI", 13),
                corner_radius=8,
            )
            btn.pack(padx=12, pady=2)
            self.nav_buttons[label] = btn

        # Spacer
        ctk.CTkFrame(self.sidebar, fg_color=C["transparent"], height=10).pack(
            expand=True
        )

        # Logout button
        ctk.CTkButton(
            self.sidebar,
            text="  🚪  Logout",
            command=self.show_logout,
            anchor="w",
            width=190,
            height=40,
            fg_color=C["transparent"],
            hover_color=C["danger"],
            text_color=C["muted"],
            font=("Segoe UI", 13),
            corner_radius=8,
        ).pack(padx=12, pady=2)

        # Footer
        footer = ctk.CTkFrame(self.sidebar, fg_color=C["transparent"])
        footer.pack(fill="x", padx=16, pady=(0, 20))
        ctk.CTkLabel(
            footer,
            text="Better Students\nBrighter Future",
            font=("Segoe UI", 11),
            text_color=C["muted"],
        ).pack(anchor="w")

    def _set_active_nav(self, page_name):
        for name, btn in self.nav_buttons.items():
            if name == page_name:
                btn.configure(fg_color=C["primary"], text_color=C["text"])
            else:
                btn.configure(fg_color=C["transparent"], text_color=C["muted"])

    # ============================================================
    #  MAIN AREA (header + content)
    # ============================================================
    def _build_main_area(self):
        self.right_area = ctk.CTkFrame(self.root, fg_color=C["bg"])
        self.right_area.pack(side="right", fill="both", expand=True)

        # ── Header bar ──
        header = ctk.CTkFrame(self.right_area, height=50, fg_color=C["bg"])
        header.pack(fill="x", padx=20, pady=(12, 0))
        header.pack_propagate(False)

        self.search_global = ctk.CTkEntry(
            header,
            placeholder_text="🔍  Search students, courses...",
            width=320,
            height=36,
            fg_color=C["card"],
            border_color=C["border"],
            text_color=C["text"],
            corner_radius=8,
        )
        self.search_global.pack(side="left")

        # User info (right side)
        user_frame = ctk.CTkFrame(header, fg_color=C["transparent"])
        user_frame.pack(side="right")

        ctk.CTkLabel(
            user_frame,
            text="Admin",
            font=("Segoe UI", 13),
            text_color=C["text"],
        ).pack(side="right", padx=(8, 0))

        ctk.CTkLabel(
            user_frame,
            text="👤",
            font=("Segoe UI", 20),
        ).pack(side="right")

        # ── Content container ──
        self.content = ctk.CTkFrame(self.right_area, fg_color=C["bg"])
        self.content.pack(fill="both", expand=True, padx=20, pady=12)

        # Page frames
        self.pages = {}
        for name in [
            "dashboard",
            "students",
            "courses",
            "enrollment",
            "reports",
            "settings",
            "logout",
        ]:
            frame = ctk.CTkFrame(self.content, fg_color=C["transparent"])
            self.pages[name] = frame

    # ============================================================
    #  NAVIGATION HELPERS
    # ============================================================
    def _hide_all(self):
        if hasattr(self, "pages"):
            for frame in self.pages.values():
                frame.pack_forget()
            return

        for attr in ["student_frame", "course_frame", "enrollment_frame", "dashboard_frame", "logout_frame"]:
            frame = getattr(self, attr, None)
            if frame is not None:
                try:
                    frame.pack_forget()
                except Exception:
                    pass

    def _show_page(self, name, nav_label=None):
        self._hide_all()

        if hasattr(self, "pages"):
            self.pages[name].pack(fill="both", expand=True)
        else:
            target = getattr(self, f"{name}_frame", None)
            if target is None:
                target = getattr(self, name, None)
            if target is not None:
                target.pack(fill="both", expand=True)

        if nav_label:
            self._set_active_nav(nav_label)
        self.active_page = name

    # ============================================================
    #  1. DASHBOARD PAGE
    # ============================================================
    def _build_dashboard_page(self):
        p = self.pages["dashboard"]

        # Welcome card
        welcome = ctk.CTkFrame(p, fg_color=C["card"], corner_radius=12)
        welcome.pack(fill="x", pady=(0, 16))

        wl = ctk.CTkFrame(welcome, fg_color=C["transparent"])
        wl.pack(side="left", fill="x", expand=True, padx=25, pady=20)

        ctk.CTkLabel(
            wl,
            text="Welcome Back, Admin! 👋",
            font=("Segoe UI", 24, "bold"),
            text_color=C["text"],
        ).pack(anchor="w")

        ctk.CTkLabel(
            wl,
            text="Here's what's happening with your students and courses today.",
            font=("Segoe UI", 13),
            text_color=C["muted"],
        ).pack(anchor="w", pady=(4, 0))

        # Today's date card
        date_frame = ctk.CTkFrame(welcome, fg_color=C["bg"], corner_radius=10)
        date_frame.pack(side="right", padx=25, pady=20)

        ctk.CTkLabel(
            date_frame,
            text="  📅  Today",
            font=("Segoe UI", 11),
            text_color=C["muted"],
        ).pack(padx=15, pady=(10, 0))

        ctk.CTkLabel(
            date_frame,
            text=datetime.now().strftime("%d %b %Y"),
            font=("Segoe UI", 14, "bold"),
            text_color=C["text"],
        ).pack(padx=15, pady=(2, 10))

        # Stats row
        stats_row = ctk.CTkFrame(p, fg_color=C["transparent"])
        stats_row.pack(fill="x", pady=(0, 16))

        stat_defs = [
            ("Total Students", "count_students", "#3B82F6", "📘"),
            ("Total Courses", "count_courses", "#10B981", "📗"),
            ("Enrolled Students", "count_enrollments", "#F59E0B", "📙"),
            ("Pending Reports", "zero", "#EF4444", "📕"),
        ]

        self.dash_labels = {}
        for i, (title, key, color, icon) in enumerate(stat_defs):
            card = ctk.CTkFrame(stats_row, fg_color=C["card"], corner_radius=12)
            card.grid(row=0, column=i, padx=6, pady=0, sticky="nsew")
            stats_row.grid_columnconfigure(i, weight=1)

            ctk.CTkLabel(
                card, text=f" {icon}",
                font=("Segoe UI", 28),
            ).pack(anchor="w", padx=15, pady=(15, 0))

            ctk.CTkLabel(
                card, text=title,
                font=("Segoe UI", 12), text_color=C["muted"],
            ).pack(anchor="w", padx=15, pady=(5, 0))

            lbl = ctk.CTkLabel(
                card, text="0",
                font=("Segoe UI", 32, "bold"), text_color=color,
            )
            lbl.pack(anchor="w", padx=15, pady=(2, 15))
            self.dash_labels[key] = lbl

        # Quick actions
        qa_card = ctk.CTkFrame(p, fg_color=C["card"], corner_radius=12)
        qa_card.pack(fill="both", expand=True, pady=(0, 0))

        ctk.CTkLabel(
            qa_card,
            text="Quick Actions",
            font=("Segoe UI", 16, "bold"),
            text_color=C["text"],
        ).pack(anchor="w", padx=25, pady=(20, 12))

        qa_row = ctk.CTkFrame(qa_card, fg_color=C["transparent"])
        qa_row.pack(anchor="w", padx=20, pady=(0, 20))

        actions = [
            ("📘 Manage Students", self.show_students, C["primary"]),
            ("📗 Manage Courses", self.show_courses, C["secondary"]),
            ("📙 Enroll Students", self.show_enrollments, C["accent"]),
            ("📋 View Reports", self.show_reports, C["danger"]),
            ("⚙️ Settings", self.show_settings, C["card_hover"]),
        ]

        for text, cmd, color in actions:
            ctk.CTkButton(
                qa_row, text=text, command=cmd,
                width=165, height=44,
                fg_color=color, corner_radius=10,
                font=("Segoe UI", 12, "bold"),
            ).pack(side="left", padx=6)

    def show_dashboard(self):
        self._show_page("dashboard", "Dashboard")
        # Update counts
        sc = count_students()
        cc = count_courses()
        ec = count_enrollments()
        self._animate(self.dash_labels["count_students"], sc)
        self._animate(self.dash_labels["count_courses"], cc)
        self._animate(self.dash_labels["count_enrollments"], ec)
        self.dash_labels["zero"].configure(text="0")

    def _animate(self, label, target, current=0):
        if current <= target:
            label.configure(text=str(current))
            self.root.after(25, lambda: self._animate(label, target, current + 1))

    # ============================================================
    #  2. STUDENTS PAGE
    # ============================================================
    def _build_students_page(self):
        p = self.pages["students"]

        # Title row
        title_row = ctk.CTkFrame(p, fg_color=C["transparent"])
        title_row.pack(fill="x", pady=(0, 10))

        tl = ctk.CTkFrame(title_row, fg_color=C["transparent"])
        tl.pack(side="left")

        ctk.CTkLabel(
            tl, text="Students",
            font=("Segoe UI", 26, "bold"), text_color=C["text"],
        ).pack(anchor="w")

        ctk.CTkLabel(
            tl, text="Manage all student records",
            font=("Segoe UI", 12), text_color=C["muted"],
        ).pack(anchor="w")

        ctk.CTkButton(
            title_row, text="+ Add Student",
            command=self._open_add_student_dialog,
            width=140, height=38,
            fg_color=C["primary"], hover_color=C["primary_hover"],
            font=("Segoe UI", 13, "bold"), corner_radius=8,
        ).pack(side="right")

        # Search / filter bar
        filter_bar = ctk.CTkFrame(p, fg_color=C["card"], corner_radius=10, height=50)
        filter_bar.pack(fill="x", pady=(0, 10))
        filter_bar.pack_propagate(False)

        self.student_search = ctk.CTkEntry(
            filter_bar,
            placeholder_text="🔍 Search by name, email, or phone...",
            width=300, height=34,
            fg_color=C["bg"], border_color=C["border"],
            text_color=C["text"],
        )
        self.student_search.pack(side="left", padx=12, pady=8)

        ctk.CTkButton(
            filter_bar, text="Search",
            command=self.search_student,
            width=80, height=34,
            fg_color=C["primary"], hover_color=C["primary_hover"],
        ).pack(side="left", padx=(0, 10))

        self.status_filter = ctk.CTkComboBox(
            filter_bar,
            values=["All Status", "Active", "Graduated", "Suspended"],
            width=130, height=34,
            fg_color=C["bg"], border_color=C["border"],
            text_color=C["text"],
            button_color=C["border"],
            dropdown_fg_color=C["card"],
        )
        self.status_filter.set("All Status")
        self.status_filter.pack(side="left", padx=4)

        ctk.CTkButton(
            filter_bar, text="🔄 Reset",
            command=self.refresh_list,
            width=80, height=34,
            fg_color=C["card_hover"], hover_color=C["border"],
        ).pack(side="left", padx=4)

        # Import / Export
        io_frame = ctk.CTkFrame(filter_bar, fg_color=C["transparent"])
        io_frame.pack(side="right", padx=12)

        ctk.CTkButton(
            io_frame, text="📥 Import CSV",
            command=self.import_csv_gui,
            width=110, height=34,
            fg_color=C["secondary"], hover_color=C["secondary_hover"],
        ).pack(side="left", padx=3)

        ctk.CTkButton(
            io_frame, text="📤 Export CSV",
            command=self.export_csv_gui,
            width=110, height=34,
            fg_color="#7C3AED", hover_color="#6D28D9",
        ).pack(side="left", padx=3)

        # Table
        tree_card = ctk.CTkFrame(p, fg_color=C["card"], corner_radius=10)
        tree_card.pack(fill="both", expand=True)

        cols = ("ID", "Name", "Age", "Email", "Phone", "Gender", "DOB", "Status")
        self.tree = ttk.Treeview(
            tree_card, columns=cols, show="headings", style="Dark.Treeview"
        )

        widths = {
            "ID": 45, "Name": 150, "Age": 45, "Email": 190,
            "Phone": 110, "Gender": 75, "DOB": 100, "Status": 80,
        }
        left = {"Name", "Email"}
        for col, w in widths.items():
            a = "w" if col in left else "center"
            self.tree.heading(col, text=col, anchor=a)
            self.tree.column(col, width=w, minwidth=w, anchor=a, stretch=True)

        sb = ctk.CTkScrollbar(tree_card, orientation="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y", padx=(0, 4), pady=4)
        self.tree.pack(side="left", fill="both", expand=True, padx=(4, 0), pady=4)

        self.tree.bind("<<TreeviewSelect>>", self.load_selected_student)

        # Bottom action bar
        bot_bar = ctk.CTkFrame(p, fg_color=C["transparent"], height=44)
        bot_bar.pack(fill="x", pady=(8, 0))

        ctk.CTkButton(
            bot_bar, text="✏️ Edit Selected",
            command=self._open_edit_student_dialog,
            width=140, height=36,
            fg_color=C["accent"], hover_color=C["accent_hover"],
            font=("Segoe UI", 12),
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            bot_bar, text="🗑️ Delete Selected",
            command=self.delete_student_gui,
            width=140, height=36,
            fg_color=C["danger"], hover_color=C["danger_hover"],
            font=("Segoe UI", 12),
        ).pack(side="left", padx=4)

        self.refresh_list()

    # ── Student form dialog (add / edit) ──
    def _open_student_form(self, title="Add Student", data=None):
        """Open a modal dialog for adding or editing a student."""
        dlg = ctk.CTkToplevel(self.root)
        dlg.title(title)
        dlg.geometry("460x620")
        dlg.resizable(False, False)
        dlg.configure(fg_color=C["bg"])
        dlg.grab_set()
        dlg.lift()
        dlg.focus_force()

        card = ctk.CTkFrame(dlg, fg_color=C["card"], corner_radius=14)
        card.pack(expand=True, fill="both", padx=18, pady=18)

        ctk.CTkLabel(
            card, text=title,
            font=("Segoe UI", 20, "bold"), text_color=C["text"],
        ).pack(pady=(18, 14))

        entries = {}
        fields = [
            ("Name", "name"), ("Age", "age"), ("Email", "email"),
            ("Phone", "phone"), ("DOB (YYYY-MM-DD)", "dob"),
        ]

        for label, key in fields:
            ctk.CTkLabel(
                card, text=label, font=("Segoe UI", 11),
                text_color=C["muted"], anchor="w",
            ).pack(padx=30, anchor="w")

            e = ctk.CTkEntry(
                card, width=380, height=36,
                fg_color=C["bg"], border_color=C["border"],
                text_color=C["text"],
            )
            e.pack(padx=30, pady=(2, 8))
            entries[key] = e

        # Combo boxes
        combo_frame = ctk.CTkFrame(card, fg_color=C["transparent"])
        combo_frame.pack(padx=30, fill="x", pady=(0, 8))

        ctk.CTkLabel(
            combo_frame, text="Gender", font=("Segoe UI", 11),
            text_color=C["muted"],
        ).grid(row=0, column=0, sticky="w")

        gender_cb = ctk.CTkComboBox(
            combo_frame, values=["Male", "Female", "Other"],
            width=170, height=34,
            fg_color=C["bg"], border_color=C["border"],
            text_color=C["text"], button_color=C["border"],
            dropdown_fg_color=C["card"],
        )
        gender_cb.set("Male")
        gender_cb.grid(row=1, column=0, padx=(0, 12), pady=2)

        ctk.CTkLabel(
            combo_frame, text="Status", font=("Segoe UI", 11),
            text_color=C["muted"],
        ).grid(row=0, column=1, sticky="w")

        status_cb = ctk.CTkComboBox(
            combo_frame, values=["Active", "Graduated", "Suspended"],
            width=170, height=34,
            fg_color=C["bg"], border_color=C["border"],
            text_color=C["text"], button_color=C["border"],
            dropdown_fg_color=C["card"],
        )
        status_cb.set("Active")
        status_cb.grid(row=1, column=1, pady=2)

        # Pre-fill if editing
        if data:
            for key, idx in [("name", 1), ("age", 2), ("email", 3), ("phone", 4), ("dob", 6)]:
                if idx < len(data) and data[idx] is not None:
                    entries[key].insert(0, str(data[idx]))
            if len(data) > 5 and data[5]:
                gender_cb.set(str(data[5]))
            if len(data) > 7 and data[7]:
                status_cb.set(str(data[7]))

        result: dict[str, Any] = {"submitted": False}

        def submit():
            result["submitted"] = True
            result["values"] = {
                "name": entries["name"].get().strip(),
                "age": entries["age"].get().strip(),
                "email": entries["email"].get().strip(),
                "phone": entries["phone"].get().strip(),
                "dob": entries["dob"].get().strip(),
                "gender": gender_cb.get(),
                "status": status_cb.get(),
            }
            dlg.destroy()

        ctk.CTkButton(
            card, text="Save" if data else "Add Student",
            command=submit,
            width=380, height=40,
            fg_color=C["primary"], hover_color=C["primary_hover"],
            font=("Segoe UI", 14, "bold"), corner_radius=8,
        ).pack(padx=30, pady=(8, 18))

        dlg.wait_window()
        return result

    def _open_add_student_dialog(self):
        result = self._open_student_form("Add Student")
        if not result["submitted"]:
            return

        v = result["values"]
        if not v["name"] or not v["age"] or not v["email"]:
            self.show_toast("Name, Age, and Email are required", "warning")
            return
        if not v["age"].isdigit():
            self.show_toast("Age must be a number", "warning")
            return

        msg = add_student(
            v["name"], int(v["age"]), v["email"],
            v["phone"], v["gender"], v["dob"], v["status"],
        )
        cat = "success" if "Successfully" in msg else "error"
        self.show_toast(msg, cat)
        self.refresh_list()
        self._refresh_student_options()

    def _open_edit_student_dialog(self):
        sel = self.tree.selection()
        if not sel:
            self.show_toast("Select a student first", "warning")
            return

        data = self.tree.item(sel[0])["values"]
        student_id = data[0]

        result = self._open_student_form("Edit Student", data)
        if not result["submitted"]:
            return

        v = result["values"]
        if not v["name"] or not v["age"] or not v["email"]:
            self.show_toast("Name, Age, and Email are required", "warning")
            return
        if not v["age"].isdigit():
            self.show_toast("Age must be a number", "warning")
            return

        msg = update_student(
            student_id, v["name"], int(v["age"]), v["email"],
            v["phone"], v["gender"], v["dob"], v["status"],
        )
        self.show_toast(msg, "success")
        self.refresh_list()
        self._refresh_student_options()

    def delete_student_gui(self):
        sel = self.tree.selection()
        if not sel:
            self.show_toast("Select a student to delete", "warning")
            return
        data = self.tree.item(sel[0])["values"]
        msg = delete_student(data[0])
        self.show_toast(msg, "info")
        self.refresh_list()
        self._refresh_student_options()
        self._refresh_enrollments_table()

    def load_selected_student(self, event):
        pass  # Selection is used by edit/delete buttons

    def search_student(self):
        kw = self.student_search.get().strip()
        for item in self.tree.get_children():
            self.tree.delete(item)

        rows = search_students(kw) if kw else get_students()

        status = self.status_filter.get()
        if status != "All Status":
            rows = [r for r in rows if len(r) > 7 and r[7] == status]

        for row in rows:
            self.tree.insert("", tk.END, values=row)

    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in get_students():
            self.tree.insert("", tk.END, values=row)

    def _refresh_student_options(self):
        student_option = getattr(self, "student_option", None)
        if student_option is not None:
            student_option.configure(
                values=[f"{s[0]} - {s[1]}" for s in get_students()]
            )

    def export_csv_gui(self):
        path = export_students_to_csv()
        if path:
            self.show_toast("Students exported to CSV!", "success")

    def import_csv_gui(self):
        fp, count = import_students_from_csv()
        if fp:
            self.refresh_list()
            self._refresh_student_options()
            self.show_toast(f"Imported {count} students!", "success")

    def show_students(self):
        self._show_page("students", "Students")
        self.refresh_list()

    # ============================================================
    #  3. COURSES PAGE
    # ============================================================
    def _build_courses_page(self):
        p = self.pages["courses"]

        # Title row
        title_row = ctk.CTkFrame(p, fg_color=C["transparent"])
        title_row.pack(fill="x", pady=(0, 10))

        tl = ctk.CTkFrame(title_row, fg_color=C["transparent"])
        tl.pack(side="left")

        ctk.CTkLabel(
            tl, text="Courses",
            font=("Segoe UI", 26, "bold"), text_color=C["text"],
        ).pack(anchor="w")

        ctk.CTkLabel(
            tl, text="Manage course details",
            font=("Segoe UI", 12), text_color=C["muted"],
        ).pack(anchor="w")

        ctk.CTkButton(
            title_row, text="+ Add Course",
            command=self._open_add_course_dialog,
            width=140, height=38,
            fg_color=C["secondary"], hover_color=C["secondary_hover"],
            font=("Segoe UI", 13, "bold"), corner_radius=8,
        ).pack(side="right")

        # Filter bar
        filter_bar = ctk.CTkFrame(p, fg_color=C["card"], corner_radius=10, height=50)
        filter_bar.pack(fill="x", pady=(0, 10))
        filter_bar.pack_propagate(False)

        self.course_dept_filter = ctk.CTkComboBox(
            filter_bar,
            values=["All Departments", "Science", "Commerce", "Arts"],
            width=160, height=34,
            fg_color=C["bg"], border_color=C["border"],
            text_color=C["text"], button_color=C["border"],
            dropdown_fg_color=C["card"],
        )
        self.course_dept_filter.set("All Departments")
        self.course_dept_filter.pack(side="left", padx=12, pady=8)

        ctk.CTkButton(
            filter_bar, text="🔄 Reset",
            command=self.refresh_courses,
            width=80, height=34,
            fg_color=C["card_hover"], hover_color=C["border"],
        ).pack(side="left", padx=4)

        # Table
        tree_card = ctk.CTkFrame(p, fg_color=C["card"], corner_radius=10)
        tree_card.pack(fill="both", expand=True)

        cols = ("ID", "Course Name", "Course Code", "Department", "Duration")
        self.course_table = ttk.Treeview(
            tree_card, columns=cols, show="headings", style="Dark.Treeview"
        )

        widths = {"ID": 50, "Course Name": 220, "Course Code": 120, "Department": 160, "Duration": 120}
        for col, w in widths.items():
            a = "w" if col == "Course Name" else "center"
            self.course_table.heading(col, text=col, anchor=a)
            self.course_table.column(col, width=w, minwidth=w, anchor=a, stretch=True)

        sb = ctk.CTkScrollbar(tree_card, orientation="vertical", command=self.course_table.yview)
        self.course_table.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y", padx=(0, 4), pady=4)
        self.course_table.pack(side="left", fill="both", expand=True, padx=(4, 0), pady=4)

        self.refresh_courses()

    def _open_add_course_dialog(self):
        dlg = ctk.CTkToplevel(self.root)
        dlg.title("Add Course")
        dlg.geometry("420x520")
        dlg.resizable(False, False)
        dlg.configure(fg_color=C["bg"])
        dlg.grab_set()
        dlg.lift()
        dlg.focus_force()

        card = ctk.CTkFrame(dlg, fg_color=C["card"], corner_radius=14)
        card.pack(expand=True, fill="both", padx=18, pady=18)

        ctk.CTkLabel(
            card, text="Add Course",
            font=("Segoe UI", 20, "bold"), text_color=C["text"],
        ).pack(pady=(18, 14))

        entries = {}
        for label, key in [("Course Name", "name"), ("Course Code", "code"), ("Department", "dept"), ("Duration", "dur")]:
            ctk.CTkLabel(
                card, text=label, font=("Segoe UI", 11),
                text_color=C["muted"], anchor="w",
            ).pack(padx=30, anchor="w")

            e = ctk.CTkEntry(
                card, width=340, height=36,
                fg_color=C["bg"], border_color=C["border"],
                text_color=C["text"],
                placeholder_text=f"Enter {label.lower()}",
            )
            e.pack(padx=30, pady=(2, 8))
            entries[key] = e

        def submit():
            name = entries["name"].get().strip()
            code = entries["code"].get().strip()
            dept = entries["dept"].get().strip()
            dur = entries["dur"].get().strip()

            if not name or not code:
                self.show_toast("Course Name and Code are required", "warning")
                return

            msg = add_course(name, code, dept, dur)
            cat = "success" if "Added" in msg else "error"
            self.show_toast(msg, cat)
            self.refresh_courses()
            self._refresh_course_options()
            dlg.destroy()

        ctk.CTkButton(
            card, text="Add Course", command=submit,
            width=340, height=40,
            fg_color=C["secondary"], hover_color=C["secondary_hover"],
            font=("Segoe UI", 14, "bold"), corner_radius=8,
        ).pack(padx=30, pady=(8, 18))

    def refresh_courses(self):
        for item in self.course_table.get_children():
            self.course_table.delete(item)
        for row in get_courses():
            self.course_table.insert("", tk.END, values=row)

    def _refresh_course_options(self):
        course_option = getattr(self, "course_option", None)
        if course_option is not None:
            course_option.configure(
                values=[f"{c[0]} - {c[1]}" for c in get_courses()]
            )

    def show_courses(self):
        self._show_page("courses", "Courses")
        self.refresh_courses()

    # ============================================================
    #  4. ENROLLMENT PAGE
    # ============================================================
    def _build_enrollment_page(self):
        p = self.pages["enrollment"]

        # Title
        title_row = ctk.CTkFrame(p, fg_color=C["transparent"])
        title_row.pack(fill="x", pady=(0, 10))

        tl = ctk.CTkFrame(title_row, fg_color=C["transparent"])
        tl.pack(side="left")

        ctk.CTkLabel(
            tl, text="Enrollment",
            font=("Segoe UI", 26, "bold"), text_color=C["text"],
        ).pack(anchor="w")

        ctk.CTkLabel(
            tl, text="Assign students to courses",
            font=("Segoe UI", 12), text_color=C["muted"],
        ).pack(anchor="w")

        ctk.CTkButton(
            title_row, text="+ New Enrollment",
            command=self._open_enroll_dialog,
            width=160, height=38,
            fg_color=C["primary"], hover_color=C["primary_hover"],
            font=("Segoe UI", 13, "bold"), corner_radius=8,
        ).pack(side="right")

        # Grade assignment bar
        grade_card = ctk.CTkFrame(p, fg_color=C["card"], corner_radius=10, height=55)
        grade_card.pack(fill="x", pady=(0, 10))
        grade_card.pack_propagate(False)

        ctk.CTkLabel(
            grade_card, text="Assign Grade:",
            font=("Segoe UI", 12, "bold"), text_color=C["muted"],
        ).pack(side="left", padx=12, pady=10)

        self.marks_entry = ctk.CTkEntry(
            grade_card, placeholder_text="Marks (0-100)",
            width=130, height=34,
            fg_color=C["bg"], border_color=C["border"],
            text_color=C["text"],
        )
        self.marks_entry.pack(side="left", padx=4)

        self.grade_option = ctk.CTkComboBox(
            grade_card, values=["A+", "A", "B+", "B", "C", "D", "F"],
            width=100, height=34,
            fg_color=C["bg"], border_color=C["border"],
            text_color=C["text"], button_color=C["border"],
            dropdown_fg_color=C["card"],
        )
        self.grade_option.pack(side="left", padx=4)

        ctk.CTkButton(
            grade_card, text="Assign Grade",
            command=self.assign_grade_gui,
            width=120, height=34,
            fg_color=C["accent"], hover_color=C["accent_hover"],
        ).pack(side="left", padx=8)

        # Export buttons
        ctk.CTkButton(
            grade_card, text="📊 Excel",
            command=self.export_excel,
            width=90, height=34,
            fg_color=C["secondary"], hover_color=C["secondary_hover"],
        ).pack(side="right", padx=(4, 12))

        ctk.CTkButton(
            grade_card, text="📄 PDF",
            command=self.export_pdf,
            width=80, height=34,
            fg_color=C["danger"], hover_color=C["danger_hover"],
        ).pack(side="right", padx=4)

        # Table
        tree_card = ctk.CTkFrame(p, fg_color=C["card"], corner_radius=10)
        tree_card.pack(fill="both", expand=True)

        cols = ("ID", "Student", "Course", "Marks", "Grade")
        self.enrollment_table = ttk.Treeview(
            tree_card, columns=cols, show="headings", style="Dark.Treeview"
        )
        self.enrollment_table.heading("ID", text="ID")
        self.enrollment_table.heading("Student", text="Student")
        self.enrollment_table.heading("Course", text="Course")
        self.enrollment_table.heading("Marks", text="Marks")
        self.enrollment_table.heading("Grade", text="Grade")
        self.enrollment_table.column("ID", width=50, anchor="center")
        self.enrollment_table.column("Student", width=200, anchor="w")
        self.enrollment_table.column("Course", width=200, anchor="w")
        self.enrollment_table.column("Marks", width=80, anchor="center")
        self.enrollment_table.column("Grade", width=80, anchor="center")

        sb = ctk.CTkScrollbar(tree_card, orientation="vertical", command=self.enrollment_table.yview)
        self.enrollment_table.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y", padx=(0, 4), pady=4)
        self.enrollment_table.pack(side="left", fill="both", expand=True, padx=(4, 0), pady=4)

        self.enrollment_table.bind("<<TreeviewSelect>>", self._load_selected_enrollment)

        self._refresh_enrollments_table()

    def _open_enroll_dialog(self):
        dlg = ctk.CTkToplevel(self.root)
        dlg.title("Enroll Student")
        dlg.geometry("440x320")
        dlg.resizable(False, False)
        dlg.configure(fg_color=C["bg"])
        dlg.grab_set()
        dlg.lift()
        dlg.focus_force()

        card = ctk.CTkFrame(dlg, fg_color=C["card"], corner_radius=14)
        card.pack(expand=True, fill="both", padx=18, pady=18)

        ctk.CTkLabel(
            card, text="New Enrollment",
            font=("Segoe UI", 20, "bold"), text_color=C["text"],
        ).pack(pady=(18, 14))

        ctk.CTkLabel(
            card, text="Select Student", font=("Segoe UI", 11),
            text_color=C["muted"], anchor="w",
        ).pack(padx=30, anchor="w")

        student_cb = ctk.CTkComboBox(
            card,
            values=[f"{s[0]} - {s[1]}" for s in get_students()],
            width=360, height=36,
            fg_color=C["bg"], border_color=C["border"],
            text_color=C["text"], button_color=C["border"],
            dropdown_fg_color=C["card"],
        )
        student_cb.pack(padx=30, pady=(2, 10))

        ctk.CTkLabel(
            card, text="Select Course", font=("Segoe UI", 11),
            text_color=C["muted"], anchor="w",
        ).pack(padx=30, anchor="w")

        course_cb = ctk.CTkComboBox(
            card,
            values=[f"{c[0]} - {c[1]}" for c in get_courses()],
            width=360, height=36,
            fg_color=C["bg"], border_color=C["border"],
            text_color=C["text"], button_color=C["border"],
            dropdown_fg_color=C["card"],
        )
        course_cb.pack(padx=30, pady=(2, 14))

        def submit():
            sv = student_cb.get()
            cv = course_cb.get()
            if not sv or not cv:
                self.show_toast("Select student and course", "warning")
                return
            try:
                sid = int(sv.split(" - ")[0])
                cid = int(cv.split(" - ")[0])
            except Exception:
                self.show_toast("Invalid selection", "error")
                return
            msg = enroll_student(sid, cid)
            cat = "success" if "Successful" in msg else "error"
            self.show_toast(msg, cat)
            self._refresh_enrollments_table()
            dlg.destroy()

        ctk.CTkButton(
            card, text="Enroll Now", command=submit,
            width=360, height=40,
            fg_color=C["primary"], hover_color=C["primary_hover"],
            font=("Segoe UI", 14, "bold"), corner_radius=8,
        ).pack(padx=30, pady=(0, 18))

    def assign_grade_gui(self):
        sel = self.enrollment_table.selection()
        if not sel:
            self.show_toast("Select an enrollment", "warning")
            return

        marks_text = self.marks_entry.get().strip()
        try:
            marks = float(marks_text)
        except ValueError:
            self.show_toast("Marks must be 0-100", "warning")
            return

        if not 0 <= marks <= 100:
            self.show_toast("Marks must be 0-100", "warning")
            return

        grade = self.grade_option.get()
        if not grade:
            self.show_toast("Select a grade", "warning")
            return

        eid = self.enrollment_table.item(sel[0])["values"][0]
        msg = update_grade(eid, marks, grade)
        self.show_toast(msg, "success")
        self._refresh_enrollments_table()

    def _load_selected_enrollment(self, event):
        sel = self.enrollment_table.selection()
        if not sel:
            return
        data = self.enrollment_table.item(sel[0])["values"]
        self.marks_entry.delete(0, tk.END)
        self.marks_entry.insert(0, str(data[3]) if data[3] else "")
        self.grade_option.set(str(data[4]) if data[4] else "N/A")

    def _refresh_enrollments_table(self):
        for item in self.enrollment_table.get_children():
            self.enrollment_table.delete(item)
        for row in get_enrollments():
            self.enrollment_table.insert("", tk.END, values=row)

    def export_excel(self):
        f = export_students_excel()
        self.show_toast(f"Saved as {f}", "success")

    def export_pdf(self):
        f = export_students_pdf()
        self.show_toast(f"Saved as {f}", "success")

    def show_enrollments(self):
        self._show_page("enrollment", "Enrollment")
        self._refresh_enrollments_table()

    # ============================================================
    #  5. REPORTS PAGE
    # ============================================================
    def _build_reports_page(self):
        p = self.pages["reports"]

        ctk.CTkLabel(
            p, text="Reports",
            font=("Segoe UI", 26, "bold"), text_color=C["text"],
        ).pack(anchor="w")

        ctk.CTkLabel(
            p, text="View and export student data",
            font=("Segoe UI", 12), text_color=C["muted"],
        ).pack(anchor="w", pady=(0, 20))

        grid = ctk.CTkFrame(p, fg_color=C["transparent"])
        grid.pack(fill="both", expand=True)

        report_cards = [
            ("📘", "Students Report", "View total students and\ntheir details", C["primary"], self.show_students),
            ("📗", "Courses Report", "View courses and\nenrollment stats", C["secondary"], self.show_courses),
            ("📙", "Enrollment Report", "View enrollment details\nand progress", C["accent"], self.show_enrollments),
            ("📕", "Export Data", "Download in Excel or PDF\nformat", C["danger"], self.export_excel),
        ]

        for i, (icon, title, desc, color, cmd) in enumerate(report_cards):
            row, col = divmod(i, 2)

            card = ctk.CTkFrame(grid, fg_color=C["card"], corner_radius=12)
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            grid.grid_columnconfigure(col, weight=1)
            grid.grid_rowconfigure(row, weight=1)

            inner = ctk.CTkFrame(card, fg_color=C["transparent"])
            inner.pack(expand=True, pady=20)

            ctk.CTkLabel(
                inner, text=icon, font=("Segoe UI", 40),
            ).pack(pady=(0, 8))

            ctk.CTkLabel(
                inner, text=title,
                font=("Segoe UI", 16, "bold"), text_color=C["text"],
            ).pack(pady=(0, 4))

            ctk.CTkLabel(
                inner, text=desc,
                font=("Segoe UI", 11), text_color=C["muted"],
                justify="center",
            ).pack(pady=(0, 12))

            ctk.CTkButton(
                inner, text="View", command=cmd,
                width=120, height=34,
                fg_color=color, corner_radius=8,
                font=("Segoe UI", 12, "bold"),
            ).pack()

    def show_reports(self):
        self._show_page("reports", "Reports")

    # ============================================================
    #  6. SETTINGS PAGE
    # ============================================================
    def _build_settings_page(self):
        p = self.pages["settings"]

        ctk.CTkLabel(
            p, text="Settings",
            font=("Segoe UI", 26, "bold"), text_color=C["text"],
        ).pack(anchor="w")

        ctk.CTkLabel(
            p, text="Customize your application",
            font=("Segoe UI", 12), text_color=C["muted"],
        ).pack(anchor="w", pady=(0, 20))

        # Settings cards with working buttons
        settings_items = [
            ("👤", "Profile Settings", "Update your profile information", self._open_profile_settings),
            ("🖥️", "Application Settings", "Toggle appearance mode", self._open_app_settings),
            ("🗄️", "Database Settings", "Backup & manage database", self._open_db_settings),
            ("🔔", "Notification Settings", "Email & notification preferences", self._open_notif_settings),
            ("🔒", "Security Settings", "Change password & security", self._open_security_settings),
        ]

        for icon, title, desc, cmd in settings_items:
            card = ctk.CTkFrame(p, fg_color=C["card"], corner_radius=10, height=70)
            card.pack(fill="x", pady=5)
            card.pack_propagate(False)

            left = ctk.CTkFrame(card, fg_color=C["transparent"])
            left.pack(side="left", padx=20, pady=15)

            ctk.CTkLabel(
                left, text=f"{icon}  {title}",
                font=("Segoe UI", 14, "bold"), text_color=C["text"],
            ).pack(anchor="w")

            ctk.CTkLabel(
                left, text=desc,
                font=("Segoe UI", 11), text_color=C["muted"],
            ).pack(anchor="w")

            ctk.CTkButton(
                card, text="→", command=cmd,
                width=40, height=34,
                fg_color=C["card_hover"], hover_color=C["border"],
                corner_radius=8,
            ).pack(side="right", padx=20)

    # ── Settings Dialogs ──

    def _settings_dialog(self, title, width=440, height=350):
        dlg = ctk.CTkToplevel(self.root)
        dlg.title(title)
        dlg.geometry(f"{width}x{height}")
        dlg.resizable(False, False)
        dlg.configure(fg_color=C["bg"])
        dlg.grab_set()
        dlg.lift()
        dlg.focus_force()
        card = ctk.CTkFrame(dlg, fg_color=C["card"], corner_radius=14)
        card.pack(expand=True, fill="both", padx=18, pady=18)
        ctk.CTkLabel(
            card, text=title,
            font=("Segoe UI", 20, "bold"), text_color=C["text"],
        ).pack(pady=(18, 14))
        return dlg, card

    def _open_profile_settings(self):
        from database import connect
        dlg, card = self._settings_dialog("Profile Settings", 440, 380)

        conn = connect()
        cur = conn.cursor()
        cur.execute("SELECT username, email FROM admins LIMIT 1")
        row = cur.fetchone()
        conn.close()

        ctk.CTkLabel(card, text="Username", font=("Segoe UI", 11), text_color=C["muted"]).pack(padx=30, anchor="w")
        uname = ctk.CTkEntry(card, width=360, height=36, fg_color=C["bg"], border_color=C["border"], text_color=C["text"])
        uname.pack(padx=30, pady=(2, 8))
        if row and row[0]:
            uname.insert(0, row[0])

        ctk.CTkLabel(card, text="Email", font=("Segoe UI", 11), text_color=C["muted"]).pack(padx=30, anchor="w")
        email = ctk.CTkEntry(card, width=360, height=36, fg_color=C["bg"], border_color=C["border"], text_color=C["text"])
        email.pack(padx=30, pady=(2, 8))
        if row and row[1]:
            email.insert(0, row[1])

        def save():
            new_u = uname.get().strip()
            new_e = email.get().strip()
            if not new_u:
                self.show_toast("Username cannot be empty", "warning")
                return
            conn2 = connect()
            cur2 = conn2.cursor()
            cur2.execute("UPDATE admins SET username=?, email=? WHERE username=?", (new_u, new_e, row[0]))
            conn2.commit()
            conn2.close()
            self.show_toast("Profile updated!", "success")
            dlg.destroy()

        ctk.CTkButton(card, text="Save Changes", command=save, width=360, height=40,
                       fg_color=C["primary"], hover_color=C["primary_hover"],
                       font=("Segoe UI", 14, "bold"), corner_radius=8).pack(padx=30, pady=(12, 18))

    def _open_app_settings(self):
        dlg, card = self._settings_dialog("Application Settings", 440, 300)

        ctk.CTkLabel(card, text="Appearance Mode", font=("Segoe UI", 12), text_color=C["muted"]).pack(padx=30, anchor="w", pady=(5, 0))

        mode_var = ctk.StringVar(value=ctk.get_appearance_mode())
        mode_cb = ctk.CTkComboBox(
            card, values=["Dark", "Light", "System"],
            variable=mode_var, width=360, height=36,
            fg_color=C["bg"], border_color=C["border"],
            text_color=C["text"], button_color=C["border"],
            dropdown_fg_color=C["card"],
        )
        mode_cb.pack(padx=30, pady=(4, 12))

        def apply_mode():
            ctk.set_appearance_mode(mode_var.get().lower())
            self.show_toast(f"Appearance set to {mode_var.get()}", "success")
            dlg.destroy()

        ctk.CTkButton(card, text="Apply", command=apply_mode, width=360, height=40,
                       fg_color=C["primary"], hover_color=C["primary_hover"],
                       font=("Segoe UI", 14, "bold"), corner_radius=8).pack(padx=30, pady=(5, 18))

    def _open_db_settings(self):
        import os, shutil
        dlg, card = self._settings_dialog("Database Settings", 440, 340)

        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "school.db")
        db_size = os.path.getsize(db_path) / 1024 if os.path.exists(db_path) else 0

        ctk.CTkLabel(card, text=f"Database: school.db", font=("Segoe UI", 12), text_color=C["text"]).pack(padx=30, anchor="w", pady=(5, 0))
        ctk.CTkLabel(card, text=f"Size: {db_size:.1f} KB", font=("Segoe UI", 11), text_color=C["muted"]).pack(padx=30, anchor="w", pady=(2, 0))
        ctk.CTkLabel(card, text=f"Path: {db_path}", font=("Segoe UI", 10), text_color=C["muted"], wraplength=370).pack(padx=30, anchor="w", pady=(2, 15))

        def backup():
            backup_name = f"school_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            backup_path = os.path.join(os.path.dirname(db_path), backup_name)
            shutil.copy2(db_path, backup_path)
            self.show_toast(f"Backup saved as {backup_name}", "success")

        ctk.CTkButton(card, text="📦 Create Backup", command=backup, width=360, height=40,
                       fg_color=C["secondary"], hover_color=C["secondary_hover"],
                       font=("Segoe UI", 13, "bold"), corner_radius=8).pack(padx=30, pady=(5, 8))

        ctk.CTkButton(card, text="Close", command=dlg.destroy, width=360, height=36,
                       fg_color=C["card_hover"], hover_color=C["border"],
                       corner_radius=8).pack(padx=30, pady=(0, 18))

    def _open_notif_settings(self):
        dlg, card = self._settings_dialog("Notification Settings", 440, 340)

        ctk.CTkLabel(card, text="Sender Email", font=("Segoe UI", 11), text_color=C["muted"]).pack(padx=30, anchor="w")
        email_entry = ctk.CTkEntry(card, width=360, height=36, fg_color=C["bg"], border_color=C["border"], text_color=C["text"])
        email_entry.pack(padx=30, pady=(2, 8))
        email_entry.insert(0, "Studentadmin45@gmail.com")

        ctk.CTkLabel(card, text="App Password", font=("Segoe UI", 11), text_color=C["muted"]).pack(padx=30, anchor="w")
        pass_entry = ctk.CTkEntry(card, width=360, height=36, fg_color=C["bg"], border_color=C["border"], text_color=C["text"], show="*")
        pass_entry.pack(padx=30, pady=(2, 12))

        def test_email():
            from otp import generate_otp, send_otp
            otp = generate_otp()
            ok = send_otp(email_entry.get().strip(), otp)
            if ok:
                self.show_toast("Test email sent successfully!", "success")
            else:
                self.show_toast("Failed to send test email", "error")

        ctk.CTkButton(card, text="📧 Send Test Email", command=test_email, width=360, height=40,
                       fg_color=C["accent"], hover_color=C["accent_hover"],
                       font=("Segoe UI", 13, "bold"), corner_radius=8).pack(padx=30, pady=(5, 18))

    def _open_security_settings(self):
        from database import connect
        dlg, card = self._settings_dialog("Security Settings", 440, 420)

        ctk.CTkLabel(card, text="Current Password", font=("Segoe UI", 11), text_color=C["muted"]).pack(padx=30, anchor="w")
        cur_pass = ctk.CTkEntry(card, width=360, height=36, fg_color=C["bg"], border_color=C["border"], text_color=C["text"], show="*")
        cur_pass.pack(padx=30, pady=(2, 8))

        ctk.CTkLabel(card, text="New Password", font=("Segoe UI", 11), text_color=C["muted"]).pack(padx=30, anchor="w")
        new_pass = ctk.CTkEntry(card, width=360, height=36, fg_color=C["bg"], border_color=C["border"], text_color=C["text"], show="*")
        new_pass.pack(padx=30, pady=(2, 8))

        ctk.CTkLabel(card, text="Confirm New Password", font=("Segoe UI", 11), text_color=C["muted"]).pack(padx=30, anchor="w")
        conf_pass = ctk.CTkEntry(card, width=360, height=36, fg_color=C["bg"], border_color=C["border"], text_color=C["text"], show="*")
        conf_pass.pack(padx=30, pady=(2, 12))

        def change_pass():
            old = cur_pass.get().strip()
            new = new_pass.get().strip()
            confirm = conf_pass.get().strip()

            if not old or not new or not confirm:
                self.show_toast("Please fill all fields", "warning")
                return
            if new != confirm:
                self.show_toast("New passwords do not match", "error")
                return

            conn = connect()
            cur = conn.cursor()
            cur.execute("SELECT password FROM admins WHERE password=?", (old,))
            if not cur.fetchone():
                conn.close()
                self.show_toast("Current password is incorrect", "error")
                return

            cur.execute("UPDATE admins SET password=? WHERE password=?", (new, old))
            conn.commit()
            conn.close()
            self.show_toast("Password changed successfully!", "success")
            dlg.destroy()

        ctk.CTkButton(card, text="Update Password", command=change_pass, width=360, height=40,
                       fg_color=C["primary"], hover_color=C["primary_hover"],
                       font=("Segoe UI", 14, "bold"), corner_radius=8).pack(padx=30, pady=(5, 18))

    def show_settings(self):
        self._show_page("settings", "Settings")

    # ============================================================
    #  LOGOUT PAGE
    # ============================================================
    def _build_logout_page(self):
        p = self.pages["logout"]

        card = ctk.CTkFrame(p, fg_color=C["card"], corner_radius=15, width=450, height=280)
        card.pack(expand=True, pady=60, padx=40)
        card.pack_propagate(False)

        ctk.CTkLabel(
            card, text="Account Logout",
            font=("Segoe UI", 26, "bold"), text_color=C["text"],
        ).pack(pady=(30, 10))

        ctk.CTkLabel(
            card, text="Are you sure you want to end your session?",
            font=("Segoe UI", 14), text_color=C["muted"],
        ).pack(pady=(0, 10))

        ctk.CTkLabel(
            card, text="You will be returned to the login screen.",
            font=("Segoe UI", 12), text_color=C["border"],
        ).pack(pady=(0, 25))

        btn_frame = ctk.CTkFrame(card, fg_color=C["transparent"])
        btn_frame.pack(pady=10)

        ctk.CTkButton(
            btn_frame, text="Confirm Logout",
            fg_color=C["danger"], hover_color=C["danger_hover"],
            width=150, height=40,
            command=self.perform_logout,
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame, text="Cancel",
            fg_color=C["card_hover"], hover_color=C["border"],
            width=150, height=40,
            command=self.show_dashboard,
        ).pack(side="left", padx=10)

    def show_logout(self):
        self._show_page("logout")

    def perform_logout(self):
        if self.on_logout:
            self.on_logout()
        else:
            for widget in self.root.winfo_children():
                widget.destroy()
            from login import LoginWindow
            LoginWindow(self.root)

    # ============================================================
    #  TOAST NOTIFICATION
    # ============================================================
    def show_toast(self, message, category="info"):
        colors = {
            "success": C["secondary"],
            "error": C["danger"],
            "warning": C["accent"],
            "info": C["primary"],
        }
        color = colors.get(category, C["primary"])

        toast = ctk.CTkFrame(self.root, fg_color=color, corner_radius=8)
        lbl = ctk.CTkLabel(
            toast, text=message,
            text_color="white", font=("Segoe UI", 12, "bold"),
        )
        lbl.pack(padx=20, pady=10)
        toast.place(relx=0.97, rely=0.93, anchor="se")
        self.root.after(3000, toast.destroy)


if __name__ == "__main__":
    root = ctk.CTk()
    app = App(root)
    root.mainloop()

