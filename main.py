import customtkinter as ctk

from database import create_tables
from login import LoginWindow

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def main():
    create_tables()
    root = ctk.CTk()
    root.title("Student Management System")
    root.geometry("450x520")
    root.resizable(False, False)

    def on_login_success():
        """Called after OTP verification — clear login UI and launch main App."""
        for widget in root.winfo_children():
            widget.destroy()
        root.geometry("1280x750")
        root.resizable(True, True)
        from ui import App
        App(root, on_logout=lambda: restart_login(root))

    def restart_login(root):
        """Called on logout — tear down App and rebuild the login screen."""
        for widget in root.winfo_children():
            widget.destroy()
        root.geometry("450x520")
        root.resizable(False, False)
        LoginWindow(root, on_success=on_login_success)

    LoginWindow(root, on_success=on_login_success)
    root.mainloop()


if __name__ == "__main__":
    main()
