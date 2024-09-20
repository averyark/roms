from ..components import feedback, manageUser
from ..account.user import User

# APIS
def request_edit_user_account(self: 'User' , requestKind: str, *arg):
    if requestKind == "EditUserCredentials":
        email = arg[0]
        newPassword = arg[1]
        manageUser.editUserCredentials(email, newPassword)
    elif requestKind == "EditFirstName":
        # Do something
        pass
    elif requestKind == "EditLastName":
        # Do something
        pass
    elif requestKind == "EditEmail":
        # Do something
        pass

def request_order_details(self: 'User'):
    pass

def request_view_feedbacks(self: 'User', dish: str):

    feedback.view_dishes()
