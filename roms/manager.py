import typing

if typing.TYPE_CHECKING:
    from .user import User

# APIS
def request_edit_user_account(self: 'User' , requestKind: str, *arg):
    if requestKind == "EditUserCredentials":
        # Do something
        pass
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
    pass

if __name__ == '__main__':
    pass
