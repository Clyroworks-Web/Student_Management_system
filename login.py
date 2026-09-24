import customtkinter as ctk
from tkinter import messagebox
from auth import hash_password
from database import connect
from otp import generate_otp, send_otp
from otp_window import OTPWindow
from reset_password import ResetPasswordWindow

try:
    from ui import App
except Exception:  # pragma: no cover - UI import is resolved lazily at runtime
    App = None


class LoginWindow:

    def __init__(self, root, on_success=None):
        self.root = root
        self.on_success = on_success
        self.reset_username = None
        self._reset_username = None
        self.setup_ui()

    def setup_ui(self):
        self.root.title("Student Management System")
        self.root.configure(fg_color="#0F172A")

        # Center card
        card = ctk.CTkFrame(self.root, fg_color="#1E293B", corner_radius=16, width=380, height=460)
        card.pack(expand=True, pady=30, padx=35)
        card.pack_propagate(False)

        # Logo / Icon area
        ctk.CTkLabel(
            card, text="🎓", font=("Segoe UI", 48)
        ).pack(pady=(30, 5))

        ctk.CTkLabel(
            card,
            text="Student Management",
            font=("Segoe UI", 22, "bold"),
            text_color="#F8FAFC",
        ).pack(pady=(0, 2))

        ctk.CTkLabel(
            card,
            text="Sign in to your account",
            font=("Segoe UI", 13),
            text_color="#94A3B8",
        ).pack(pady=(0, 25))

        # Username
        ctk.CTkLabel(
            card, text="Username", font=("Segoe UI", 12),
            text_color="#94A3B8", anchor="w"
        ).pack(padx=30, anchor="w")

        self.username = ctk.CTkEntry(
            card,
            placeholder_text="Enter username",
            width=320, height=40,
            fg_color="#0F172A", border_color="#334155",
            text_color="#F8FAFC",
        )
        self.username.pack(padx=30, pady=(4, 12))

        # Password
        ctk.CTkLabel(
            card, text="Password", font=("Segoe UI", 12),
            text_color="#94A3B8", anchor="w"
        ).pack(padx=30, anchor="w")

        self.password = ctk.CTkEntry(
            card,
            placeholder_text="Enter password",
            show="*",
            width=320, height=40,
            fg_color="#0F172A", border_color="#334155",
            text_color="#F8FAFC",
        )
        self.password.pack(padx=30, pady=(4, 20))

        # Login Button
        ctk.CTkButton(
            card,
            text="Sign In",
            command=self.login,
            width=320, height=42,
            fg_color="#6366F1",
            hover_color="#4F46E5",
            font=("Segoe UI", 14, "bold"),
            corner_radius=8,
        ).pack(padx=30)

        # Forgot Password
        ctk.CTkButton(
            card,
            text="Forgot Password?",
            command=self.forgot_password,
            width=320, height=30,
            fg_color="transparent",
            hover_color="#1E293B",
            text_color="#6366F1",
            font=("Segoe UI", 12),
        ).pack(pady=(10, 15))

    def open_dashboard(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        if App is not None:
            App(self.root, on_logout=self.on_app_logout)

    def on_app_logout(self):
        if hasattr(self, "root") and self.root is not None:
            for widget in self.root.winfo_children():
                widget.destroy()
        self.setup_ui()

    def login(self):
        username = self.username.get().strip()
        password = self.password.get().strip()
        hashed_password = hash_password(password)

        conn = connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT email FROM admins WHERE username=? AND password=?",
            (username, hashed_password),
        )
        admin = cursor.fetchone()
        conn.close()

        if admin and admin[0]:
            otp = generate_otp()
            success = send_otp(admin[0], otp)

            if success:
                messagebox.showinfo("Success", "OTP sent successfully")
                otp_root = ctk.CTkToplevel(self.root)
                OTPWindow(otp_root, otp, on_success=self._on_otp_verified)
            else:
                messagebox.showerror("Error", "Failed to send OTP")
        else:
            messagebox.showerror("Error", "Invalid Username or Password")

    def _on_otp_verified(self):
        """Called when login OTP is verified successfully."""
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

        ctk.CTkLabel(
            card, text="🔑", font=("Segoe UI", 36)
        ).pack(pady=(20, 5))

        ctk.CTkLabel(
            card,
            text="Forgot Password",
            font=("Segoe UI", 20, "bold"),
            text_color="#F8FAFC",
        ).pack(pady=(0, 5))

        ctk.CTkLabel(
            card,
            text="Enter your username to receive an OTP",
            font=("Segoe UI", 12),
            text_color="#94A3B8",
        ).pack(pady=(0, 15))

        self.fp_username = ctk.CTkEntry(
            card,
            placeholder_text="Username",
            width=300, height=40,
            fg_color="#0F172A", border_color="#334155",
            text_color="#F8FAFC",
        )
        self.fp_username.pack(pady=5)

        ctk.CTkButton(
            card,
            text="Send OTP",
            command=self.send_reset_otp,
            width=300, height=40,
            fg_color="#6366F1",
            hover_color="#4F46E5",
            font=("Segoe UI", 13, "bold"),
        ).pack(pady=(15, 20))

    def send_reset_otp(self):
        username = self.fp_username.get().strip()

        if not username:
            messagebox.showwarning(
                "Warning", "Please enter a username.",
                parent=self.forget_window,
            )
            return

        conn = connect()
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM admins WHERE username=?", (username,))
        result = cursor.fetchone()
        conn.close()

        if not result or not result[0]:
            messagebox.showwarning(
                "Warning",
                f"No account found for username: {username}",
                parent=self.forget_window,
            )
            return

        receiver_email = result[0]
        otp = generate_otp()
        success = send_otp(receiver_email, otp)

        if success:
            messagebox.showinfo(
                "Success", "OTP sent successfully!",
                parent=self.forget_window,
            )
            self.reset_username = username
            self._reset_username = username
            self.forget_window.withdraw()
            otp_root = ctk.CTkToplevel(self.root)
            OTPWindow(otp_root, otp, on_success=self.open_reset_password)
        else:
            messagebox.showerror(
                "Error", "Failed to send OTP.",
                parent=self.forget_window,
            )
            try:
                self.forget_window.grab_release()
            except Exception:
                pass
            self.forget_window.destroy()

    def open_reset_password(self):
        username = getattr(self, "_reset_username", getattr(self, "reset_username", None))

        try:
            self.forget_window.grab_release()
        except Exception:
            pass
        self.forget_window.destroy()

        reset_root = ctk.CTkToplevel(self.root)
        ResetPasswordWindow(reset_root, username)


if __name__ == "__main__":
    root = ctk.CTk()
    LoginWindow(root)
    root.mainloop()