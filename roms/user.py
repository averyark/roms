# @fileName: user.py
# @creation_date: 14/09/2024
# @authors: averyark

from icecream import ic
import pendulum
from .database import UserData, get_user_data_in_dict

userPermissionRanks = {
    'Manager': 255,
    'Chef': 100,
    'Cashier': 50,
    'Customer': 10
}

def get_user_class(userPermission: int):
    for className, classRank in userPermissionRanks.items():
        if userPermission < classRank:
            continue

        userClassName = className
        return userClassName

    if not userClassName is None:
        return

    return None

'''
    Extra User Methods
'''
class User(UserData):
    def get_role(self):
        return get_user_class(self.permission_level)

    def get_birthday_object(self):
       return pendulum.from_format(self.birthday, 'YYYY-MM-DD')

def get_user(user_id: int) -> User:
    user_data = get_user_data_in_dict(user_id)
    if not user_data:
        raise LookupError('Attempted to get user that does not exist in the database')

    return User(**user_data)
