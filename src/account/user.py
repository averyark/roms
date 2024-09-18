# @fileName: user.py
# @creation_date: 14/09/2024
# @authors: averyark

import pendulum

def validateDate(date_text):
        try:
            datetime.date.fromisoformat(date_text)
        except ValueError:
            raise ValueError("Incorrect data format, should be YYYY-MM-DD")

class User:
    def __init__(self, firstName, lastName, email, birthday):
        isinstance(firstName, str)
        validateDate(birthday)

        self.firstName = firstName
        self.lastName = lastName
        self.email = email
        self.birthday = birthday

    def __str__(self):
        return f"{self.getName()}"

    def getName(self):
        return f"{self.lastName} {self.firstName}"


def __init__():
     print("loaded")
