import re

def validate_student_inputs(name, age, email, phone, dob):
    # Name validation
    if not name or len(name.strip()) < 2:
        return False, "Name must be at least 2 characters long."
        
    # Age validation
    if not age.isdigit() or not (5 <= int(age) <= 100):
        return False, "Age must be a valid number between 5 and 100."
        
    # Email validation using Regex
    email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not re.match(email_pattern, email.strip()):
        return False, "Please enter a valid email address (e.g., user@domain.com)."
        
    # Phone validation (10 digits)
    phone_pattern = r"^\d{10}$"
    if not re.match(phone_pattern, phone.strip()):
        return False, "Phone number must be exactly 10 digits."
        
    # DOB validation (YYYY-MM-DD format)
    dob_pattern = r"^\d{4}-\d{2}-\d{2}$"
    if not re.match(dob_pattern, dob.strip()):
        return False, "DOB must be in YYYY-MM-DD format."

    return True, "Valid"