import datetime
import re

def validate_date(date_text):
    try:
        datetime.date.fromisoformat(date_text)
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD")

def validate_name(name):
    if not isinstance(name, str):
        raise TypeError("name must be a string")
    elif len(name) < 1 or len(name) > 50:
        raise ValueError("name must have 1-50 characters")
    elif re.search("^[a-zA-Z0-9 ]*", name).end() != len(name):
        raise ValueError("name must be alphabets, numbers, and space only")

def validate_email(email: str):
    matched = re.search(r"^[a-zA-Z0-9\.]+@[a-zA-Z0-9]*.com$", email)
    if not isinstance(email, str):
        raise TypeError("email must be a string")
    elif len(email) < 1 or len(email) > 50:
        raise ValueError("email must have 1-50 characters")
    elif not matched or matched.end() != len(email):
        raise ValueError("invalid email format")

def validate_password(password: str):
    matched = re.search(r"^[a-zA-Z0-9!\"#\$%\&'\(\)\*\+,\-:;<=>\?@\[\]\^_`\{\|\}~\.]*", password)

    if not isinstance(password, str):
        raise TypeError("password must be a string")
    elif len(password) < 8 or len(password) > 50:
        raise ValueError("password must have 8-50 characters")
    elif len(re.findall(r"[0-9]", password)) < 1:
        raise ValueError("password must have at least 1 number")
    elif len(re.findall(r"[a-zA-Z]", password)) < 1:
        raise ValueError("password must have at least 1 alphabet")
    elif not matched or matched.end() != len(password):
        raise ValueError("password must be alphabet, number or #~`!.@#$%^&*()_-+={[}]|:;\"'<,>?")

def validate_user_data(data: dict):
    if not dict(data):
        raise TypeError("data must be a dictionary")

    validate_password(data.password)
    validate_name(data.first_name)
    validate_name(data.last_name)
    validate_date(data.birthday)
    validate_email(data.email)
