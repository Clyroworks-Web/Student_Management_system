import customtkinter as ctk
from tkinter import messagebox
from database import connect
from auth import hash_password


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

        # Scramble the new password before saving
        hashed_new_pass = hash_password(new_password)
        cursor.execute("UPDATE admins SET password=? WHERE username=?", (hashed_new_pass, self.username))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Password updated successfully.", parent=self.root)
        self.on_close()
        if self.on_success:
            self.on_success()