import unittest
from unittest.mock import patch, MagicMock

import login
import otp_window
import reset_password
import ui


class LoginWindowTests(unittest.TestCase):
    def test_send_reset_otp_queries_email_with_parameter(self):
        window = login.LoginWindow.__new__(login.LoginWindow)
        window.root = MagicMock()
        window.forget_window = MagicMock()
        window.fp_username = type("Entry", (), {"get": lambda self: "admin"})()

        with patch("login.connect") as mock_connect, \
             patch("login.messagebox.showinfo") as mock_showinfo, \
             patch("login.send_otp", return_value=True) as mock_send_otp, \
             patch("login.ctk.CTkToplevel") as mock_toplevel, \
             patch("login.OTPWindow") as mock_otp_window:
            conn = mock_connect.return_value
            cursor = conn.cursor.return_value
            cursor.fetchone.return_value = ("admin@example.com",)

            window.send_reset_otp()

            cursor.execute.assert_called_once_with(
                "SELECT email FROM admins WHERE username=?",
                ("admin",),
            )
            mock_send_otp.assert_called_once_with("admin@example.com", unittest.mock.ANY)
            mock_showinfo.assert_called_once()
            self.assertEqual(window.reset_username, "admin")

    def test_send_reset_otp_warns_for_missing_account(self):
        window = login.LoginWindow.__new__(login.LoginWindow)
        window.root = MagicMock()
        window.forget_window = MagicMock()
        window.fp_username = type("Entry", (), {"get": lambda self: "missing"})()

        with patch("login.connect") as mock_connect, \
             patch("login.messagebox.showwarning") as mock_showwarning:
            conn = mock_connect.return_value
            cursor = conn.cursor.return_value
            cursor.fetchone.return_value = None

            window.send_reset_otp()

            mock_showwarning.assert_called_once()

    def test_login_hashes_password_before_query(self):
        window = login.LoginWindow.__new__(login.LoginWindow)
        window.root = MagicMock()
        window.username = type("Entry", (), {"get": lambda self: "admin"})()
        window.password = type("Entry", (), {"get": lambda self: "admin123"})()

        with patch("login.connect") as mock_connect, \
             patch("login.generate_otp", return_value="123456") as mock_generate_otp, \
             patch("login.send_otp", return_value=True) as mock_send_otp, \
             patch("login.messagebox.showinfo") as mock_showinfo, \
             patch("login.ctk.CTkToplevel") as mock_toplevel, \
             patch("login.OTPWindow") as mock_otp_window:
            conn = mock_connect.return_value
            cursor = conn.cursor.return_value
            cursor.fetchone.return_value = ("admin@example.com",)

            window.login()

            args = cursor.execute.call_args[0][1]
            self.assertEqual(args[0], "admin")
            self.assertEqual(args[1], login.hash_password("admin123"))
            mock_send_otp.assert_called_once_with("admin@example.com", "123456")
            mock_showinfo.assert_called_once()

    def test_open_dashboard_clears_widgets_and_creates_app(self):
        window = login.LoginWindow.__new__(login.LoginWindow)
        mock_widget = MagicMock()
        window.root = MagicMock()
        window.root.winfo_children.return_value = [mock_widget]

        with patch("login.App") as mock_app:
            window.open_dashboard()
            mock_widget.destroy.assert_called_once()
            mock_app.assert_called_once_with(window.root, on_logout=window.on_app_logout)

    def test_on_app_logout_reloads_login_ui(self):
        window = login.LoginWindow.__new__(login.LoginWindow)
        window.setup_ui = MagicMock()
        window.on_app_logout()
        window.setup_ui.assert_called_once()


class ResetPasswordWindowTests(unittest.TestCase):
    def test_update_password_success(self):
        window = reset_password.ResetPasswordWindow.__new__(reset_password.ResetPasswordWindow)
        window.root = MagicMock()
        window.username = "admin"
        window.on_success = MagicMock()
        window.new_password = type("Entry", (), {"get": lambda self: "newpass123"})()
        window.confirm_password = type("Entry", (), {"get": lambda self: "newpass123"})()

        with patch("reset_password.connect") as mock_connect, \
             patch("reset_password.messagebox.showinfo") as mock_showinfo:
            conn = mock_connect.return_value
            cursor = conn.cursor.return_value
            cursor.fetchone.return_value = (1,)

            window.update_password()

            cursor.execute.assert_any_call(
                "UPDATE admins SET password=? WHERE username=?",
                (login.hash_password("newpass123"), "admin")
            )
            conn.commit.assert_called_once()
            mock_showinfo.assert_called_once()
            window.on_success.assert_called_once()

    def test_update_password_mismatched(self):
        window = reset_password.ResetPasswordWindow.__new__(reset_password.ResetPasswordWindow)
        window.root = MagicMock()
        window.username = "admin"
        window.new_password = type("Entry", (), {"get": lambda self: "pass1"})()
        window.confirm_password = type("Entry", (), {"get": lambda self: "pass2"})()

        with patch("reset_password.messagebox.showerror") as mock_showerror:
            window.update_password()
            mock_showerror.assert_called_once()

    def test_update_password_empty(self):
        window = reset_password.ResetPasswordWindow.__new__(reset_password.ResetPasswordWindow)
        window.root = MagicMock()
        window.username = "admin"
        window.new_password = type("Entry", (), {"get": lambda self: ""})()
        window.confirm_password = type("Entry", (), {"get": lambda self: ""})()

        with patch("reset_password.messagebox.showwarning") as mock_showwarning:
            window.update_password()
            mock_showwarning.assert_called_once()


class OTPWindowTests(unittest.TestCase):
    def test_verify_otp_success(self):
        window = otp_window.OTPWindow.__new__(otp_window.OTPWindow)
        window.root = MagicMock()
        window.generated_otp = "123456"
        window.on_success = MagicMock()
        window.on_cancel = None
        window.otp_entry = type("Entry", (), {"get": lambda self: "123456"})()

        with patch("otp_window.messagebox.showinfo") as mock_showinfo:
            window.verify_otp()
            mock_showinfo.assert_called_once()
            window.on_success.assert_called_once()

    def test_verify_otp_invalid(self):
        window = otp_window.OTPWindow.__new__(otp_window.OTPWindow)
        window.root = MagicMock()
        window.generated_otp = "123456"
        window.on_success = MagicMock()
        window.on_cancel = None
        window.otp_entry = type("Entry", (), {"get": lambda self: "000000"})()

        with patch("otp_window.messagebox.showerror") as mock_showerror:
            window.verify_otp()
            mock_showerror.assert_called_once()
            window.on_success.assert_not_called()


class AppLogoutTests(unittest.TestCase):
    def test_perform_logout_calls_on_logout(self):
        app = ui.App.__new__(ui.App)
        app.root = MagicMock()
        app.on_logout = MagicMock()

        app.perform_logout()
        app.on_logout.assert_called_once()

    def test_show_logout_switches_frame(self):
        app = ui.App.__new__(ui.App)
        app.student_frame = MagicMock()
        app.course_frame = MagicMock()
        app.enrollment_frame = MagicMock()
        app.dashboard_frame = MagicMock()
        app.logout_frame = MagicMock()

        app.show_logout()
        app.logout_frame.pack.assert_called_once_with(fill="both", expand=True)


if __name__ == "__main__":
    unittest.main()





