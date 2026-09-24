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

        ctk.CTkLabel(
            card, text="🔐", font=("Segoe UI", 42)
        ).pack(pady=(25, 5))

        ctk.CTkLabel(
            card,
            text="OTP Verification",
            font=("Segoe UI", 20, "bold"),
            text_color="#F8FAFC",
        ).pack(pady=(0, 5))

        ctk.CTkLabel(
            card,
            text="Enter the 6-digit OTP sent to your email",
            font=("Segoe UI", 12),
            text_color="#94A3B8",
        ).pack(pady=(0, 15))

        self.otp_entry = ctk.CTkEntry(
            card,
            placeholder_text="Enter OTP",
            width=280, height=42,
            fg_color="#0F172A", border_color="#334155",
            text_color="#F8FAFC",
            font=("Segoe UI", 16),
            justify="center",
        )
        self.otp_entry.pack(pady=8)

        ctk.CTkButton(
            card,
            text="Verify OTP",
            command=self.verify_otp,
            width=280, height=42,
            fg_color="#6366F1",
            hover_color="#4F46E5",
            font=("Segoe UI", 14, "bold"),
            corner_radius=8,
        ).pack(pady=(15, 20))

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
            # Close this OTP toplevel window
            try:
                self.root.grab_release()
            except Exception:
                pass
            self.root.destroy()

            if on_success:
                on_success()
        else:
            messagebox.showerror("Error", "Invalid OTP", parent=self.root)
