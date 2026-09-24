from otp import generate_otp, send_otp

if __name__ == "__main__":
    otp = generate_otp()
    print("OTP:", otp)

    send_otp(
        "Studentadmin45@gmail.com",
        otp,
    )

    print("sent")
