# @fileName: database.py
# @creation_date: 23/09/2024
# @authors: averyark

from typing import Optional, List
from icecream import ic
import sqlite3
from pydantic import BaseModel, Field

db_path = "mock-database.db"
db = sqlite3.connect(db_path)
db_cursor = db.cursor()

class UserData(BaseModel):
    # Shared
    user_id: int

    # Stored in Credentials
    hashed_password: str

    # Stored in UserSessionTokens
    session_tokens: List[str] = Field(default_factory=list)

    # Stored in UserData
    email: str
    first_name: str
    last_name: str
    birthday: str
    permission_level: int

def get_user_data_in_dict(user_id: int):

    dict = {
        "user_id": user_id,
        "session_tokens": []
    }

    db_cursor.execute(
        f'''
            SELECT token FROM UserSessionTokens
            WHERE user_id IS {user_id}
        '''
    )

    for token in db_cursor.fetchall():
        dict["session_tokens"].append(token[0])

    db_cursor.execute(
        f'''
            SELECT password FROM Credentials
            WHERE user_id IS {user_id}
        '''
    )

    dict["hashed_password"] = db_cursor.fetchone()[0]

    db_cursor.execute(
        f'''
            SELECT
                email,
                first_name,
                last_name,
                birthday,
                permission_level
            FROM Userdata
            WHERE user_id IS {user_id}
        '''
    )
    userdata = db_cursor.fetchone()
    names = [description[0] for description in db_cursor.description]

    for index in range(0, len(names)):
        dict[names[index]] = userdata[index]

    return dict
