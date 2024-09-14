# @fileName: user.py
# @creation_date: 14/09/2024
# @authors: averyark

import datetime

class User:
    def __init__(self, firstName, lastName, email, birthday):

        self.firstName = firstName
        self.lastName = lastName
        self.email = email
        self.birthday = birthday

    def __str__(self):
        return f"{self.getName()}"

    def getName(self):
        return f"{self.lastName} {self.firstName}"
    

User("Alwin", "Ting", "alwinting@gmail.com")