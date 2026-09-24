import customtkinter as ctk
from otp_window import OTPWindow

if __name__ == "__main__":
    root = ctk.CTk()
    app = OTPWindow(
        root,
        "123456"
    )
    root.mainloop()
